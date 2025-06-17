#!/usr/bin/env python3
"""
Test script for Logical and Physical Architecture integration in ARCADIA system
"""

import sys
import os
from pathlib import Path
import logging
import time

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem
from src.core.logical_architecture_extractor import LogicalArchitectureExtractor
from src.core.physical_architecture_extractor import PhysicalArchitectureExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_example_proposal():
    """Test proposal for Smart Transportation System"""
    return """
# Smart Transportation Management System

## Project Overview
Development of an intelligent transportation management system for smart city infrastructure using Model-Based Systems Engineering (MBSE) approach with ARCADIA methodology.

## System Objectives
1. Design integrated traffic management system with real-time optimization
2. Implement predictive analytics for traffic flow management
3. Create operator interface for traffic control center
4. Establish quality monitoring framework

## Stakeholders
- Traffic Control Operators: Monitor and manage traffic flow patterns
- City Planners: Strategic planning and infrastructure development
- Emergency Services: Priority routing and incident response coordination
- Citizens: End users expecting efficient transportation services

## Operational Capabilities
- Real-time traffic monitoring and data collection
- Dynamic traffic signal optimization
- Incident detection and response coordination
- Emergency vehicle priority management
- Historical data analysis and reporting

## System Functions
- Data Processing Engine: Collect and process sensor data from 500+ traffic sensors
- Traffic Optimization Algorithm: Calculate optimal signal timing patterns
- Operator Dashboard: Provide real-time monitoring and control interface
- Emergency Response Module: Handle priority routing for emergency vehicles
- Data Storage System: Store traffic patterns and historical data

## Logical Architecture
- Traffic Data Processing Component: Central processing unit for sensor data
- Signal Control Logic: Algorithms for traffic light management
- Communication Interface: Data exchange with external systems
- User Interface Layer: Operator control and monitoring functions
- Database Management: Data persistence and retrieval services

## Physical Implementation
- High-performance servers with redundant processing capabilities
- Network infrastructure with fiber optic connections
- Traffic signal controllers with wireless communication
- Mobile applications for field operators
- Data center with backup power and cooling systems

## Technical Requirements
- The system shall process traffic data from 500+ sensors in real-time
- Response time for traffic signal adjustments must be under 2 seconds
- System availability shall be 99.9% or higher
- Integration with emergency services dispatch systems is mandatory
- Data encryption required for all communications
- Compliance with smart city infrastructure standards

## Performance Constraints
- Maximum response latency: 2 seconds for signal adjustments
- Data processing throughput: 10,000 events per second
- Network bandwidth: minimum 1 Gbps for data transmission
- Storage capacity: 10 TB for historical data retention
- Backup and recovery: maximum 30 seconds downtime
"""

