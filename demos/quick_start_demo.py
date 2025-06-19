#!/usr/bin/env python3
"""
Quick Start Demo - SAFE MBSE RAG System

A simple demonstration of how to use the SAFE MBSE RAG system programmatically.
This demo shows the basic workflow for requirements generation from project text.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("🚀 SAFE MBSE RAG System - Quick Start Demo")
    print("=" * 50)
    print()
    
    # Sample project proposal
    sample_proposal = """
    # Smart Traffic Management System
    
    ## Project Overview
    Develop an intelligent traffic management system for urban environments
    using the ARCADIA methodology to ensure systematic requirements development.
    
    ## Stakeholders
    - Traffic Control Operators: Monitor and control traffic flow
    - City Planners: Strategic urban development
    - Emergency Services: Priority routing for emergency vehicles
    - Citizens: End users expecting efficient transportation
    
    ## Objectives
    1. Real-time traffic monitoring and optimization
    2. Emergency vehicle priority routing
    3. Integration with city infrastructure
    4. 99.9% system availability
    5. Response time under 2 seconds
    
    ## Scope
    The system will cover downtown area with 50+ intersections,
    integrate with existing traffic infrastructure, and provide
    web-based monitoring interface for operators.
    """
    
    print("📄 Sample Project Proposal:")
    print("-" * 30)
    print(sample_proposal[:200] + "...")
    print()
    
    # Initialize the RAG system
    print("🔧 Initializing SAFE MBSE RAG System...")
    
    try:
        # Try enhanced persistent system first
        from src.core.enhanced_persistent_rag_system import EnhancedPersistentRAGSystem
        rag_system = EnhancedPersistentRAGSystem()
        system_type = "Enhanced Persistent"
        print(f"✅ {system_type} RAG System initialized")
        
    except Exception as e:
        print(f"⚠️  Enhanced system not available: {e}")
        try:
            # Fallback to basic system
            from src.core.rag_system import SAFEMBSERAGSystem
            rag_system = SAFEMBSERAGSystem()
            system_type = "Basic"
            print(f"✅ {system_type} RAG System initialized")
            
        except Exception as basic_error:
            print(f"❌ Failed to initialize RAG system: {basic_error}")
            print("💡 Make sure Ollama is running and models are available")
            return
    
    # Generate requirements
    print("\n🏗️ Generating Requirements using ARCADIA Methodology...")
    print("⏳ This may take a few moments...")
    
    try:
        # Generate requirements for system analysis phase
        results = rag_system.generate_requirements_from_proposal(
            proposal_text=sample_proposal,
            target_phase="system",  # Focus on system analysis
            requirement_types=["functional", "non_functional"]
        )
        
        print("✅ Requirements generated successfully!")
        print()
        
        # Display results
        print("📋 Generated Requirements Summary:")
        print("-" * 40)
        
        requirements = results.get('requirements', {})
        total_count = 0
        
        for phase, phase_reqs in requirements.items():
            print(f"\n🏗️ {phase.upper()} Phase:")
            phase_count = 0
            
            for req_type, reqs in phase_reqs.items():
                if isinstance(reqs, list) and reqs:
                    print(f"  📝 {req_type.title()} Requirements: {len(reqs)}")
                    phase_count += len(reqs)
                    
                    # Show first requirement as example
                    if reqs:
                        first_req = reqs[0]
                        title = first_req.get('title', 'No title')
                        priority = first_req.get('priority', 'SHOULD')
                        print(f"     Example: {title} (Priority: {priority})")
            
            total_count += phase_count
            print(f"  📊 Phase Total: {phase_count} requirements")
        
        print(f"\n🎯 Total Requirements Generated: {total_count}")
        
        # Show stakeholders if available
        stakeholders = results.get('stakeholders', {})
        if stakeholders:
            print(f"\n👥 Stakeholders Identified: {len(stakeholders)}")
            for stakeholder_type, stakeholder_list in stakeholders.items():
                if isinstance(stakeholder_list, list):
                    print(f"  • {stakeholder_type.title()}: {len(stakeholder_list)}")
        
        print()
        print("🎉 Demo completed successfully!")
        print("💡 To explore more features, run: python run_app.py")
        
    except Exception as e:
        print(f"❌ Error generating requirements: {e}")
        print("💡 Check that Ollama is running and models are available")
        print("   Run: ollama list")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("💡 Make sure you're in the project root directory")
        print("   And that all dependencies are installed: pip install -r requirements.txt") 