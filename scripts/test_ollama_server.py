#!/usr/bin/env python3
"""
Script pour tester la connexion au serveur Ollama et lister les modèles disponibles.
"""

import requests
import json
import sys
import os

# Ajouter le répertoire parent au path pour importer config
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.config import OLLAMA_BASE_URL


def test_ollama_connection():
    """Test la connexion au serveur Ollama."""
    try:
        print(f"🔗 Test de connexion à {OLLAMA_BASE_URL}")
        
        # Test de l'endpoint /api/tags pour lister les modèles (format Ollama)
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code != 200:
            # Essayer le format OpenAI compatible
            response = requests.get(f"{OLLAMA_BASE_URL}/v1/models", timeout=10)
        
        response.raise_for_status()
        data = response.json()
        
        # Support pour les deux formats de réponse
        if 'models' in data:
            models = data['models']  # Format Ollama
        elif 'data' in data:
            models = data['data']    # Format OpenAI compatible
        else:
            models = []
        
        print(f"✅ Connexion réussie ! {len(models)} modèles disponibles :")
        print("-" * 50)
        
        for model in models:
            if 'name' in model:
                # Format Ollama
                name = model.get('name', 'N/A')
                size = model.get('size', 0)
                size_gb = size / (1024**3) if size > 0 else 0
                modified = model.get('modified', 'N/A')
                
                print(f"📦 {name}")
                if size_gb > 0:
                    print(f"   Taille: {size_gb:.1f} GB")
                if modified != 'N/A':
                    print(f"   Modifié: {modified}")
            else:
                # Format OpenAI compatible
                name = model.get('id', 'N/A')
                created = model.get('created', 'N/A')
                
                print(f"📦 {name}")
                if created != 'N/A':
                    print(f"   Créé: {created}")
            print()
        
        return True, models
        
    except requests.exceptions.ConnectTimeout:
        print("❌ Timeout de connexion. Vérifiez votre connexion réseau.")
        return False, []
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion. Le serveur n'est peut-être pas accessible.")
        print("💡 Êtes-vous connecté au VPN de l'université ?")
        return False, []
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP: {e}")
        return False, []
    except json.JSONDecodeError:
        print("❌ Réponse invalide du serveur.")
        return False, []
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False, []


def test_model_availability(model_name):
    """Test si un modèle spécifique est disponible."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": "Hello",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Modèle '{model_name}' disponible et fonctionnel")
            return True
        else:
            print(f"❌ Modèle '{model_name}' non disponible (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test du modèle '{model_name}': {e}")
        return False


def main():
    """Fonction principale."""
    print("🚀 Test du serveur Ollama GPU")
    print("=" * 50)
    
    # Test de connexion
    success, models = test_ollama_connection()
    
    if success:
        # Test des modèles configurés
        from config.config import DEFAULT_MODEL, EMBEDDING_MODEL, AI_MODELS
        
        print("🧪 Test des modèles configurés :")
        print("-" * 30)
        
        models_to_test = set([DEFAULT_MODEL, EMBEDDING_MODEL])
        for config in AI_MODELS.values():
            models_to_test.add(config["model"])
        
        for model in models_to_test:
            test_model_availability(model)
        
        print("\n📋 Modèles disponibles sur le serveur :")
        print("-" * 30)
        # Modèles basés sur ce qui a été trouvé
        available_server_models = [
            "nomic-embed-text:latest",
            "gemma3:27b",
            "gemma3:12b", 
            "gemma3:4b",
            "deepseek-r1:7b",
            "llama3:instruct",
            "mistral:latest"
        ]
        
        # Extraire les noms des modèles de la réponse
        if models:
            if 'name' in models[0]:
                available_models = [m.get('name', '') for m in models]
            else:
                available_models = [m.get('id', '') for m in models]
        else:
            available_models = []
        
        for model in available_server_models:
            status = "✅ Disponible" if any(model in available for available in available_models) else "❓ À vérifier"
            print(f"  {model}: {status}")
    
    else:
        print("\n💡 Suggestions de dépannage :")
        print("- Vérifiez votre connexion VPN à l'université")
        print("- Confirmez l'URL du serveur auprès de votre administrateur")
        print(f"- Testez avec : curl {OLLAMA_BASE_URL}/v1/models")


if __name__ == "__main__":
    main() 