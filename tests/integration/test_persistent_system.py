#!/usr/bin/env python3
"""
Script de test pour le système RAG persistant avec embedding Nomic
"""

import sys
import os
from pathlib import Path

# Ajouter le projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime

# Configuration du logging pour les tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/test_persistent_system.log')
    ]
)

logger = logging.getLogger("Test_Persistent_System")

def test_persistence_service():
    """Tester le service de persistance"""
    logger.info("🧪 Test du service de persistance")
    
    try:
        from src.services.persistence_service import PersistenceService
        
        # Initialiser le service
        persistence = PersistenceService()
        
        # Créer un projet de test
        project_id = persistence.create_project(
            name="Test Project Nomic",
            description="Projet de test pour le système persistant",
            proposal_text="Développer un système de transport autonome..."
        )
        
        logger.info(f"✅ Projet créé : {project_id}")
        
        # Récupérer le projet
        project = persistence.get_project(project_id)
        if project:
            logger.info(f"✅ Projet récupéré : {project.name}")
        else:
            logger.error("❌ Échec récupération projet")
            return False
        
        # Lister tous les projets
        projects = persistence.get_all_projects()
        logger.info(f"✅ {len(projects)} projet(s) dans la base")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test persistance : {str(e)}")
        return False

def test_nomic_embedding():
    """Tester l'embedding Nomic"""
    logger.info("🧪 Test de l'embedding Nomic")
    
    try:
        import ollama
        from config import config
        
        # Test de connexion au serveur Ollama
        client = ollama.Client(host=config.OLLAMA_BASE_URL)
        
        # Tester l'embedding avec Nomic
        test_text = "Ceci est un test d'embedding avec le modèle Nomic"
        
        response = client.embeddings(
            model=config.EMBEDDING_MODEL,
            prompt=test_text
        )
        
        embedding = response['embedding']
        logger.info(f"✅ Embedding généré : dimension {len(embedding)}")
        
        if len(embedding) > 0:
            logger.info(f"✅ Premier élément : {embedding[0]:.6f}")
            return True
        else:
            logger.error("❌ Embedding vide")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test embedding : {str(e)}")
        return False

def test_persistent_rag_system():
    """Tester le système RAG persistant complet"""
    logger.info("🧪 Test du système RAG persistant")
    
    try:
        from src.core.enhanced_persistent_rag_system import EnhancedPersistentRAGSystem
        
        # Initialiser le système
        rag_system = EnhancedPersistentRAGSystem()
        logger.info("✅ Système RAG persistant initialisé")
        
        # Créer un projet de test
        project_id = rag_system.create_project(
            name="Test RAG Nomic",
            description="Test complet du système RAG avec Nomic",
            proposal_text="""
            Développer un système de surveillance de trafic urbain basé sur l'IA.
            Le système doit pouvoir analyser les flux de circulation en temps réel,
            détecter les anomalies et proposer des solutions d'optimisation.
            
            Exigences principales:
            - Traitement temps réel des données de capteurs
            - Interface utilisateur intuitive
            - Intégration avec les systèmes existants
            - Haute disponibilité et fiabilité
            """
        )
        
        logger.info(f"✅ Projet RAG créé : {project_id}")
        
        # Tester les statistiques
        stats = rag_system.get_project_statistics()
        if not stats.get("error"):
            logger.info(f"✅ Statistiques projet : {stats['project']['name']}")
        else:
            logger.error(f"❌ Erreur statistiques : {stats['error']}")
            return False
        
        # Tester la génération de requirements persistants
        logger.info("🔄 Test génération requirements persistants...")
        
        results = rag_system.generate_persistent_requirements(
            target_phase="operational",
            requirement_types=["functional", "non_functional"],
            enable_structured_analysis=True,
            enable_cross_phase_analysis=False
        )
        
        if results.get("requirements"):
            total_reqs = sum(
                len(reqs) for phase_reqs in results["requirements"].values()
                for reqs in phase_reqs.values() if isinstance(reqs, list)
            )
            logger.info(f"✅ {total_reqs} requirements générés et sauvegardés")
        else:
            logger.error("❌ Aucun requirement généré")
            return False
        
        # Tester le chargement des requirements
        saved_reqs = rag_system.load_project_requirements()
        if saved_reqs.get("requirements"):
            logger.info("✅ Requirements rechargés depuis la base")
        else:
            logger.error("❌ Échec rechargement requirements")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test système RAG : {str(e)}")
        return False

