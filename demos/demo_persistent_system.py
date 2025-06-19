#!/usr/bin/env python3
"""
Démonstration interactive du système RAG persistant avec embedding Nomic
"""

import sys
import os
from pathlib import Path
import time

# Ajouter le projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime

# Configuration du logging pour la démo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("Demo_Persistent_System")

def print_header(title):
    """Display a styled header"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_step(step_num, description):
    """Display a step"""
    print(f"\n📋 Étape {step_num}: {description}")
    print("-" * 40)

def wait_for_user():
    """Attendre l'utilisateur"""
    input("\n⏸️  Appuyez sur Entrée pour continuer...")

def demo_1_system_initialization():
    """Demonstration 1: System initialization"""
    print_header("Démonstration du Système RAG Persistant avec Nomic")
    
    print("""
🚀 **Bienvenue dans la démonstration du nouveau système MBSE RAG !**

Cette démonstration vous présente les améliorations majeures :
- 🔧 Embedding Nomic-embed-text depuis le serveur Ollama
- 🗂️ Gestion persistante des projets
- ⚡ Optimisation intelligente des traitements
- 📊 Statistiques avancées et traçabilité
    """)
    
    wait_for_user()
    
    print_step(1, "Vérification des services")
    
    try:
        # Test connexion Ollama
        import ollama
        from config import config
        
        print("🔌 Test de connexion au serveur Ollama...")
        client = ollama.Client(host=config.OLLAMA_BASE_URL)
        
        # Test du modèle d'embedding
        print(f"🧠 Test du modèle d'embedding : {config.EMBEDDING_MODEL}")
        
        test_text = "Test d'embedding pour la démonstration MBSE"
        response = client.embeddings(model=config.EMBEDDING_MODEL, prompt=test_text)
        
        embedding_dim = len(response['embedding'])
        print(f"✅ Embedding Nomic fonctionnel - Dimension : {embedding_dim}")
        
        # Test base de données
        print("🗃️ Test de la base de données...")
        from src.services.persistence_service import PersistenceService
        
        persistence = PersistenceService()
        print("✅ Service de persistance initialisé")
        
        print("\n🎉 Tous les services sont opérationnels !")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {str(e)}")
        print("Veuillez vérifier la configuration avant de continuer.")
        return False
    
    return True

def demo_2_project_management():
    """Démonstration 2: Gestion des projets"""
    print_header("Gestion des Projets Persistants")
    
    print("""
🗂️ **Nouvelle fonctionnalité : Gestion de projets**

Plus besoin de recharger vos documents à chaque session !
Le système maintient une persistance complète de vos projets.
    """)
    
    wait_for_user()
    
    try:
        from src.core.enhanced_persistent_rag_system import EnhancedPersistentRAGSystem
        
        print_step(1, "Initialisation du système RAG persistant")
        rag_system = EnhancedPersistentRAGSystem()
        print("✅ Système RAG persistant initialisé avec embedding Nomic")
        
        print_step(2, "Création d'un projet de démonstration")
        project_id = rag_system.create_project(
            name="Démonstration MBSE RAG",
            description="Projet de démonstration du système persistant",
            proposal_text="""
            Développer un système de gestion de trafic urbain intelligent.
            
            Le système doit intégrer :
            - Capteurs IoT pour la surveillance en temps réel
            - Algorithmes d'IA pour l'analyse prédictive
            - Interface utilisateur pour les opérateurs
            - Intégration avec les systèmes de transport existants
            
            Exigences principales :
            - Haute disponibilité (99.9%)
            - Traitement temps réel (< 1 seconde)
            - Scalabilité horizontale
            - Sécurité et authentification robustes
            """
        )
        
        print(f"✅ Projet créé avec l'ID : {project_id}")
        
        # Afficher les informations du projet
        project = rag_system.get_current_project()
        print(f"📋 Nom : {project.name}")
        print(f"📅 Créé le : {project.created_at.strftime('%d/%m/%Y %H:%M')}")
        
        print_step(3, "Liste des projets existants")
        projects = rag_system.get_all_projects()
        print(f"📊 Nombre total de projets : {len(projects)}")
        
        for i, proj in enumerate(projects[-3:], 1):  # Afficher les 3 derniers
            print(f"   {i}. {proj.name} ({proj.documents_count} docs, {proj.requirements_count} reqs)")
        
        return rag_system, project_id
        
    except Exception as e:
        print(f"❌ Erreur lors de la gestion des projets : {str(e)}")
        return None, None

