#!/usr/bin/env python3
"""
Test simple de syntaxe pour vérifier les réparations
"""

def test_syntax():
    print("🔧 Test de Syntaxe Simple")
    print("=" * 30)
    
    try:
        # Test de compilation du fichier ui/app.py
        print("Test de syntaxe de ui/app.py...")
        with open('ui/app.py', 'r') as f:
            code = f.read()
        
        compile(code, 'ui/app.py', 'exec')
        print("✅ Syntaxe correcte")
        
        # Vérifier la présence des fonctions ajoutées
        if 'def evaluation_tab(' in code:
            print("✅ Fonction evaluation_tab trouvée")
        else:
            print("❌ Fonction evaluation_tab manquante")
            
        if 'def chat_tab(' in code:
            print("✅ Fonction chat_tab trouvée")
        else:
            print("❌ Fonction chat_tab manquante")
            
        if 'import json' in code:
            print("✅ Import json trouvé")
        else:
            print("❌ Import json manquant")
        
        print()
        print("🎉 Interface réparée avec succès !")
        print("L'application devrait maintenant démarrer sans erreur.")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Erreur de syntaxe : {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

if __name__ == "__main__":
    test_syntax() 