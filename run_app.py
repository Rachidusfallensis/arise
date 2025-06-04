#!/usr/bin/env python3
"""
SAFE MBSE RAG System - Main Application Runner

Enhanced version with comprehensive validation and setup verification.
This script ensures all dependencies and configurations are properly set up
before launching the Streamlit web interface.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import pkg_resources
from typing import List, Tuple


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    required_version = (3, 9)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]}+ required. Current: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"✅ Python version: {current_version[0]}.{current_version[1]}")
    return True


def check_virtual_environment() -> bool:
    """Check if virtual environment exists and is activated."""
    script_dir = Path(__file__).parent
    venv_path = script_dir / "venv"
    
    # Check if venv directory exists
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("Please create it with: python -m venv venv")
        return False
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment exists but is not activated")
        print("Please activate it with: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
        return False
    
    print("✅ Virtual environment is active")
    return True


def check_required_packages() -> Tuple[bool, List[str]]:
    """Check if all required packages are installed."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False, []
    
    missing_packages = []
    
    try:
        with open(requirements_file, 'r') as f:
            requirements = f.read().splitlines()
        
        # Filter out comments and empty lines
        requirements = [req.strip() for req in requirements if req.strip() and not req.strip().startswith('#')]
        
        print("📦 Checking required packages...")
        
        for requirement in requirements:
            # Parse package name (handle version specifiers)
            package_name = requirement.split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()
            
            try:
                pkg_resources.get_distribution(package_name)
                print(f"  ✅ {package_name}")
            except pkg_resources.DistributionNotFound:
                print(f"  ❌ {package_name} - Missing")
                missing_packages.append(package_name)
            except Exception as e:
                print(f"  ⚠️  {package_name} - Check failed: {e}")
                missing_packages.append(package_name)
    
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False, []
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False, missing_packages
    
    print("✅ All required packages are installed")
    return True, []


def check_environment_variables() -> bool:
    """Check for required environment variables."""
    required_env_vars: List[Tuple[str, str]] = []  # No required API keys for Ollama setup
    
    optional_env_vars = [
        ("LANGCHAIN_API_KEY", "LangChain API key for enhanced functionality"),
        ("LANGCHAIN_TRACING_V2", "LangChain tracing (set to 'true' for debugging)"),
        ("OLLAMA_BASE_URL", "Custom Ollama base URL (defaults to config value)"),
    ]
    
    print("🔑 Checking environment variables...")
    
    missing_required = []
    
    # Check required vars (none for Ollama setup)
    if not required_env_vars:
        print("  ✅ No required API keys (using Ollama local models)")
    
    for var_name, description in required_env_vars:
        if not os.getenv(var_name):
            print(f"  ❌ {var_name} - {description}")
            missing_required.append(var_name)
        else:
            print(f"  ✅ {var_name} - Set")
    
    for var_name, description in optional_env_vars:
        if os.getenv(var_name):
            print(f"  ✅ {var_name} - Set (optional)")
        else:
            print(f"  ⚪ {var_name} - Not set (optional) - {description}")
    
    if missing_required:
        print("\n❌ Missing required environment variables!")
        print("Set them in your environment:")
        for var in missing_required:
            print(f"  export {var}=your_value_here")
        return False
    
    return True


def check_ollama_connectivity() -> bool:
    """Check if Ollama server is accessible and models are available."""
    try:
        import requests
    except ImportError:
        print("  ⚠️  requests package not available for Ollama check")
        return True  # Don't fail if requests isn't available
    
    print("🤖 Checking Ollama connectivity...")
    
    # Get Ollama URL from config
    try:
        import sys
        from pathlib import Path
        
        # Add config to path
        config_path = Path(__file__).parent / "config"
        if str(config_path) not in sys.path:
            sys.path.insert(0, str(config_path))
        
        import config
        ollama_url = getattr(config, 'OLLAMA_BASE_URL', 'http://chat-eva.univ-pau.fr:11434')
        models = getattr(config, 'AI_MODELS', {})
        
    except Exception as e:
        print(f"  ⚠️  Could not load config: {e}")
        ollama_url = "http://chat-eva.univ-pau.fr:11434"
        models = {}
    
    # Check server connectivity
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Ollama server accessible at {ollama_url}")
            
            # Check available models
            available_models = response.json().get('models', [])
            model_names = [model['name'] for model in available_models]
            
            print(f"  📦 Available models: {len(model_names)}")
            
            # Check if required models are available
            required_models = []
            for service, model_config in models.items():
                if isinstance(model_config, dict) and 'model' in model_config:
                    required_models.append(model_config['model'])
            
            # Also check from config direct values
            try:
                import config
                if hasattr(config, 'DEFAULT_MODEL'):
                    required_models.append(config.DEFAULT_MODEL)
                if hasattr(config, 'EMBEDDING_MODEL'):
                    required_models.append(config.EMBEDDING_MODEL)
            except:
                pass
            
            required_models = list(set(required_models))  # Remove duplicates
            
            missing_models = []
            for model in required_models:
                if any(model in available_model for available_model in model_names):
                    print(f"    ✅ {model}")
                else:
                    print(f"    ❌ {model} - Not found")
                    missing_models.append(model)
            
            if missing_models:
                print(f"\n  ⚠️  Missing models: {', '.join(missing_models)}")
                print(f"  📥 Install with: ollama pull <model_name>")
                return False
            
            return True
            
        else:
            print(f"  ❌ Ollama server returned status {response.status_code}")
            return False
            
    except Exception as e:
        if "ConnectionError" in str(type(e)):
            print(f"  ❌ Cannot connect to Ollama server at {ollama_url}")
            print(f"  💡 Make sure Ollama is running and accessible")
        elif "Timeout" in str(type(e)):
            print(f"  ❌ Timeout connecting to Ollama server")
        else:
            print(f"  ❌ Error checking Ollama: {e}")
        return False


