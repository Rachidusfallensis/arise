#!/usr/bin/env python3
"""
Performance Analysis Script for ARCADIA RAG System

This script analyzes the performance characteristics of the requirements generation process
and provides insights into timing bottlenecks.
"""

import time
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.core.rag_system import SAFEMBSERAGSystem
from config import arcadia_config

def analyze_generation_performance():
    """Analyze performance of requirements generation process."""
    
    print("🔍 ARCADIA RAG System Performance Analysis")
    print("=" * 50)
    
    # Initialize system
    print("📊 Initializing system...")
    start_time = time.time()
    rag_system = SAFEMBSERAGSystem()
    init_time = time.time() - start_time
    print(f"✅ System initialized in {init_time:.2f} seconds")
    
    # Test text
    test_proposal = """
    # Smart Transportation System
    
    ## Objectives
    1. Develop real-time traffic management system
    2. Implement AI-based optimization algorithms
    3. Create stakeholder interfaces for city operators
    
    ## Stakeholders
    - Traffic Control Operators: Monitor traffic flow
    - City Planners: Strategic infrastructure planning
    - Emergency Services: Priority routing capabilities
    
    ## Requirements
    - The system shall process sensor data in real-time
    - Response time must be under 2 seconds
    - System availability shall exceed 99.9%
    """
    
    # Test different configurations
    test_configs = [
        {"phase": "operational", "types": ["functional"], "name": "Single Phase, Single Type"},
        {"phase": "operational", "types": ["functional", "non_functional"], "name": "Single Phase, Multiple Types"},
        {"phase": "all", "types": ["functional"], "name": "All Phases, Single Type"},
        {"phase": "all", "types": ["functional", "non_functional"], "name": "All Phases, Multiple Types"},
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n🧪 Testing: {config['name']}")
        print(f"   Phase: {config['phase']}, Types: {config['types']}")
        
        start_time = time.time()
        
        try:
            generation_result = rag_system.generate_requirements_from_proposal(
                test_proposal, 
                config['phase'], 
                config['types']
            )
            
            duration = time.time() - start_time
            stats = generation_result.get('statistics', {})
            total_reqs = stats.get('total_requirements', 0)
            
            result = {
                "config": config['name'],
                "duration": duration,
                "total_requirements": total_reqs,
                "avg_per_requirement": duration / max(1, total_reqs),
                "phases": len(generation_result.get('requirements', {})),
                "types": len(config['types'])
            }
            
            results.append(result)
            
            print(f"   ✅ Completed in {duration:.1f}s")
            print(f"   📊 Generated {total_reqs} requirements")
            print(f"   ⚡ {duration/total_reqs:.1f}s per requirement")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            continue
    
    # Analysis
    print(f"\n📈 Performance Analysis Summary")
    print("=" * 50)
    
    if results:
        fastest = min(results, key=lambda x: x['duration'])
        slowest = max(results, key=lambda x: x['duration'])
        
        print(f"🏃 Fastest: {fastest['config']} - {fastest['duration']:.1f}s")
        print(f"🐌 Slowest: {slowest['config']} - {slowest['duration']:.1f}s")
        print(f"📊 Speed Factor: {slowest['duration'] / fastest['duration']:.1f}x slower")
        
        avg_duration = sum(r['duration'] for r in results) / len(results)
        avg_reqs = sum(r['total_requirements'] for r in results) / len(results)
        
        print(f"\n📊 Average Metrics:")
        print(f"   Duration: {avg_duration:.1f}s ({avg_duration/60:.1f} min)")
        print(f"   Requirements: {avg_reqs:.1f}")
        print(f"   Per Requirement: {avg_duration/avg_reqs:.1f}s")
        
        # Performance recommendations
        print(f"\n💡 Performance Recommendations:")
        print(f"   • Single phase generation is {fastest['duration']:.1f}s faster")
        print(f"   • Consider limiting phases for faster prototyping")
        print(f"   • Multiple requirement types add ~{(slowest['duration'] - fastest['duration'])/2:.1f}s per type")
    
    print(f"\n🎯 Optimization Tips:")
    print(f"   • Use specific phases instead of 'all' for faster generation")
    print(f"   • Start with functional requirements only for quick testing")
    print(f"   • Network latency to Ollama affects overall performance")
    print(f"   • Model size (gemma:7b) impacts generation speed")

if __name__ == "__main__":
    analyze_generation_performance() 