def test_logical_physical_integration():
    """Test the integration of logical and physical architecture extractors"""
    
    print("🧪 Testing Logical and Physical Architecture Integration")
    print("=" * 60)
    
    try:
        # Initialize the enhanced system
        print("📋 1. Initializing Enhanced Structured RAG System...")
        start_time = time.time()
        
        enhanced_system = EnhancedStructuredRAGSystem()
        
        init_time = time.time() - start_time
        print(f"   ✅ System initialized in {init_time:.2f} seconds")
        
        # Test proposal
        proposal_text = test_example_proposal()
        print(f"📄 2. Using test proposal ({len(proposal_text)} characters)")
        
        # Generate enhanced requirements with all phases
        print("🔧 3. Generating enhanced requirements with all ARCADIA phases...")
        generation_start = time.time()
        
        results = enhanced_system.generate_enhanced_requirements_from_proposal(
            proposal_text=proposal_text,
            target_phase="all",  # This should now include logical and physical
            requirement_types=["functional", "non_functional"],
            enable_structured_analysis=True,
            enable_cross_phase_analysis=True
        )
        
        generation_time = time.time() - generation_start
        print(f"   ✅ Generation completed in {generation_time:.2f} seconds")
        
        # Analyze results
        print("\n📊 4. Analyzing Results:")
        print("-" * 40)
        
        # Check traditional requirements
        traditional_reqs = results.get('traditional_requirements', {})
        total_traditional = sum(
            len(phase_reqs.get(req_type, [])) 
            for phase_reqs in traditional_reqs.get('requirements', {}).values()
            for req_type in ['functional', 'non_functional']
        )
        print(f"   📝 Traditional Requirements: {total_traditional}")
        
        # Check structured analysis
        structured_analysis = results.get('structured_analysis')
        if structured_analysis:
            print("   🏗️  Structured Analysis:")
            
            # Operational phase
            if structured_analysis.operational_analysis:
                op_actors = len(structured_analysis.operational_analysis.actors)
                op_capabilities = len(structured_analysis.operational_analysis.capabilities)
                print(f"      🎭 Operational: {op_actors} actors, {op_capabilities} capabilities")
            
            # System phase
            if structured_analysis.system_analysis:
                sys_functions = len(structured_analysis.system_analysis.functions)
                sys_capabilities = len(structured_analysis.system_analysis.capabilities)
                print(f"      🏗️  System: {sys_functions} functions, {sys_capabilities} capabilities")
            
            # Logical phase (NEW!)
            if structured_analysis.logical_architecture:
                log_components = len(structured_analysis.logical_architecture.components)
                log_functions = len(structured_analysis.logical_architecture.functions)
                log_interfaces = len(structured_analysis.logical_architecture.interfaces)
                print(f"      🧩 Logical: {log_components} components, {log_functions} functions, {log_interfaces} interfaces")
                
                # Show some logical components
                if structured_analysis.logical_architecture.components:
                    print("         Sample Logical Components:")
                    for comp in structured_analysis.logical_architecture.components[:3]:
                        print(f"         - {comp.name} ({comp.component_type})")
            else:
                print("      ❌ Logical Architecture: No data generated")
            
            # Physical phase (NEW!)
            if structured_analysis.physical_architecture:
                phys_components = len(structured_analysis.physical_architecture.components)
                phys_constraints = len(structured_analysis.physical_architecture.constraints)
                phys_functions = len(structured_analysis.physical_architecture.functions)
                print(f"      🔧 Physical: {phys_components} components, {phys_constraints} constraints, {phys_functions} functions")
                
                # Show some physical components
                if structured_analysis.physical_architecture.components:
                    print("         Sample Physical Components:")
                    for comp in structured_analysis.physical_architecture.components[:3]:
                        print(f"         - {comp.name} ({comp.component_type}, {comp.technology_platform})")
            else:
                print("      ❌ Physical Architecture: No data generated")
            
            # Cross-phase analysis
            if structured_analysis.cross_phase_analysis:
                traceability_links = len(structured_analysis.cross_phase_analysis.traceability_links)
                gaps = len(structured_analysis.cross_phase_analysis.gap_analysis)
                print(f"      🔗 Cross-Phase: {traceability_links} traceability links, {gaps} gaps identified")
                
                # Show some traceability links
                if structured_analysis.cross_phase_analysis.traceability_links:
                    print("         Sample Traceability Links:")
                    for link in structured_analysis.cross_phase_analysis.traceability_links[:3]:
                        print(f"         - {link.source_element} → {link.target_element} ({link.relationship_type}, {link.confidence_score:.2f})")
            
        else:
            print("   ❌ No structured analysis generated")
        
        # Enhancement summary
        enhancement_summary = results.get('enhancement_summary', {})
        if enhancement_summary:
            print("\n🎯 5. Enhancement Summary:")
            print("-" * 40)
            phases_analyzed = enhancement_summary.get('phases_analyzed', [])
            print(f"   📊 Phases Analyzed: {', '.join(phases_analyzed)}")
            print(f"   👥 Total Actors: {enhancement_summary.get('total_actors_identified', 0)}")
            print(f"   🎯 Total Capabilities: {enhancement_summary.get('total_capabilities_identified', 0)}")
            print(f"   🧩 Total Components: {enhancement_summary.get('total_components_identified', 0)}")
            print(f"   ⚙️  Total Functions: {enhancement_summary.get('total_functions_identified', 0)}")
            print(f"   🔗 Cross-Phase Links: {enhancement_summary.get('cross_phase_links', 0)}")
        
        # Test structured analysis summary
        print("\n📈 6. Testing Structured Analysis Summary:")
        print("-" * 40)
        
        if hasattr(enhanced_system, 'get_structured_analysis_summary'):
            try:
                summary = enhanced_system.get_structured_analysis_summary(results)
                phases_in_summary = summary.get('phases_analyzed', [])
                print(f"   📊 Summary includes phases: {', '.join(phases_in_summary)}")
                
                extraction_stats = summary.get('extraction_statistics', {})
                for phase, stats in extraction_stats.items():
                    elements = sum(stats.values())
                    print(f"   {phase.title()}: {elements} total elements")
                
            except Exception as e:
                print(f"   ❌ Error getting structured summary: {str(e)}")
        
        # Success indicators
        print("\n✅ 7. Integration Success Indicators:")
        print("-" * 40)
        
        success_indicators = []
        
        # Check if all phases are present
        if structured_analysis:
            if structured_analysis.operational_analysis:
                success_indicators.append("✅ Operational Analysis")
            if structured_analysis.system_analysis:
                success_indicators.append("✅ System Analysis")
            if structured_analysis.logical_architecture:
                success_indicators.append("✅ Logical Architecture")
            if structured_analysis.physical_architecture:
                success_indicators.append("✅ Physical Architecture")
            if structured_analysis.cross_phase_analysis:
                success_indicators.append("✅ Cross-Phase Analysis")
        
        # Check enhancement summary
        if enhancement_summary.get('phases_analyzed'):
            if 'logical' in enhancement_summary['phases_analyzed']:
                success_indicators.append("✅ Logical Phase Integration")
            if 'physical' in enhancement_summary['phases_analyzed']:
                success_indicators.append("✅ Physical Phase Integration")
        
        if success_indicators:
            for indicator in success_indicators:
                print(f"   {indicator}")
        else:
            print("   ❌ No success indicators found")
        
        # Overall assessment
        print(f"\n🎉 Integration Test Complete!")
        print(f"   Total time: {time.time() - start_time:.2f} seconds")
        
        if 'logical' in enhancement_summary.get('phases_analyzed', []) and 'physical' in enhancement_summary.get('phases_analyzed', []):
            print("   🏆 SUCCESS: Logical and Physical Architecture phases are now integrated!")
            return True
        else:
            print("   ⚠️  PARTIAL: Some phases may not be working correctly")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        logger.error(f"Integration test error: {str(e)}", exc_info=True)
        return False

