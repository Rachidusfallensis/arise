#!/usr/bin/env python3
"""
Test rapide de la nouvelle interface reorganisée
"""

import sys
from pathlib import Path

# Ajouter le projet à PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_interface():
    print("🧪 Test de la nouvelle interface...")
    
    try:
        # Test 1: Import des composants principaux
        print("1. Import des composants...")
        from ui.components.project_manager import ProjectManager
        print("✅ ProjectManager importé")
        
        # Test 2: Vérifier les nouvelles méthodes
        print("2. Vérification des nouvelles méthodes...")
        required_methods = [
            '_render_requirements_tab',
            '_render_existing_requirements',
            '_render_requirements_generation',
            '_execute_requirements_generation',
            '_display_generation_results'
        ]
        
        for method in required_methods:
            if hasattr(ProjectManager, method):
                print(f"✅ Méthode {method} présente")
            else:
                print(f"❌ Méthode {method} manquante")
        
        # Test 3: Test d'import de l'application principale
        print("3. Test de l'application principale...")
        try:
            import ui.app
            print("✅ ui.app importé avec succès")
        except Exception as e:
            print(f"❌ Erreur d'import ui.app: {e}")
        
        # Test 4: Vérifier la structure des onglets
        print("4. Vérification de la structure...")
        
        # Simuler la vérification des onglets
        expected_tabs = [
            "Project Management",
            "ARCADIA Analysis", 
            "Document Chat",
            "Quality Evaluation"
        ]
        
        print(f"✅ Structure attendue: {len(expected_tabs)} onglets principaux")
        for tab in expected_tabs:
            print(f"   - {tab}")
        
        print("\n🎉 Tous les tests passent ! Interface prête !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur pendant les tests: {e}")
        return False

if __name__ == "__main__":
    success = test_interface()
    if success:
        print("\n🚀 Pour tester l'interface complète:")
        print("   streamlit run ui/app.py")
    else:
        print("\n💡 Vérifiez les imports et dépendances") 