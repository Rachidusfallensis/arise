#!/usr/bin/env python3
"""
Simple Test for Unified RAG System

Validation test to ensure the new unified system works correctly.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_unified_system_import():
    """Test unified system import"""
    try:
        from src.core.unified_rag_system import UnifiedRAGSystem, RAGConfiguration
        print("✅ Unified system import successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_configuration():
    """Test with basic configuration"""
    try:
        from src.core.unified_rag_system import UnifiedRAGSystem, RAGConfiguration
        
        # Minimal configuration
        config = RAGConfiguration(
            enable_enhanced_generation=False,
            enable_structured_analysis=False,
            enable_persistence=False,
            enable_validation=False,
            enable_enrichment=False
        )
        
        system = UnifiedRAGSystem(config)
        print("✅ System creation with basic configuration successful")
        
        # Test status
        status = system.get_system_status()
        print(f"✅ System status: {status['system_ready']}")
        
        return True
    except Exception as e:
        print(f"❌ Basic configuration error: {e}")
        return False

def test_generation_simple():
    """Test simple generation"""
    try:
        from src.core.unified_rag_system import UnifiedRAGSystem, RAGConfiguration
        
        # Configuration for test
        config = RAGConfiguration(
            enable_enhanced_generation=False,
            enable_structured_analysis=False,
            enable_persistence=False,
            enable_validation=False,
            enable_enrichment=False
        )
        
        system = UnifiedRAGSystem(config)
        
        # Simple test text
        test_text = """
        Test system for requirements generation.
        The system must be simple and functional.
        It must process input data correctly.
        """
        
        result = system.generate_requirements_from_proposal(
            proposal_text=test_text,
            target_phase="operational",
            requirement_types=["functional"]
        )
        
        print(f"✅ Generation successful - Quality score: {result.quality_score:.2f}")
        print(f"✅ Generation time: {result.generation_time:.2f}s")
        
        # Verify result structure
        assert hasattr(result, 'traditional_requirements')
        assert hasattr(result, 'quality_score')
        assert hasattr(result, 'generation_time')
        
        print("✅ Result structure validated")
        return True
        
    except Exception as e:
        print(f"❌ Simple generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_configuration():
    """Test with advanced configuration"""
    try:
        from src.core.unified_rag_system import UnifiedRAGSystem, RAGConfiguration
        
        # Complete configuration (without persistence to avoid DB errors)
        config = RAGConfiguration(
            enable_enhanced_generation=True,
            enable_structured_analysis=True,
            enable_persistence=False,  # Disabled for tests
            enable_validation=True,
            enable_enrichment=True,
            enable_cross_phase_analysis=True
        )
        
        system = UnifiedRAGSystem(config)
        print("✅ System creation with advanced configuration successful")
        
        # Check available components
        status = system.get_system_status()
        components = status["available_components"]
        
        expected_components = [
            'enhanced_generation', 
            'structured_analysis',
            'validation_pipeline',
            'context_enrichment'
        ]
        
        for component in expected_components:
            if components.get(component, False):
                print(f"✅ Component {component} available")
            else:
                print(f"⚠️  Component {component} not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced configuration error: {e}")
        return False

def main():
    """Main test"""
    print("🧪 Unified RAG System Test")
    print("=" * 50)
    
    tests = [
        ("System import", test_unified_system_import),
        ("Basic configuration", test_basic_configuration),
        ("Simple generation", test_generation_simple),
        ("Advanced configuration", test_enhanced_configuration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Results summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Final Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The unified system is operational.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 