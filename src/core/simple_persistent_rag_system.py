import ollama
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
import logging
import hashlib

from .rag_system import SAFEMBSERAGSystem
from ..services.persistence_service import PersistenceService, Project
from config import config

class SimplePersistentRAGSystem:
    """
    Version simplifiée du système RAG persistant
    
    Fonctionnalités :
    - Persistance des projets avec SQLite
    - Utilisation de ChromaDB par défaut (sans embedding custom)
    - Gestion intelligente des doublons
    - Interface compatible avec l'UI existante
    """
    
    def __init__(self, project_id: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialiser le service de persistance
        self.persistence_service = PersistenceService()
        
        # Initialiser Ollama
        self.ollama_client = ollama.Client(host=config.OLLAMA_BASE_URL)
        
        # Initialiser ChromaDB (mode simple)
        self.chroma_client = chromadb.PersistentClient(
            path=config.VECTORDB_PATH,
            settings=Settings(allow_reset=True)
        )
        
        # Gestion du projet
        self.current_project_id = project_id
        self.current_project: Optional[Project] = None
        
        # Initialiser la collection
        self._setup_simple_collection()
        
        # Initialiser les composants de base
        from .document_processor import ArcadiaDocumentProcessor
        from .requirements_generator import RequirementsGenerator
        
        self.doc_processor = ArcadiaDocumentProcessor()
        self.req_generator = RequirementsGenerator(self.ollama_client)
        
        # Charger le projet si spécifié
        if self.current_project_id:
            self.load_project(self.current_project_id)
        
        self.logger.info("Système RAG persistant simple initialisé")
    
    def _setup_simple_collection(self):
        """Configure une collection ChromaDB simple et robuste"""
        collection_name = f"{config.COLLECTION_NAME}_simple"
        
        try:
            # Tenter de récupérer la collection existante
            self.collection = self.chroma_client.get_collection(name=collection_name)
            self.logger.info(f"Collection existante récupérée : {collection_name}")
        except Exception:
            # Créer une nouvelle collection
            try:
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": "MBSE Simple Persistent System"}
                )
                self.logger.info(f"Nouvelle collection créée : {collection_name}")
            except Exception as e:
                self.logger.error(f"Erreur création collection : {str(e)}")
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
        """Ajouter des documents à un projet"""
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
                    self.logger.info(f"Document déjà traité : {file_path}")
                    results["skipped_files"].append({
                        "file_path": file_path,
                        "reason": "already_processed",
                        "document_id": doc_id
                    })
                else:
                    # Traiter le nouveau document
                    doc_id = self.persistence_service.register_document(file_path, project_id)
                    
                    # Extraire le contenu
                    chunks = self._process_document_content(file_path)
                    
                    # Sauvegarder les chunks
                    success = self.persistence_service.save_document_chunks(doc_id, project_id, chunks)
                    
                    if success:
                        # Ajouter à ChromaDB
                        self._add_chunks_to_vectorstore_simple(chunks, doc_id, project_id)
                        
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
        return results
    
    def _process_document_content(self, file_path: str) -> List[Dict[str, Any]]:
        """Traiter le contenu d'un document"""
        try:
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
            
            # Chunking
            chunks = self.doc_processor._chunk_text_with_metadata(
                content, 
                {"source": file_path, "filename": file_path.split('/')[-1]}
            )
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Erreur traitement document {file_path} : {str(e)}")
            raise
    
    def _add_chunks_to_vectorstore_simple(self, chunks: List[Dict[str, Any]], doc_id: str, project_id: str):
        """Ajouter les chunks à ChromaDB (mode simple)"""
        try:
            texts = [chunk["content"] for chunk in chunks]
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                metadata = chunk.get("metadata", {}).copy()
                metadata.update({
                    "document_id": doc_id,
                    "project_id": project_id,
                    "chunk_index": i,
                    "embedding_model": "default"
                })
                metadatas.append(metadata)
            
            # Ajouter à ChromaDB
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Ajouté {len(chunks)} chunks à ChromaDB")
            
        except Exception as e:
            self.logger.error(f"Erreur ajout ChromaDB : {str(e)}")
            raise
    
    # ===== GÉNÉRATION DE REQUIREMENTS =====
    
    def generate_persistent_requirements(self, 
                                       proposal_text: str = "", 
                                       target_phase: str = "all",
                                       requirement_types: Optional[List[str]] = None,
                                       enable_structured_analysis: bool = False,
                                       enable_cross_phase_analysis: bool = False,
                                       project_id: Optional[str] = None) -> Dict[str, Any]:
        """Générer des requirements avec persistance"""
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        if not proposal_text and self.current_project:
            proposal_text = self.current_project.proposal_text
        
        if not proposal_text:
            raise ValueError("Aucun texte de proposition disponible")
        
        # Générer les requirements (version simplifiée)
        context_chunks = self.doc_processor._chunk_text_with_metadata(
            proposal_text, 
            {"source": "proposal", "type": "project_description"}
        )
        
        results = {
            "metadata": {
                "source": "project_proposal",
                "generation_timestamp": datetime.now().isoformat(),
                "target_phase": target_phase,
                "requirement_types": requirement_types or ["functional", "non_functional"]
            },
            "requirements": {},
            "statistics": {}
        }
        
        # Génération simple par phase
        phases_to_process = [target_phase] if target_phase != "all" else ["operational", "system"]
        
        for phase in phases_to_process:
            results["requirements"][phase] = {}
            
            if "functional" in (requirement_types or []):
                functional_reqs = self.req_generator.generate_functional_requirements(
                    context_chunks, phase, proposal_text
                )
                results["requirements"][phase]["functional"] = functional_reqs
            
            if "non_functional" in (requirement_types or []):
                nf_reqs = self.req_generator.generate_non_functional_requirements(
                    context_chunks, phase, proposal_text
                )
                results["requirements"][phase]["non_functional"] = nf_reqs
        
        # Statistiques
        total_reqs = sum(
            len(reqs) for phase_reqs in results["requirements"].values()
            for reqs in phase_reqs.values() if isinstance(reqs, list)
        )
        
        results["statistics"] = {
            "total_requirements": total_reqs,
            "by_phase": {
                phase: sum(len(reqs) for reqs in phase_reqs.values() if isinstance(reqs, list))
                for phase, phase_reqs in results["requirements"].items()
            }
        }
        
        # Sauvegarder
        if results.get("requirements"):
            success = self.persistence_service.save_project_requirements(project_id, results)
            results["persistence_status"] = "saved" if success else "failed"
        
        # Ajouter les informations du projet
        results["project_info"] = {
            "project_id": project_id,
            "project_name": self.current_project.name if self.current_project else "Unknown"
        }
        
        return results
    
    def load_project_requirements(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Charger les requirements d'un projet"""
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        return self.persistence_service.get_project_requirements(project_id)
    
    # ===== RECHERCHE =====
    
    def query_project_documents(self, query: str, top_k: int = 5, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Rechercher dans les documents d'un projet"""
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"project_id": project_id}
            )
            
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
            self.logger.error(f"Erreur recherche : {str(e)}")
            return {"query": query, "project_id": project_id, "total_results": 0, "results": [], "error": str(e)}
    
    # ===== STATISTIQUES =====
    
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
            try:
                vectorstore_stats = self.collection.count()
            except:
                vectorstore_stats = 0
            
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
                    "embedding_model": "default"
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
            self.logger.error(f"Erreur statistiques : {str(e)}")
            return {"error": str(e)}
    
    # ===== MAINTENANCE =====
    
    def cleanup_project_vectors(self, project_id: Optional[str] = None):
        """Nettoyer les vecteurs d'un projet"""
        if not project_id:
            project_id = self.current_project_id
            
        if not project_id:
            raise ValueError("Aucun projet spécifié ou chargé")
        
        try:
            results = self.collection.get(where={"project_id": project_id})
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                self.logger.info(f"Supprimé {len(results['ids'])} vecteurs pour le projet {project_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur nettoyage : {str(e)}")
            raise
    
    # ===== COMPATIBILITÉ =====
    
    def export_requirements(self, requirements: Dict[str, Any], export_format: str) -> str:
        """Méthode de compatibilité pour l'export"""
        if export_format == "JSON":
            return json.dumps(requirements, indent=2, ensure_ascii=False)
        else:
            # Utiliser le système de base pour les autres formats
            base_system = SAFEMBSERAGSystem()
            return base_system.export_requirements(requirements, export_format) 