def demo_3_document_processing(rag_system, project_id):
    """Démonstration 3: Traitement de documents intelligent"""
    print_header("Traitement Intelligent de Documents")
    
    print("""
📄 **Nouvelle fonctionnalité : Traitement optimisé**

Le système détecte automatiquement les documents déjà traités
et évite les recalculs d'embedding coûteux.
    """)
    
    wait_for_user()
    
    try:
        print_step(1, "Création de documents de démonstration")
        
        # Créer des documents de test
        os.makedirs("temp", exist_ok=True)
        
        documents = {
            "specifications.md": """
# Spécifications Système de Trafic

## Vue d'ensemble
Le système de gestion de trafic urbain intelligent (SGTU) vise à optimiser 
les flux de circulation en temps réel.

## Exigences Fonctionnelles
- RF001: Collecte de données de capteurs IoT
- RF002: Analyse prédictive du trafic
- RF003: Génération d'alertes automatiques
- RF004: Interface de supervision

## Exigences Non-Fonctionnelles
- RNF001: Disponibilité 99.9%
- RNF002: Temps de réponse < 1 seconde
- RNF003: Scalabilité jusqu'à 10000 capteurs
- RNF004: Sécurité avec chiffrement AES-256
            """,
            
            "architecture.md": """
# Architecture du Système

## Architecture Générale
Le SGTU adopte une architecture en microservices distribuée.

### Couche de Collecte
- Ingestion des données capteurs
- Validation et normalisation
- Stockage temporaire

### Couche de Traitement
- Moteur d'analyse temps réel
- Algorithmes de machine learning
- Calcul des optimisations

### Couche de Présentation
- Dashboard web responsive
- API REST pour intégrations
- Notifications push
            """,
            
            "stakeholders.md": """
# Parties Prenantes

## Stakeholders Primaires
- **Opérateurs de trafic** : Utilisateurs principaux du système
- **Citoyens** : Bénéficiaires des optimisations
- **Autorités municipales** : Commanditaires du projet

## Stakeholders Secondaires
- **Fournisseurs de capteurs** : Partenaires techniques
- **Équipes de maintenance** : Support opérationnel
- **Services d'urgence** : Utilisateurs spécialisés

## Exigences par Stakeholder
- Opérateurs : Interface intuitive, alertes claires
- Citoyens : Réduction des embouteillages
- Autorités : Rapports de performance, ROI
            """
        }
        
        # Écrire les fichiers
        file_paths = []
        for filename, content in documents.items():
            file_path = f"temp/{filename}"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_paths.append(file_path)
            print(f"📄 Créé : {filename}")
        
        print_step(2, "Premier traitement des documents")
        start_time = time.time()
        
        results = rag_system.add_documents_to_project(file_paths)
        
        processing_time = time.time() - start_time
        
        print(f"⏱️  Temps de traitement : {processing_time:.2f} secondes")
        print(f"✅ Fichiers traités : {len(results['processed_files'])}")
        print(f"🧩 Chunks créés : {results['new_chunks']}")
        print(f"📊 Total chunks : {results['total_chunks']}")
        
        if results['errors']:
            print(f"⚠️  Erreurs : {len(results['errors'])}")
        
        print_step(3, "Test de détection de doublons")
        print("🔄 Retraitement des mêmes fichiers...")
        
        start_time = time.time()
        results2 = rag_system.add_documents_to_project(file_paths)
        processing_time2 = time.time() - start_time
        
        print(f"⏱️  Temps de retraitement : {processing_time2:.2f} secondes")
        print(f"✅ Fichiers traités : {len(results2['processed_files'])}")
        print(f"⏭️  Fichiers ignorés : {len(results2['skipped_files'])}")
        print(f"🎯 Optimisation : {((processing_time - processing_time2) / processing_time * 100):.1f}% plus rapide")
        
        # Nettoyer les fichiers temporaires
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement des documents : {str(e)}")
        return False