def test_file_processing():
    """Tester le traitement de fichiers"""
    logger.info("🧪 Test du traitement de fichiers")
    
    try:
        from src.core.enhanced_persistent_rag_system import EnhancedPersistentRAGSystem
        
        # Créer un fichier de test
        test_file_path = "temp/test_document.md"
        os.makedirs("temp", exist_ok=True)
        
        test_content = """
# Document de Test MBSE

## Introduction
Ce document présente les spécifications pour un système de transport intelligent.

## Exigences Fonctionnelles
- Le système doit surveiller le trafic en temps réel
- Les données doivent être collectées via des capteurs IoT
- L'interface utilisateur doit être accessible via web

## Exigences Non-Fonctionnelles
- Disponibilité : 99.9%
- Temps de réponse < 2 secondes
- Sécurité : chiffrement bout en bout

## Architecture
Le système comprend trois couches principales :
1. Couche de collecte de données
2. Couche de traitement
3. Couche de présentation
        """
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Initialiser le système RAG
        rag_system = EnhancedPersistentRAGSystem()
        
        # Créer un projet pour le test
        project_id = rag_system.create_project(
            name="Test File Processing",
            description="Test du traitement de fichiers"
        )
        
        # Traiter le fichier
        results = rag_system.add_documents_to_project([test_file_path])
        
        if results["processed_files"]:
            logger.info(f"✅ Fichier traité : {results['new_chunks']} chunks créés")
            
            # Tester la recherche
            search_results = rag_system.query_project_documents("transport intelligent", top_k=3)
            
            if search_results.get("results"):
                logger.info(f"✅ Recherche réussie : {len(search_results['results'])} résultats")
            else:
                logger.error("❌ Aucun résultat de recherche")
                return False
        else:
            logger.error("❌ Échec traitement fichier")
            return False
        
        # Nettoyer
        try:
            os.remove(test_file_path)
        except:
            pass
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test fichiers : {str(e)}")
        return False

def test_vectorstore_performance():
    """Tester les performances du vectorstore"""
    logger.info("🧪 Test des performances vectorstore")
    
    try:
        from src.core.enhanced_persistent_rag_system import EnhancedPersistentRAGSystem
        import time
        
        rag_system = EnhancedPersistentRAGSystem()
        
        # Créer un projet de test
        project_id = rag_system.create_project(
            name="Test Performance",
            description="Test des performances"
        )
        
        # Préparer des textes de test
        test_texts = [
            "Exigence fonctionnelle de surveillance du trafic",
            "Interface utilisateur pour la gestion des données",
            "Architecture système distribuée et scalable",
            "Sécurité et authentification des utilisateurs",
            "Performance et optimisation des requêtes"
        ]
        
        # Créer des chunks de test
        chunks = []
        for i, text in enumerate(test_texts):
            chunks.append({
                "content": text,
                "metadata": {"test_chunk": i, "type": "performance_test"}
            })
        
        # Mesurer le temps d'ajout
        start_time = time.time()
        doc_id = rag_system.persistence_service.register_document("/tmp/test_perf.txt", project_id)
        rag_system.persistence_service.save_document_chunks(doc_id, project_id, chunks)
        rag_system._add_chunks_to_vectorstore(chunks, doc_id, project_id)
        add_time = time.time() - start_time
        
        logger.info(f"✅ Ajout de {len(chunks)} chunks : {add_time:.3f}s")
        
        # Mesurer le temps de recherche
        start_time = time.time()
        results = rag_system.query_project_documents("surveillance trafic", top_k=3)
        search_time = time.time() - start_time
        
        logger.info(f"✅ Recherche : {search_time:.3f}s pour {len(results.get('results', []))} résultats")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test performance : {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    logger.info("🚀 Début des tests du système RAG persistant")
    
    # Créer les répertoires nécessaires
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    tests = [
        ("Service de persistance", test_persistence_service),
        ("Embedding Nomic", test_nomic_embedding),
        ("Système RAG persistant", test_persistent_rag_system),
        ("Traitement de fichiers", test_file_processing),
        ("Performance vectorstore", test_vectorstore_performance)
    ]
    
    results = {}
    
    for test_name, test_function in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 {test_name}")
        logger.info('='*50)
        
        try:
            success = test_function()
            results[test_name] = success
            
            if success:
                logger.info(f"✅ {test_name} : SUCCÈS")
            else:
                logger.error(f"❌ {test_name} : ÉCHEC")
                
        except Exception as e:
            logger.error(f"💥 {test_name} : ERREUR - {str(e)}")
            results[test_name] = False
    
    # Résumé final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RÉSUMÉ DES TESTS")
    logger.info('='*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    for test_name, success in results.items():
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n🎯 RÉSULTAT GLOBAL : {passed_tests}/{total_tests} tests réussis")
    
    if passed_tests == total_tests:
        logger.info("🎉 Tous les tests sont passés ! Le système est prêt.")
        return True
    else:
        logger.error("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 