def test_individual_extractors():
    """Test individual extractors separately"""
    
    print("\n🔬 Testing Individual Extractors")
    print("=" * 40)
    
    try:
        # Initialize individual extractors
        from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem
        system = EnhancedStructuredRAGSystem()
        
        logical_extractor = LogicalArchitectureExtractor(system.ollama_client)
        physical_extractor = PhysicalArchitectureExtractor(system.ollama_client)
        
        # Prepare test context
        proposal_text = test_example_proposal()
        context_chunks = system._extract_proposal_context(proposal_text)
        
        print(f"📄 Test context: {len(context_chunks)} chunks")
        
        # Test Logical Extractor
        print("\n🧩 Testing Logical Architecture Extractor:")
        try:
            logical_results = logical_extractor.extract_logical_architecture(
                context_chunks, proposal_text
            )
            
            print(f"   ✅ Components: {len(logical_results.components)}")
            print(f"   ✅ Functions: {len(logical_results.functions)}")
            print(f"   ✅ Interfaces: {len(logical_results.interfaces)}")
            print(f"   ✅ Scenarios: {len(logical_results.scenarios)}")
            
        except Exception as e:
            print(f"   ❌ Logical extractor failed: {str(e)}")
        
        # Test Physical Extractor  
        print("\n🔧 Testing Physical Architecture Extractor:")
        try:
            physical_results = physical_extractor.extract_physical_architecture(
                context_chunks, proposal_text
            )
            
            print(f"   ✅ Components: {len(physical_results.components)}")
            print(f"   ✅ Constraints: {len(physical_results.constraints)}")
            print(f"   ✅ Functions: {len(physical_results.functions)}")
            print(f"   ✅ Scenarios: {len(physical_results.scenarios)}")
            
        except Exception as e:
            print(f"   ❌ Physical extractor failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Individual extractor test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Logical and Physical Architecture Integration Test")
    print("=" * 80)
    
    # Test integration
    success = test_logical_physical_integration()
    
    # Test individual extractors
    test_individual_extractors()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 INTEGRATION SUCCESSFUL: Logical and Physical Architecture phases are now active!")
        print("✅ The Structured ARCADIA Analysis tab should now display all 4 phases")
        print("✅ Users can generate comprehensive ARCADIA methodology analysis")
    else:
        print("⚠️  INTEGRATION INCOMPLETE: Please check the error messages above")
        print("🔧 The system may still work but some phases might not be fully functional")
    
    print("=" * 80) 