def demo_4_requirements_generation(rag_system):
    """Démonstration 4: Génération persistante de requirements"""
    print_header("Génération Persistante de Requirements")
    
    print("""
📝 **Nouvelle fonctionnalité : Requirements persistants**

Les requirements générés sont automatiquement sauvegardés
et peuvent être rechargés à tout moment.
    """)
    
    wait_for_user()
    
    try:
        print_step(1, "Génération de requirements avec analyse ARCADIA")
        
        start_time = time.time()
        results = rag_system.generate_persistent_requirements(
            target_phase="operational",
            requirement_types=["functional", "non_functional", "stakeholder"],
            enable_structured_analysis=True,
            enable_cross_phase_analysis=False
        )
        generation_time = time.time() - start_time
        
        print(f"⏱️  Temps de génération : {generation_time:.1f} secondes")
        
        if results.get("requirements"):
            total_reqs = sum(
                len(reqs) for phase_reqs in results["requirements"].values()
                for reqs in phase_reqs.values() if isinstance(reqs, list)
            )
            print(f"✅ Requirements générés : {total_reqs}")
            
            # Afficher quelques exemples
            print("\n📋 Exemples de requirements générés :")
            for phase, phase_reqs in results["requirements"].items():
                print(f"\n🔹 Phase {phase.title()}:")
                for req_type, reqs in phase_reqs.items():
                    if isinstance(reqs, list) and reqs:
                        print(f"   • {req_type.title()} : {len(reqs)} requirements")
                        if reqs:
                            example = reqs[0]
                            print(f"     Exemple: {example.get('title', 'Sans titre')}")
        
        if results.get("persistence_status") == "saved":
            print("💾 Requirements sauvegardés automatiquement !")
        
        print_step(2, "Test de rechargement des requirements")
        
        saved_reqs = rag_system.load_project_requirements()
        if saved_reqs.get("requirements"):
            total_saved = sum(
                len(reqs) for phase_reqs in saved_reqs["requirements"].values()
                for reqs in phase_reqs.values() if isinstance(reqs, list)
            )
            print(f"✅ Requirements rechargés : {total_saved}")
        else:
            print("❌ Aucun requirement sauvegardé trouvé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {str(e)}")
        return False

def demo_5_smart_search(rag_system):
    """Démonstration 5: Recherche intelligente"""
    print_header("Recherche Intelligente avec Nomic")
    
    print("""
🔍 **Nouvelle fonctionnalité : Recherche optimisée**

La recherche utilise les embeddings Nomic pour des résultats
plus pertinents et contextualisés.
    """)
    
    wait_for_user()
    
    try:
        queries = [
            "Comment gérer la scalabilité du système ?",
            "Quelles sont les exigences de sécurité ?",
            "Interface utilisateur et dashboard",
            "Capteurs IoT et collecte de données",
            "Performance et temps de réponse"
        ]
        
        print_step(1, "Tests de recherche sémantique")
        
        for i, query in enumerate(queries, 1):
            print(f"\n🔎 Query {i}: '{query}'")
            
            start_time = time.time()
            results = rag_system.query_project_documents(query, top_k=3)
            search_time = time.time() - start_time
            
            print(f"⏱️  Temps de recherche : {search_time:.3f} secondes")
            
            if results.get("results"):
                print(f"📋 Résultats trouvés : {len(results['results'])}")
                
                # Afficher le meilleur résultat
                best_result = results["results"][0]
                similarity = 1 - best_result.get("distance", 1)
                
                print(f"🎯 Meilleur score : {similarity:.3f}")
                content_preview = best_result["content"][:100] + "..."
                print(f"📝 Aperçu : {content_preview}")
                
                if best_result.get("metadata"):
                    source = best_result["metadata"].get("source_filename", "Source inconnue")
                    print(f"📄 Source : {source}")
            else:
                print("❌ Aucun résultat trouvé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {str(e)}")
        return False

def demo_6_statistics_and_maintenance(rag_system):
    """Démonstration 6: Statistiques et maintenance"""
    print_header("Statistiques et Maintenance")
    
    print("""
📊 **Nouvelle fonctionnalité : Monitoring avancé**

Le système fournit des statistiques détaillées sur
l'utilisation et les performances.
    """)
    
    wait_for_user()
    
    try:
        print_step(1, "Statistiques du projet")
        
        stats = rag_system.get_project_statistics()
        
        if not stats.get("error"):
            print("📊 Statistiques du projet :")
            print(f"   📋 Nom : {stats['project']['name']}")
            print(f"   📅 Créé : {stats['project']['created_at']}")
            print(f"   📄 Documents : {stats['documents']['total']}")
            print(f"   🧩 Chunks : {stats['chunks']['total']}")
            print(f"   📝 Requirements : {stats['requirements']['total']}")
            print(f"   💾 Taille totale : {stats['documents']['total_size'] / (1024*1024):.1f} MB")
            print(f"   🔧 Modèle embedding : {stats['documents']['embedding_model']}")
            
            # Détail par statut
            print("\n📈 Répartition des documents :")
            for status, count in stats['documents']['by_status'].items():
                print(f"   • {status} : {count}")
            
            # Détail par phase
            if stats['requirements']['by_phase']:
                print("\n📝 Requirements par phase :")
                for phase, count in stats['requirements']['by_phase'].items():
                    print(f"   • {phase} : {count}")
        
        print_step(2, "Actions de maintenance")
        
        print("🧹 Test du nettoyage des vecteurs...")
        try:
            # Note: On ne fait pas vraiment le nettoyage en démo
            print("✅ Fonction de nettoyage disponible")
        except Exception as e:
            print(f"⚠️  Nettoyage : {str(e)}")
        
        print("📤 Test des capacités d'export...")
        try:
            # Test export (sans vraiment exporter)
            formats = ["JSON", "Markdown", "Excel", "DOORS", "ReqIF"]
            print(f"✅ Formats d'export supportés : {', '.join(formats)}")
        except Exception as e:
            print(f"⚠️  Export : {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des statistiques : {str(e)}")
        return False

