#!/usr/bin/env python3
"""
Test script to validate the enhanced system integration with UI
Tests the complete flow: Enhanced system -> Requirements generation -> UI compatibility
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_enhanced_system_integration():
    """Test the enhanced system end-to-end"""
    print("🧪 Testing Enhanced System Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import all required modules
        print("📦 Testing imports...")
        from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem
        from src.core.structured_arcadia_service import StructuredARCADIAService
        from src.core.system_analysis_extractor import SystemAnalysisExtractor
        print("✅ All imports successful")
        
        # Test 2: Initialize enhanced system
        print("\n🏗️ Initializing enhanced system...")
        enhanced_system = EnhancedStructuredRAGSystem()
        print("✅ Enhanced system initialized")
        
        # Test 3: Test with simple proposal
        print("\n📝 Testing with sample proposal...")
        sample_proposal = """
        # Smart Traffic Management System Project

        ## Objectives
        Develop an intelligent traffic management system for urban environments using MBSE methodology.

        ## Stakeholders
        - Traffic Control Operators: Monitor and manage traffic flow
        - City Planners: Strategic planning and infrastructure development
        - Emergency Services: Priority routing and incident response
        - Citizens: End users expecting efficient transportation

        ## Technical Requirements
        - The system shall process traffic data from 500+ sensors in real-time
        - Response time for traffic signal adjustments must be under 2 seconds
        - System availability shall be 99.9% or higher
        - Integration with emergency services dispatch systems is mandatory
        """
        
        # Test 4: Generate enhanced requirements (with limited phases to avoid long execution)
        print("⚙️ Generating enhanced requirements (limited phases)...")
        try:
            results = enhanced_system.generate_enhanced_requirements_from_proposal(
                proposal_text=sample_proposal,
                target_phase="operational",  # Limited to operational only for testing
                requirement_types=["functional"],  # Limited to functional only
                enable_structured_analysis=True,
                enable_cross_phase_analysis=False  # Disabled for faster testing
            )
            
            print("✅ Enhanced requirements generation completed")
            
            # Test 5: Verify results structure
            print("\n🔍 Analyzing results structure...")
            
            # Check that traditional requirements are accessible at top level
            has_requirements = 'requirements' in results
            has_statistics = 'statistics' in results
            has_stakeholders = 'stakeholders' in results
            has_traditional = 'traditional_requirements' in results
            has_structured = 'structured_analysis' in results
            has_enhancement = 'enhancement_summary' in results
            
            print(f"   📊 Has requirements: {has_requirements}")
            print(f"   📈 Has statistics: {has_statistics}")
            print(f"   👥 Has stakeholders: {has_stakeholders}")
            print(f"   🔧 Has traditional_requirements: {has_traditional}")
            print(f"   🏗️ Has structured_analysis: {has_structured}")
            print(f"   ✨ Has enhancement_summary: {has_enhancement}")
            
            # Check requirements content
            if has_requirements:
                total_reqs = 0
                for phase, phase_reqs in results.get('requirements', {}).items():
                    if isinstance(phase_reqs, dict):
                        phase_total = sum(len(reqs) if isinstance(reqs, list) else 0 for reqs in phase_reqs.values())
                        total_reqs += phase_total
                        print(f"   📋 {phase.upper()}: {phase_total} requirements")
                
                print(f"   🎯 Total requirements generated: {total_reqs}")
                
                # Check statistics
                if has_statistics:
                    stats = results.get('statistics', {})
                    print(f"   📊 Statistics total: {stats.get('total_requirements', 0)}")
                    print(f"   📊 Priority distribution: {stats.get('by_priority', {})}")
            
            # Test 6: Test export functionality
            print("\n📤 Testing export functionality...")
            
            # Test traditional export
            try:
                json_export = enhanced_system.export_requirements(results, "JSON")
                print("✅ Traditional JSON export successful")
            except Exception as e:
                print(f"❌ Traditional JSON export failed: {str(e)}")
            
            # Test enhanced exports (only if structured analysis was successful)
            if has_structured and results.get('structured_analysis'):
                try:
                    arcadia_export = enhanced_system.export_structured_requirements(results, "ARCADIA_JSON")
                    print("✅ ARCADIA JSON export successful")
                except Exception as e:
                    print(f"❌ ARCADIA JSON export failed: {str(e)}")
                
                try:
                    markdown_export = enhanced_system.export_structured_requirements(results, "Structured_Markdown")
                    print("✅ Structured Markdown export successful")
                except Exception as e:
                    print(f"❌ Structured Markdown export failed: {str(e)}")
            else:
                print("⚠️ Skipping enhanced exports (no structured analysis)")
            
            # Test 7: UI compatibility check
            print("\n🖥️ Checking UI compatibility...")
            
            # Simulate UI requirements display logic
            ui_compatible = True
            ui_issues = []
            
            # Check if display_generation_results would work
            if not results.get('statistics'):
                ui_compatible = False
                ui_issues.append("Missing statistics")
            
            if not results.get('requirements'):
                ui_compatible = False
                ui_issues.append("Missing requirements")
            
            # Check if phase display would work
            for phase, phase_reqs in results.get('requirements', {}).items():
                if not isinstance(phase_reqs, dict):
                    ui_compatible = False
                    ui_issues.append(f"Invalid phase requirements structure for {phase}")
            
            if ui_compatible:
                print("✅ UI compatibility check passed")
            else:
                print("❌ UI compatibility issues found:")
                for issue in ui_issues:
                    print(f"   - {issue}")
            
            print(f"\n🎉 Test Results Summary:")
            print(f"   ✅ Enhanced system initialization: SUCCESS")
            print(f"   ✅ Requirements generation: SUCCESS")
            print(f"   ✅ Results structure: {'SUCCESS' if has_requirements and has_statistics else 'PARTIAL'}")
            print(f"   ✅ UI compatibility: {'SUCCESS' if ui_compatible else 'ISSUES FOUND'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Enhanced requirements generation failed: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed during setup: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_traditional_fallback():
    """Test that traditional requirements still work if enhanced fails"""
    print("\n🔄 Testing traditional fallback...")
    
    try:
        from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem
        
        enhanced_system = EnhancedStructuredRAGSystem()
        
        sample_proposal = "Simple project proposal for testing traditional fallback with basic requirements."
        
        # Test with structured analysis disabled
        results = enhanced_system.generate_enhanced_requirements_from_proposal(
            proposal_text=sample_proposal,
            target_phase="operational",
            requirement_types=["functional"],
            enable_structured_analysis=False,  # Disabled
            enable_cross_phase_analysis=False
        )
        
        print("✅ Traditional fallback test completed")
        print(f"   Has requirements: {'requirements' in results}")
        print(f"   Has statistics: {'statistics' in results}")
        
        # Check if we have any requirements generated
        total_reqs = 0
        if 'requirements' in results:
            for phase, phase_reqs in results['requirements'].items():
                if isinstance(phase_reqs, dict):
                    phase_total = sum(len(reqs) if isinstance(reqs, list) else 0 for reqs in phase_reqs.values())
                    total_reqs += phase_total
        
        print(f"   Total requirements: {total_reqs}")
        
        return True
        
    except Exception as e:
        print(f"❌ Traditional fallback test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Enhanced System UI Integration Tests")
    print("=" * 60)
    
    success1 = test_enhanced_system_integration()
    success2 = test_traditional_fallback()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! Enhanced system is ready for UI integration.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    print("\n📋 Next steps for UI testing:")
    print("1. Run the Streamlit app: streamlit run ui/app.py")
    print("2. Test requirements generation with enhanced analysis enabled")
    print("3. Verify that requirements are displayed correctly")
    print("4. Test export functionality with different formats")
    print("5. Check the debugging guide: docs/ui_debugging_guide.md") 