def check_directory_structure() -> bool:
    """Check if required directories and files exist."""
    script_dir = Path(__file__).parent
    
    required_dirs = [
        "src",
        "src/core", 
        "src/services",
        "config",
        "ui",
        "data",
    ]
    
    required_files = [
        "ui/app.py",
        "config/config.py",
        "config/arcadia_config.py",
        "src/core/rag_system.py",
        "src/services/evaluation_service.py",
    ]
    
    print("📁 Checking directory structure...")
    
    missing_items = []
    
    # Check directories
    for dir_path in required_dirs:
        full_path = script_dir / dir_path
        if not full_path.exists():
            print(f"  ❌ Directory missing: {dir_path}")
            missing_items.append(dir_path)
        else:
            print(f"  ✅ {dir_path}")
    
    # Check files
    for file_path in required_files:
        full_path = script_dir / file_path
        if not full_path.exists():
            print(f"  ❌ File missing: {file_path}")
            missing_items.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_items:
        print(f"\n❌ Missing required items: {len(missing_items)}")
        return False
    
    return True


def create_data_directories():
    """Create necessary data directories if they don't exist."""
    script_dir = Path(__file__).parent
    
    directories_to_create = [
        "data/vectordb",
        "data/examples", 
        "data/templates",
        "logs",
    ]
    
    print("📂 Creating necessary directories...")
    
    for dir_path in directories_to_create:
        full_path = script_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")


def setup_environment():
    """Setup environment variables and paths."""
    script_dir = Path(__file__).parent
    src_path = script_dir / "src"
    
    # Add src to Python path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Set environment variables
    os.environ["PYTHONPATH"] = str(src_path)
    
    print("✅ Environment paths configured")


def run_pre_launch_checks() -> bool:
    """Run all pre-launch validation checks."""
    print("🔍 Running pre-launch validation checks...")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Required Packages", lambda: check_required_packages()[0]),
        ("Environment Variables", check_environment_variables),
        ("Directory Structure", check_directory_structure),
        ("Ollama Connectivity", check_ollama_connectivity),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"  ❌ Check failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ All validation checks passed!")
        return True
    else:
        print("❌ Some validation checks failed!")
        print("\nPlease fix the issues above before running the application.")
        return False


def launch_streamlit():
    """Launch the Streamlit application."""
    script_dir = Path(__file__).parent
    ui_app_path = script_dir / "ui" / "app.py"
    
    print("\n🚀 Launching SAFE MBSE RAG System...")
    print("=" * 60)
    print("🌐 The app will open at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the server")
    print("💡 Features included:")
    print("  • 🧠 AI-Powered Requirements Generation")
    print("  • 🏗️ ARCADIA Methodology Integration")
    print("=" * 60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(ui_app_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        print("👋 Thank you for using SAFE MBSE RAG System!")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)


def main():
    """Main entry point for the application."""
    print("🏗️ SAFE MBSE RAG System")
    print("AI-Driven Requirements Generation using ARCADIA Methodology")
    print("=" * 60)
    
    try:
        # Change to script directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Create necessary directories
        create_data_directories()
        
        # Setup environment
        setup_environment()
        
        # Run validation checks
        if not run_pre_launch_checks():
            print("\n❌ Validation failed. Please fix the issues and try again.")
            sys.exit(1)
        
        # Launch application
        launch_streamlit()
        
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
