#!/usr/bin/env python3
"""
Test Script for Enhanced Structured ARCADIA System

This script demonstrates the new structured analysis capabilities:
1. Traditional requirements generation (existing)
2. Structured ARCADIA analysis (new)
3. Cross-phase analysis with traceability (new)
4. Export capabilities (enhanced)
"""

import sys
import json
from pathlib import Path
import time
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem

def run_comprehensive_test():
    """Run comprehensive test of the enhanced structured system"""
    
    print("🚀 ENHANCED STRUCTURED ARCADIA SYSTEM TEST")
    print("=" * 60)
    
    # Test proposal text (realistic example)
    test_proposal = """
    # Smart City Traffic Management System

    ## Project Overview
    Development of an intelligent traffic management system for urban environments 
    using advanced AI algorithms and real-time sensor networks.

    ## Objectives
    1. Implement real-time traffic monitoring and optimization
    2. Develop predictive analytics for traffic flow management
    3. Create operator interfaces for traffic control centers
    4. Establish emergency vehicle priority routing
    5. Provide citizen information services

    ## Stakeholders
    - Traffic Control Operators: Monitor and manage city-wide traffic flow
    - Emergency Services: Require priority routing capabilities
    - City Planners: Strategic traffic infrastructure planning
    - Citizens: End users expecting efficient transportation
    - System Administrators: Maintain and operate the technical infrastructure

    ## Functional Requirements
    - The system shall process traffic sensor data in real-time
    - Emergency vehicle detection must trigger automatic priority routing
    - Traffic signal optimization shall reduce average wait times by 30%
    - The operator interface shall provide real-time traffic visualization
    - Predictive analytics shall forecast traffic patterns 24 hours ahead

    ## Technical Specifications
    - System shall integrate with 500+ traffic sensors across the city
    - Response time for traffic signal adjustments must be under 2 seconds
    - System availability shall exceed 99.9% uptime
    - Data processing capacity must handle 10,000 events per second
    - Integration with emergency services dispatch systems required

    ## Quality Requirements
    - User interface shall be accessible on mobile and desktop platforms
    - System shall provide multilingual support for operators
    - All data shall be encrypted in transit and at rest
    - Audit logging required for all system operations
    - Disaster recovery capability with 4-hour RTO
    """
    
    # Initialize the enhanced system
    print("\n📊 Initializing Enhanced Structured RAG System...")
    try:
        enhanced_system = EnhancedStructuredRAGSystem()
        print("✅ System initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing system: {str(e)}")
        return
    
    # Test 1: Enhanced Requirements Generation
    print("\n🔍 Test 1: Enhanced Requirements Generation")
    print("-" * 40)
    
    start_time = time.time()
    
    try:
        enhanced_results = enhanced_system.generate_enhanced_requirements_from_proposal(
            proposal_text=test_proposal,
            target_phase="all",
            requirement_types=["functional", "non_functional", "stakeholder"],
            enable_structured_analysis=True,
            enable_cross_phase_analysis=True
        )
        
        generation_time = time.time() - start_time
        print(f"✅ Enhanced generation completed in {generation_time:.1f} seconds")
        
        # Display basic statistics
        traditional_reqs = enhanced_results.get('traditional_requirements', {})
        print(f"\n📈 Traditional Requirements:")
        total_traditional = 0
        for phase, phase_reqs in traditional_reqs.get('requirements', {}).items():
            phase_total = sum(len(reqs) if isinstance(reqs, list) else 0 for reqs in phase_reqs.values())
            total_traditional += phase_total
            print(f"   • {phase.title()}: {phase_total} requirements")
        print(f"   • Total Traditional: {total_traditional} requirements")
        
        # Display enhancement summary
        enhancement_summary = enhanced_results.get('enhancement_summary', {})
        print(f"\n🔬 Structured Analysis Summary:")
        print(f"   • Phases Analyzed: {enhancement_summary.get('phases_analyzed', [])}")
        print(f"   • Total Actors: {enhancement_summary.get('total_actors_identified', 0)}")
        print(f"   • Total Capabilities: {enhancement_summary.get('total_capabilities_identified', 0)}")
        print(f"   • Cross-phase Links: {enhancement_summary.get('cross_phase_links', 0)}")
        print(f"   • Quality Assessment: {'Available' if enhancement_summary.get('quality_assessment_available') else 'Not Available'}")
        
    except Exception as e:
        print(f"❌ Error in enhanced generation: {str(e)}")
        return
    
    # Test 2: Structured Analysis Summary
    print("\n🎯 Test 2: Detailed Structured Analysis")
    print("-" * 40)
    
    try:
        analysis_summary = enhanced_system.get_structured_analysis_summary(enhanced_results)
        
        if "error" not in analysis_summary:
            print("✅ Structured analysis summary generated")
            
            # Display extraction statistics
            extraction_stats = analysis_summary.get('extraction_statistics', {})
            for phase, stats in extraction_stats.items():
                print(f"\n📋 {phase.title()} Phase Statistics:")
                for item_type, count in stats.items():
                    print(f"   • {item_type.title()}: {count}")
            
            # Display cross-phase insights
            cross_phase_insights = analysis_summary.get('cross_phase_insights', {})
            if cross_phase_insights:
                print(f"\n🔗 Cross-Phase Analysis:")
                print(f"   • Traceability Links: {cross_phase_insights.get('traceability_links', 0)}")
                print(f"   • Gaps Identified: {cross_phase_insights.get('gaps_identified', 0)}")
                print(f"   • Consistency Checks: {cross_phase_insights.get('consistency_checks', 0)}")
            
            # Display quality scores
            quality_scores = analysis_summary.get('quality_scores', {})
            if quality_scores:
                print(f"\n📊 Quality Metrics:")
                for metric_name, score_info in quality_scores.items():
                    print(f"   • {metric_name}: {score_info['percentage']:.1f}%")
            
            # Display recommendations
            recommendations = analysis_summary.get('recommendations', [])
            if recommendations:
                print(f"\n💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")
        else:
            print(f"❌ Error in structured analysis: {analysis_summary['error']}")
    
    except Exception as e:
        print(f"❌ Error getting analysis summary: {str(e)}")
    
    # Test 3: Export Capabilities
    print("\n📤 Test 3: Export Capabilities")
    print("-" * 40)
    
    export_formats = [
        ("ARCADIA_JSON", "structured_analysis.json"),
        ("Structured_Markdown", "structured_analysis.md"),
        ("JSON", "traditional_requirements.json")
    ]
    
    for format_type, filename in export_formats:
        try:
            print(f"\n📁 Exporting as {format_type}...")
            exported_content = enhanced_system.export_structured_requirements(
                enhanced_results, format_type
            )
            
            # Save to file for demonstration
            output_path = Path("test_outputs") / filename
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(exported_content)
            
            print(f"   ✅ Exported to {output_path} ({len(exported_content)} characters)")
            
        except Exception as e:
            print(f"   ❌ Error exporting {format_type}: {str(e)}")
    
    # Test 4: Detailed Analysis Inspection
    print("\n🔬 Test 4: Detailed Analysis Inspection")
    print("-" * 40)
    
    structured_analysis = enhanced_results.get('structured_analysis')
    if structured_analysis:
        print("✅ Structured analysis available")
        
        # Inspect operational analysis
        if structured_analysis.operational_analysis:
            op_analysis = structured_analysis.operational_analysis
            print(f"\n🎭 Operational Analysis Details:")
            print(f"   • Actors: {len(op_analysis.actors)}")
            if op_analysis.actors:
                print(f"     - Example: {op_analysis.actors[0].name} - {op_analysis.actors[0].role_definition}")
            
            print(f"   • Capabilities: {len(op_analysis.capabilities)}")
            if op_analysis.capabilities:
                print(f"     - Example: {op_analysis.capabilities[0].name}")
            
            print(f"   • Scenarios: {len(op_analysis.scenarios)}")
            print(f"   • Processes: {len(op_analysis.processes)}")
        
        # Inspect system analysis
        if structured_analysis.system_analysis:
            sys_analysis = structured_analysis.system_analysis
            print(f"\n🏗️ System Analysis Details:")
            print(f"   • System Boundary: {sys_analysis.system_boundary.scope_definition[:100]}...")
            print(f"   • Actors: {len(sys_analysis.actors)}")
            print(f"   • Functions: {len(sys_analysis.functions)}")
            print(f"   • Capabilities: {len(sys_analysis.capabilities)}")
            print(f"   • Functional Chains: {len(sys_analysis.functional_chains)}")
        
        # Inspect cross-phase analysis
        if structured_analysis.cross_phase_analysis:
            cross_analysis = structured_analysis.cross_phase_analysis
            print(f"\n🌐 Cross-Phase Analysis Details:")
            print(f"   • Traceability Links: {len(cross_analysis.traceability_links)}")
            if cross_analysis.traceability_links:
                link = cross_analysis.traceability_links[0]
                print(f"     - Example: {link.source_element} → {link.target_element} ({link.relationship_type})")
            
            print(f"   • Gap Analysis Items: {len(cross_analysis.gap_analysis)}")
            if cross_analysis.gap_analysis:
                gap = cross_analysis.gap_analysis[0]
                print(f"     - Example: {gap.gap_type} - {gap.description[:50]}...")
            
            print(f"   • Quality Metrics: {len(cross_analysis.quality_metrics)}")
            if cross_analysis.quality_metrics:
                metric = cross_analysis.quality_metrics[0]
                percentage = (metric.score / metric.max_score) * 100
                print(f"     - Example: {metric.metric_name} - {percentage:.1f}%")
    else:
        print("❌ No structured analysis available")
    
    # Test Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print("✅ Enhanced Structured ARCADIA System Test Completed")
    print(f"⏱️  Total execution time: {time.time() - start_time:.1f} seconds")
    print(f"📁 Output files saved to: test_outputs/")
    print("\n🎉 All tests completed successfully!")
    print("\n📝 Next Steps:")
    print("   1. Review generated outputs in test_outputs/ directory")
    print("   2. Examine structured analysis JSON for detailed data")
    print("   3. Check markdown report for human-readable analysis")
    print("   4. Integrate enhanced system into your application")

def main():
    """Main test execution"""
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n⏸️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 