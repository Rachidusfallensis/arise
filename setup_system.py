#!/usr/bin/env python3
"""
SAFE MBSE RAG System - Setup and Verification Script

This script helps you set up and verify your SAFE MBSE RAG system installation.
It checks dependencies, tests connectivity, and provides setup guidance.
"""

import sys
import subprocess
import importlib
from pathlib import Path
import requests
import json

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.9+")
        return False

def check_virtual_environment():
    """Check if running in virtual environment"""
    print("\n🔒 Checking virtual environment...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        return True
    else:
        print("⚠️  Not in virtual environment")
        print("💡 Recommended: python -m venv venv && source venv/bin/activate")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking required packages...")
    
    required_packages = [
        ("streamlit", "streamlit"),
        ("langchain", "langchain"),
        ("ollama", "ollama"),
        ("chromadb", "chromadb"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("sentence-transformers", "sentence_transformers"),
        ("transformers", "transformers"),
        ("torch", "torch"),
        ("plotly", "plotly"),
        ("PyPDF2", "PyPDF2"),
        ("python-docx", "docx"),
        ("pydantic", "pydantic"),
    ]
    
    missing_packages = []
    installed_count = 0
    
    for package_name, import_name in required_packages:
        if check_package(package_name, import_name):
            print(f"✅ {package_name}")
            installed_count += 1
        else:
            print(f"❌ {package_name}")
            missing_packages.append(package_name)
    
    print(f"\n📊 Packages: {installed_count}/{len(required_packages)} installed")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages installed")
        return True

def check_ollama_connectivity():
    """Check if Ollama server is accessible"""
    print("\n🤖 Checking Ollama connectivity...")
    
    ollama_urls = [
        "http://localhost:11434",
        "http://llm-eva.univ-pau.fr:11434"
    ]
    
    for url in ollama_urls:
        try:
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✅ Ollama server accessible at {url}")
                print(f"📦 Available models: {len(models)}")
                
                # Check for required models
                model_names = [model['name'] for model in models]
                required_models = ['llama3:instruct', 'nomic-embed-text:latest']
                
                for model in required_models:
                    if any(model in name for name in model_names):
                        print(f"  ✅ {model}")
                    else:
                        print(f"  ❌ {model} (missing)")
                        print(f"     Install with: ollama pull {model}")
                
                return True
                
        except Exception as e:
            print(f"❌ {url} - {str(e)}")
    
    print("💡 Install Ollama: https://ollama.ai")
    print("💡 Then pull models: ollama pull llama3:instruct && ollama pull nomic-embed-text:latest")
    return False

def check_directory_structure():
    """Check if project structure is correct"""
    print("\n📁 Checking project structure...")
    
    required_dirs = [
        "src",
        "src/core", 
        "src/services",
        "config",
        "ui",
        "data"
    ]
    
    required_files = [
        "ui/app.py",
        "config/config.py",
        "config/arcadia_config.py",
        "src/core/rag_system.py",
        "requirements.txt",
        "run_app.py"
    ]
    
    missing_items = []
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/")
            missing_items.append(dir_path)
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_items.append(file_path)
    
    if missing_items:
        print(f"\n❌ Missing: {', '.join(missing_items)}")
        return False
    else:
        print("✅ Project structure is correct")
        return True

def create_data_directories():
    """Create necessary data directories"""
    print("\n📂 Creating necessary directories...")
    
    directories = [
        "data/vectordb",
        "data/examples", 
        "data/templates",
        "logs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}")

def test_basic_functionality():
    """Test basic system functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test imports
        from src.core.rag_system import SAFEMBSERAGSystem
        print("✅ Basic imports successful")
        
        # Test system initialization (without actually running LLM)
        print("✅ Core modules accessible")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    print("🚀 SAFE MBSE RAG System - Setup & Verification")
    print("=" * 60)
    
    checks = []
    
    # Run all checks
    checks.append(check_python_version())
    checks.append(check_virtual_environment())
    checks.append(check_dependencies())
    checks.append(check_directory_structure())
    
    # Create directories regardless of other checks
    create_data_directories()
    
    checks.append(check_ollama_connectivity())
    checks.append(test_basic_functionality())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your system is ready to use")
        print("\n🚀 Next steps:")
        print("   1. Run: python demos/quick_start_demo.py")
        print("   2. Or run: python run_app.py")
        print("   3. Open: http://localhost:8501")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("❌ Please fix the issues above before proceeding")
        
        if not checks[2]:  # Dependencies check
            print("\n💡 Quick fix for dependencies:")
            print("   pip install -r requirements.txt")
        
        if not checks[4]:  # Ollama check
            print("\n💡 Quick fix for Ollama:")
            print("   1. Install Ollama: https://ollama.ai")
            print("   2. Run: ollama pull llama3:instruct")
            print("   3. Run: ollama pull nomic-embed-text:latest")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("💡 Please report this issue on GitHub") 