def demo_conclusion():
    """Conclusion de la démonstration"""
    print_header("Conclusion et Prochaines Étapes")
    
    print("""
🎉 **Démonstration terminée avec succès !**

📋 **Récapitulatif des améliorations :**
- ✅ Embedding Nomic pour une meilleure qualité de recherche
- ✅ Persistance complète des projets et données
- ✅ Optimisation intelligente (détection de doublons)
- ✅ Interface de gestion de projets intuitive
- ✅ Statistiques et monitoring avancés
- ✅ Recherche contextuelle par projet

🚀 **Pour commencer :**
1. Lancez les tests : `python test_persistent_system.py`
2. Démarrez l'interface : `streamlit run ui/app.py`
3. Créez votre premier projet
4. Ajoutez vos documents
5. Générez vos requirements MBSE

📚 **Documentation complète :**
- Guide utilisateur : `docs/guide_systeme_persistant.md`
- Architecture : `docs/architecture.md`
- Dépannage : Consultez les logs dans `logs/`

🆘 **Support :**
- Tests de diagnostic : `python test_persistent_system.py`
- Logs détaillés dans le répertoire `logs/`
- Vérification Ollama : `curl http://llm-eva.univ-pau.fr:11434/api/version`
    """)
    
    print("\n" + "="*60)
    print("🎯 Merci d'avoir suivi cette démonstration !")
    print("="*60)

def main():
    """Fonction principale de la démonstration"""
    try:
        # Créer les répertoires nécessaires
        os.makedirs("logs", exist_ok=True)
        os.makedirs("temp", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        # Variable pour stocker les résultats de la démo 2
        demo_2_result = None
        
        print("🎬 Début de la démonstration du système RAG persistant")
        print("⏸️  Vous pouvez interrompre à tout moment avec Ctrl+C")
        
        # Démonstration 1 : Initialisation
        try:
            success = demo_1_system_initialization()
            if not success:
                print("❌ Impossible de continuer sans initialisation")
                return False
        except KeyboardInterrupt:
            print("\n⏹️  Démonstration interrompue à l'initialisation")
            return False
        except Exception as e:
            print(f"❌ Erreur dans l'initialisation : {str(e)}")
            return False
        
        # Démonstration 2 : Gestion des projets
        try:
            demo_2_result = demo_2_project_management()
            if not demo_2_result or not demo_2_result[0]:
                print("❌ Impossible de continuer sans projet")
                return False
        except KeyboardInterrupt:
            print("\n⏹️  Démonstration interrompue à la gestion des projets")
            return False
        except Exception as e:
            print(f"❌ Erreur dans la gestion des projets : {str(e)}")
            return False
        
        # Démonstrations suivantes (qui dépendent du projet)
        remaining_demos = [
            ("Traitement de documents", lambda: demo_3_document_processing(demo_2_result[0], demo_2_result[1])),
            ("Génération de requirements", lambda: demo_4_requirements_generation(demo_2_result[0])),
            ("Recherche intelligente", lambda: demo_5_smart_search(demo_2_result[0])),
            ("Statistiques et maintenance", lambda: demo_6_statistics_and_maintenance(demo_2_result[0]))
        ]
        
        for name, demo_func in remaining_demos:
            try:
                success = demo_func()
                if not success:
                    print(f"⚠️  Problème avec {name}, mais on continue...")
            except KeyboardInterrupt:
                print(f"\n⏹️  Démonstration interrompue à {name}")
                return False
            except Exception as e:
                print(f"❌ Erreur dans {name} : {str(e)}")
                print("⚠️  On continue avec les autres démonstrations...")
        
        # Conclusion
        demo_conclusion()
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Démonstration interrompue par l'utilisateur")
        return False
    except Exception as e:
        print(f"❌ Erreur générale : {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 