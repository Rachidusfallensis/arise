#!/usr/bin/env python3
"""
Test script for the enhanced UI integration with structured ARCADIA analysis.
Verifies that all components work together correctly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem
        print("✅ EnhancedStructuredRAGSystem import successful")
    except Exception as e:
        print(f"❌ EnhancedStructuredRAGSystem import failed: {e}")
        return False
    
    try:
        from src.models.arcadia_outputs import OperationalAnalysis
        print("✅ OperationalAnalysis import successful")
    except Exception as e:
        print(f"❌ OperationalAnalysis import failed: {e}")
        return False
    
    try:
        from ui.app import structured_arcadia_tab, display_analysis_overview
        print("✅ UI function imports successful")
    except Exception as e:
        print(f"❌ UI function imports failed: {e}")
        return False
    
    return True

def test_system_initialization():
    """Test that the enhanced system can be initialized"""
    print("\n🔧 Testing system initialization...")
    
    try:
        from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem
        system = EnhancedStructuredRAGSystem()
        print("✅ Enhanced system initialized successfully")
        
        # Test if key methods exist
        required_methods = [
            'generate_enhanced_requirements_from_proposal',
            'export_structured_requirements',
            'get_structured_analysis_summary'
        ]
        
        for method in required_methods:
            if hasattr(system, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return False

def test_ui_components():
    """Test that UI components are properly structured"""
    print("\n🖥️ Testing UI components...")
    
    try:
        # Test streamlit imports (optional - may not be available in test environment)
        import streamlit as st
        print("✅ Streamlit available")
    except ImportError:
        print("⚠️ Streamlit not available (OK for testing)")
    
    # Test that UI functions are defined
    try:
        from ui.app import (
            structured_arcadia_tab,
            display_analysis_overview,
            display_operational_analysis,
            display_system_analysis,
            display_cross_phase_analysis
        )
        print("✅ All UI functions defined")
        return True
    except Exception as e:
        print(f"❌ UI functions test failed: {e}")
        return False

def test_configuration():
    """Test that configuration files are accessible"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import config, arcadia_config
        print("✅ Configuration imports successful")
        
        # Test that enhanced export formats are available
        if hasattr(config, 'REQUIREMENTS_OUTPUT_FORMATS'):
            formats = config.REQUIREMENTS_OUTPUT_FORMATS
            print(f"✅ Available export formats: {formats}")
        
        # Test ARCADIA phases configuration
        if hasattr(arcadia_config, 'ARCADIA_PHASES'):
            phases = list(arcadia_config.ARCADIA_PHASES.keys())
            print(f"✅ Available ARCADIA phases: {phases}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_data_models():
    """Test that data models are properly structured"""
    print("\n📊 Testing data models...")
    
    try:
        from src.models.arcadia_outputs import (
            OperationalActor,
            OperationalCapability,
            SystemFunction,
            CrossPhaseAnalysis
        )
        print("✅ Data model imports successful")
        
        # Test creating sample instances
        actor = OperationalActor(
            id="ACT001",
            name="Test Actor",
            description="Test description",
            role_definition="Test role"
        )
        print("✅ Sample actor created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Data models test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 Starting Enhanced UI Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("System Initialization", test_system_initialization),
        ("UI Components", test_ui_components),
        ("Configuration", test_configuration),
        ("Data Models", test_data_models)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! UI integration is ready.")
        print("\n📝 Next steps:")
        print("1. Run the Streamlit app: streamlit run ui/app.py")
        print("2. Test the new 'Structured ARCADIA Analysis' tab")
        print("3. Try the enhanced export formats (ARCADIA_JSON, Structured_Markdown)")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 