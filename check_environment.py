#!/usr/bin/env python3
import sys
import importlib
import requests

def check_environment():
    print("🔍 ARISE Environment Check")
    print("=" * 30)
    
    # Check Python version
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.9+")
        return False
    
    # Check key packages
    required_packages = [
        'streamlit', 'langchain', 'ollama', 'chromadb', 
        'pandas', 'numpy', 'transformers', 'torch'
    ]
    
    print("\n📦 Package Check:")
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    # Check Ollama connectivity
    print("\n🤖 Ollama Check:")
    try:
        response = requests.get("http://llm-eva.univ-pau.fr:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server accessible")
        else:
            print("⚠️ Ollama server responded with error")
    except:
        print("❌ Ollama server not accessible")
    
    print("\n" + "=" * 30)
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install " + " ".join(missing))
        return False
    else:
        print("✅ Environment looks good!")
        return True

if __name__ == "__main__":
    check_environment()
