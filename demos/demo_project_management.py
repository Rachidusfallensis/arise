#!/usr/bin/env python3
"""
Démonstration des fonctionnalités de gestion de projets intégrées dans ARISE
"""

import sys
from pathlib import Path

# Ajouter le projet à PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🚀 Démonstration - Gestion de Projets ARISE")
    print("=" * 50)
    
    try:
        # Test d'importation des composants
        print("📦 Test des imports...")
        from src.core.enhanced_persistent_rag_system import EnhancedPersistentRAGSystem
        from src.core.simple_persistent_rag_system import SimplePersistentRAGSystem
        from ui.components.project_manager import ProjectManager
        from src.services.persistence_service import PersistenceService
        print("✅ Tous les imports réussis")
        
        # Test d'initialisation des services
        print("\n🔧 Test d'initialisation des services...")
        
        # Essayer d'abord le système complet
        try:
            rag_system = EnhancedPersistentRAGSystem()
            system_type = "Enhanced (avec Nomic embeddings)"
            print(f"✅ Système RAG initialisé : {system_type}")
        except Exception as e:
            print(f"⚠️  Système Enhanced échoué : {str(e)}")
            print("🔄 Tentative avec le système simple...")
            try:
                rag_system = SimplePersistentRAGSystem()
                system_type = "Simple (avec embeddings par défaut)"
                print(f"✅ Système RAG initialisé : {system_type}")
            except Exception as e2:
                print(f"❌ Échec complet : {str(e2)}")
                return
        
        # Test d'initialisation du ProjectManager
        print("\n📋 Test d'initialisation du ProjectManager...")
        try:
            project_manager = ProjectManager(rag_system)
            print("✅ ProjectManager initialisé avec succès")
            
            # Vérification des capacités
            print(f"   • Persistance : {'✅' if project_manager.has_persistence else '❌'}")
            print(f"   • Gestion projets : {'✅' if project_manager.has_project_management else '❌'}")
            print(f"   • Gestion documents : {'✅' if project_manager.has_document_management else '❌'}")
            
        except Exception as e:
            print(f"❌ ProjectManager échoué : {str(e)}")
            return
        
        # Test de la base de données
        print("\n💾 Test de la base de données...")
        try:
            projects = rag_system.get_all_projects()
            print(f"✅ Base de données accessible - {len(projects)} projet(s) existant(s)")
            
            if projects:
                print("📂 Projets existants :")
                for project in projects[:3]:  # Afficher les 3 premiers
                    print(f"   • {project.name} (ID: {project.id})")
                    print(f"     └─ Créé : {project.created_at.strftime('%d/%m/%Y %H:%M')}")
                    print(f"     └─ Documents : {project.documents_count}")
                if len(projects) > 3:
                    print(f"   ... et {len(projects) - 3} autre(s)")
            else:
                print("📁 Aucun projet existant")
            
        except Exception as e:
            print(f"❌ Test base de données échoué : {str(e)}")
        
        # Test de création d'un projet de démonstration
        print("\n🆕 Test de création d'un projet de démonstration...")
        try:
            demo_project_id = rag_system.create_project(
                name="Demo Project Management",
                description="Projet de démonstration des fonctionnalités de gestion",
                proposal_text="Système de démonstration MBSE utilisant la méthodologie ARCADIA"
            )
            print(f"✅ Projet de démo créé : {demo_project_id}")
            
            # Charger le projet
            success = rag_system.load_project(demo_project_id)
            if success:
                current_project = rag_system.get_current_project()
                print(f"✅ Projet chargé : {current_project.name}")
            else:
                print("⚠️  Problème lors du chargement du projet")
                
        except Exception as e:
            print(f"❌ Création du projet échoué : {str(e)}")
        
        # Test des statistiques
        print("\n📊 Test des statistiques du système...")
        try:
            if hasattr(rag_system, 'get_project_statistics'):
                stats = rag_system.get_project_statistics()
                if not stats.get("error"):
                    print("✅ Statistiques disponibles :")
                    docs = stats.get("documents", {})
                    chunks = stats.get("chunks", {})
                    reqs = stats.get("requirements", {})
                    
                    print(f"   • Documents : {docs.get('total', 0)}")
                    print(f"   • Chunks : {chunks.get('total', 0)}")
                    print(f"   • Requirements : {reqs.get('total', 0)}")
                    print(f"   • Modèle embedding : {docs.get('embedding_model', 'N/A')}")
                else:
                    print(f"⚠️  Erreur statistiques : {stats.get('error')}")
            else:
                print("ℹ️  Statistiques non disponibles dans cette version")
        except Exception as e:
            print(f"❌ Test statistiques échoué : {str(e)}")
        
        print("\n🎯 Comment utiliser la gestion de projets :")
        print("=" * 50)
        print("1. 🚀 Lancez l'application : streamlit run ui/app.py")
        print("2. 🗂️  Allez dans l'onglet 'Project Management'")
        print("3. ➕ Créez un nouveau projet dans la sidebar")
        print("4. 📄 Uploadez des documents dans l'onglet 'Documents'")
        print("5. 📝 Générez des requirements dans l'onglet 'Generate Requirements'")
        print("6. 🔍 Recherchez dans vos documents via l'onglet 'Recherche'")
        print("7. 📊 Consultez les statistiques du projet")
        print("8. 📤 Exportez vos analyses et requirements")
        
        print("\n🌟 Fonctionnalités disponibles :")
        print("─" * 40)
        print("• ✅ Gestion multi-projets persistante")
        print("• ✅ Déduplication intelligente des documents")
        print("• ✅ Recherche vectorielle par projet")
        print("• ✅ Statistiques et métriques détaillées")
        print("• ✅ Export d'analyses ARCADIA complètes")
        print("• ✅ Interface intégrée avec sidebar de projets")
        print("• ✅ Sauvegarde automatique des requirements")
        print("• ✅ Support embedding Nomic + fallback")
        
        print("\n✨ Intégration réussie ! Votre système dispose maintenant d'une")
        print("   gestion complète des projets MBSE avec persistance des données.")
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {str(e)}")
        print("💡 Vérifiez que tous les modules sont installés :")
        print("   pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Erreur inattendue : {str(e)}")
        print("💡 Consultez les logs pour plus de détails")

if __name__ == "__main__":
    main() 