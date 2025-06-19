import ollama
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Tuple, Optional, Any
import json
import numpy as np
from datetime import datetime
import logging
import hashlib

from .rag_system import SAFEMBSERAGSystem
from .enhanced_structured_rag_system import EnhancedStructuredRAGSystem
from ..services.persistence_service import PersistenceService, Project, ProcessedDocument
from config import config

class EnhancedPersistentRAGSystem(EnhancedStructuredRAGSystem):
    """
    Système RAG persistant utilisant l'embedding Nomic et la gestion de projets
    
    Fonctionnalités :
    - Embedding avec le modèle Nomic-embed-text du serveur Ollama
    - Persistance complète des projets, documents et chunks
    - Optimisation : évite le retraitement des documents déjà traités
    - Gestion de sessions utilisateur
    """
    
    def __init__(self, project_id: Optional[str] = None):
        # Initialiser le service de persistance en premier
        self.persistence_service = PersistenceService()
        
        # Initialiser le client Ollama pour l'embedding
        self.ollama_client = ollama.Client(host=config.OLLAMA_BASE_URL)
        
        # Configuration ChromaDB avec embeddings custom
        self.chroma_client = chromadb.PersistentClient(
            path=config.VECTORDB_PATH,
            settings=Settings(allow_reset=True)
        )
        
        # Project management
        self.current_project_id = project_id
        self.current_project: Optional[Project] = None
        
        # Initialiser le logger
        self.logger = logging.getLogger(__name__)
        
        # Créer/récupérer la collection avec embedding function custom
        self._setup_collection()
        
        # Initialiser les autres composants depuis la classe parent
        # Nous ne pouvons pas appeler super().__init__() car nous avons modifié l'initialisation
        from .document_processor import ArcadiaDocumentProcessor
        from .requirements_generator import RequirementsGenerator
        from ..utils.enhanced_requirement_extractor import EnhancedRequirementExtractor
        from .structured_arcadia_service import StructuredARCADIAService
        
        self.doc_processor = ArcadiaDocumentProcessor()
        self.req_generator = RequirementsGenerator(self.ollama_client)
        self.enhanced_extractor = EnhancedRequirementExtractor()
        self.structured_service = StructuredARCADIAService(self.ollama_client)
        
        # Charger le projet actuel si spécifié
        if self.current_project_id:
            self.load_project(self.current_project_id)
        
        self.logger.info("Système RAG persistant initialisé avec embedding Nomic")
    
    def _setup_collection(self):
        """Configure la collection ChromaDB avec l'embedding function Nomic"""
        
        # Créer une fonction d'embedding custom utilisant Nomic
        class NomicEmbeddingFunction:
            def __init__(self, ollama_client):
                self.ollama_client = ollama_client
                self.model = config.EMBEDDING_MODEL
                
            def __call__(self, input: list[str]) -> list[list[float]]:
                """Génère des embeddings avec le modèle Nomic - Interface ChromaDB v0.4.16+"""
                embeddings = []
                for text in input:
                    try:
                        response = self.ollama_client.embeddings(
                            model=self.model,
                            prompt=text
                        )
                        embeddings.append(response['embedding'])
                    except Exception as e:
                        logging.error(f"Erreur embedding pour le texte : {str(e)}")
                        # Fallback: vecteur zéro
                        embeddings.append([0.0] * 768)  # Dimension typique pour Nomic
                return embeddings
        
        self.embedding_function = NomicEmbeddingFunction(self.ollama_client)
        
        # Créer ou récupérer la collection avec gestion des conflits
        collection_name = f"{config.COLLECTION_NAME}_persistent"
        
        try:
            # Tenter de récupérer la collection existante
            self.collection = self.chroma_client.get_collection(
                name=collection_name
            )
            self.logger.info(f"Collection existante récupérée : {collection_name}")
            
            # Mettre à jour la fonction d'embedding si nécessaire
            try:
                # Tester si la collection fonctionne avec notre embedding function
                test_result = self.collection.query(
                    query_texts=["test"],
                    n_results=1
                )
                self.logger.info("Collection existante compatible")
            except Exception:
                self.logger.warning("Collection existante incompatible, recréation...")
                self.chroma_client.delete_collection(name=collection_name)
                raise Exception("Force recreation")
                
        except Exception:
            # Créer une nouvelle collection
            try:
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"description": "MBSE Persistent System with Nomic Embeddings"}
                )
                self.logger.info(f"Nouvelle collection créée : {collection_name}")
            except Exception as e:
                self.logger.error(f"Erreur création collection : {str(e)}")
                # Fallback: utiliser collection sans embedding function custom
                try:
                    # Supprimer toute collection conflictuelle
                    try:
                        self.chroma_client.delete_collection(name=collection_name)
                    except:
                        pass
                    
                    # Créer collection simple
                    self.collection = self.chroma_client.create_collection(
                        name=collection_name,
                        metadata={"description": "MBSE Persistent System - Fallback Mode"}
                    )
                    self.logger.warning(f"Collection créée en mode fallback : {collection_name}")
                    self.embedding_function = None  # Utiliser embeddings par défaut
                except Exception as final_error:
                    self.logger.error(f"Échec complet création collection : {str(final_error)}")
                    raise
    
    # ===== GESTION DES PROJETS =====
    
    def create_project(self, name: str, description: str = "", proposal_text: str = "") -> str:
        """Créer un nouveau projet"""
        project_id = self.persistence_service.create_project(name, description, proposal_text)
        self.current_project_id = project_id
        self.load_project(project_id)
        return project_id
    
    def load_project(self, project_id: str) -> bool:
        """Charger un projet existant"""
        project = self.persistence_service.get_project(project_id)
        if project:
            self.current_project_id = project_id
            self.current_project = project
            self.logger.info(f"Projet chargé : {project.name} ({project_id})")
            return True
        else:
            self.logger.error(f"Projet non trouvé : {project_id}")
            return False
    
    def get_all_projects(self) -> List[Project]:
        """Récupérer tous les projets"""
        return self.persistence_service.get_all_projects()
    
    def get_current_project(self) -> Optional[Project]:
        """Récupérer le projet actuel"""
        return self.current_project
    
    # ===== GESTION DES DOCUMENTS =====
    
    def add_documents_to_project(self, file_paths: List[str], project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ajouter des documents à un projet avec gestion intelligente de la persistence
        
        Args:
            file_paths: Liste des chemins des fichiers à traiter
            project_id: ID du projet (utilise le projet actuel si None)
            
        Returns:
            Résultats du traitement avec statistiques
        """
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        results = {
            "project_id": project_id,
            "processed_files": [],
            "skipped_files": [],
            "new_chunks": 0,
            "total_chunks": 0,
            "processing_time": 0,
            "errors": []
        }
        
        start_time = datetime.now()
        
        for file_path in file_paths:
            try:
                self.logger.info(f"Traitement du fichier : {file_path}")
                
                # Vérifier si le document a déjà été traité
                is_processed, doc_id = self.persistence_service.is_document_processed(file_path, project_id)
                
                if is_processed:
                    self.logger.info(f"Document déjà traité, récupération des chunks : {file_path}")
                    results["skipped_files"].append({
                        "file_path": file_path,
                        "reason": "already_processed",
                        "document_id": doc_id
                    })
                    
                    # Récupérer les chunks existants pour les statistiques
                    existing_chunks = self._get_document_chunks_from_db(doc_id)
                    results["total_chunks"] += len(existing_chunks)
                    
                else:
                    # Traiter le nouveau document
                    self.logger.info(f"Nouveau document, traitement en cours : {file_path}")
                    
                    # Enregistrer le document
                    doc_id = self.persistence_service.register_document(file_path, project_id)
                    
                    # Extraire et traiter le contenu
                    chunks = self._process_document_content(file_path)
                    
                    # Sauvegarder les chunks dans la base
                    success = self.persistence_service.save_document_chunks(doc_id, project_id, chunks)
                    
                    if success:
                        # Ajouter les chunks à ChromaDB avec embeddings Nomic
                        self._add_chunks_to_vectorstore(chunks, doc_id, project_id)
                        
                        results["processed_files"].append({
                            "file_path": file_path,
                            "document_id": doc_id,
                            "chunks_count": len(chunks)
                        })
                        
                        results["new_chunks"] += len(chunks)
                        results["total_chunks"] += len(chunks)
                        
                        self.logger.info(f"Document traité avec succès : {len(chunks)} chunks")
                    else:
                        results["errors"].append(f"Erreur sauvegarde chunks : {file_path}")
                        
            except Exception as e:
                error_msg = f"Erreur traitement {file_path} : {str(e)}"
                self.logger.error(error_msg)
                results["errors"].append(error_msg)
        
        results["processing_time"] = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"Traitement terminé : {len(results['processed_files'])} nouveaux, "
                        f"{len(results['skipped_files'])} ignorés, "
                        f"{results['new_chunks']} nouveaux chunks")
        
        return results
    
    def _process_document_content(self, file_path: str) -> List[Dict[str, Any]]:
        """Traiter le contenu d'un document et créer les chunks"""
        try:
            # Extraction du contenu selon le type de fichier
            content = ""
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension in ['txt', 'md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            elif file_extension == 'pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        content = ""
                        for page in pdf_reader.pages:
                            content += page.extract_text() + "\n"
                except ImportError:
                    self.logger.error("PyPDF2 non installé pour traiter les PDF")
                    raise
            
            else:
                raise ValueError(f"Type de fichier non supporté : {file_extension}")
            
            # Chunking du contenu
            chunks = self.doc_processor._chunk_text_with_metadata(
                content, 
                {"source": file_path, "filename": file_path.split('/')[-1]}
            )
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du document {file_path} : {str(e)}")
            raise
    
    def _add_chunks_to_vectorstore(self, chunks: List[Dict[str, Any]], doc_id: str, project_id: str):
        """Ajouter les chunks à ChromaDB avec embeddings Nomic"""
        try:
            # Préparer les données pour ChromaDB
            texts = [chunk["content"] for chunk in chunks]
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                metadata = chunk.get("metadata", {}).copy()
                metadata.update({
                    "document_id": doc_id,
                    "project_id": project_id,
                    "chunk_index": i,
                    "embedding_model": "nomic-embed-text" if self.embedding_function else "default"
                })
                metadatas.append(metadata)
            
            # Ajouter à ChromaDB (les embeddings seront générés automatiquement)
            if self.embedding_function:
                # Mode Nomic avec embedding function custom
                self.collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                self.logger.info(f"Ajouté {len(chunks)} chunks à ChromaDB avec embeddings Nomic")
            else:
                # Mode fallback avec embeddings par défaut de ChromaDB
                self.collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                self.logger.info(f"Ajouté {len(chunks)} chunks à ChromaDB avec embeddings par défaut")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout à ChromaDB : {str(e)}")
            raise
    
    def _get_document_chunks_from_db(self, doc_id: str) -> List[Dict[str, Any]]:
        """Récupérer les chunks d'un document depuis la base de données"""
        try:
            # Cette méthode sera utilisée pour récupérer les chunks existants
            # Pour l'instant, on retourne une liste vide
            return []
        except Exception as e:
            self.logger.error(f"Erreur récupération chunks : {str(e)}")
            return []
    
    # ===== GÉNÉRATION DE REQUIREMENTS PERSISTANTS =====
    
    def generate_persistent_requirements(self, 
                                       proposal_text: str = "", 
                                       target_phase: str = "all",
                                       requirement_types: Optional[List[str]] = None,
                                       enable_structured_analysis: bool = True,
                                       enable_cross_phase_analysis: bool = True,
                                       project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Générer des requirements avec persistance automatique
        
        Args:
            proposal_text: Texte de proposition (utilise celui du projet si vide)
            target_phase: Phase ARCADIA ciblée
            requirement_types: Types de requirements à générer
            enable_structured_analysis: Activer l'analyse structurée
            enable_cross_phase_analysis: Activer l'analyse inter-phases
            project_id: ID du projet (utilise le projet actuel si None)
            
        Returns:
            Résultats avec persistence automatique
        """
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        # Utiliser le texte de proposition du projet si pas fourni
        if not proposal_text and self.current_project:
            proposal_text = self.current_project.proposal_text
        
        if not proposal_text:
            raise ValueError("Aucun texte de proposition disponible")
        
        # Générer les requirements avec la méthode héritée
        results = self.generate_enhanced_requirements_from_proposal(
            proposal_text=proposal_text,
            target_phase=target_phase,
            requirement_types=requirement_types,
            enable_structured_analysis=enable_structured_analysis,
            enable_cross_phase_analysis=enable_cross_phase_analysis
        )
        
        # Sauvegarder les requirements dans la base
        if results.get("requirements"):
            success = self.persistence_service.save_project_requirements(project_id, results)
            if success:
                results["persistence_status"] = "saved"
                self.logger.info(f"Requirements sauvegardés pour le projet {project_id}")
            else:
                results["persistence_status"] = "failed"
                self.logger.error(f"Échec sauvegarde requirements pour le projet {project_id}")
        
        # Ajouter les informations du projet
        results["project_info"] = {
            "project_id": project_id,
            "project_name": self.current_project.name if self.current_project else "Unknown"
        }
        
        return results
    
    def load_project_requirements(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Charger les requirements sauvegardés d'un projet"""
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        return self.persistence_service.get_project_requirements(project_id)
    
    # ===== RECHERCHE DANS LE PROJET =====
    
    def query_project_documents(self, query: str, top_k: int = 5, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Rechercher dans les documents d'un projet spécifique
        
        Args:
            query: Requête de recherche
            top_k: Nombre de résultats à retourner
            project_id: ID du projet (utilise le projet actuel si None)
            
        Returns:
            Résultats de recherche filtrés par projet
        """
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        try:
            # Recherche avec filtre par projet
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"project_id": project_id}
            )
            
            # Formater les résultats
            formatted_results = {
                "query": query,
                "project_id": project_id,
                "total_results": len(results["documents"][0]) if results["documents"] else 0,
                "results": []
            }
            
            if results["documents"]:
                for i in range(len(results["documents"][0])):
                    formatted_results["results"].append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0,
                        "id": results["ids"][0][i] if results["ids"] else ""
                    })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche : {str(e)}")
            return {"query": query, "project_id": project_id, "total_results": 0, "results": [], "error": str(e)}
    
    # ===== STATISTIQUES ET MAINTENANCE =====
    
    def get_project_statistics(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtenir les statistiques d'un projet"""
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        try:
            project = self.persistence_service.get_project(project_id)
            if not project:
                return {"error": "Projet non trouvé"}
            
            documents = self.persistence_service.get_project_documents(project_id)
            requirements = self.persistence_service.get_project_requirements(project_id)
            chunks = self.persistence_service.get_project_chunks(project_id)
            
            # Statistiques vectorstore
            vectorstore_stats = self.collection.count()
            
            return {
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat()
                },
                "documents": {
                    "total": len(documents),
                    "by_status": {
                        "completed": len([d for d in documents if d.processing_status == "completed"]),
                        "processing": len([d for d in documents if d.processing_status == "processing"]),
                        "failed": len([d for d in documents if d.processing_status == "failed"])
                    },
                    "total_size": sum(d.file_size for d in documents),
                    "embedding_model": "nomic-embed-text"
                },
                "chunks": {
                    "total": len(chunks),
                    "vectorstore_count": vectorstore_stats
                },
                "requirements": {
                    "total": sum(len(reqs) for phase_reqs in requirements.get("requirements", {}).values() 
                               for reqs in phase_reqs.values() if isinstance(reqs, list)),
                    "by_phase": {
                        phase: sum(len(reqs) for reqs in phase_reqs.values() if isinstance(reqs, list))
                        for phase, phase_reqs in requirements.get("requirements", {}).items()
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erreur calcul statistiques : {str(e)}")
            return {"error": str(e)}
    
    def cleanup_project_vectors(self, project_id: Optional[str] = None):
        """Nettoyer les vecteurs d'un projet du vectorstore"""
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        try:
            # Récupérer tous les IDs de chunks pour ce projet
            results = self.collection.get(where={"project_id": project_id})
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                self.logger.info(f"Supprimé {len(results['ids'])} vecteurs pour le projet {project_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur nettoyage vecteurs : {str(e)}")
            raise 