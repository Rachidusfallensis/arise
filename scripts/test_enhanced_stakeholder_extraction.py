#!/usr/bin/env python3
"""
Test script for enhanced stakeholder extraction from technical documents
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.enhanced_stakeholder_extractor import EnhancedStakeholderExtractor
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_with_sample_text():
    """Test with a sample technical document text"""
    
    sample_text = """
    The CYDERCO Cybersecurity Operations Center implements a comprehensive threat detection and response system. 
    
    The SOC Analysts are responsible for monitoring security events and investigating potential incidents. 
    The Network Engineers maintain the network infrastructure and ensure proper connectivity. 
    The Security Manager oversees the entire security operations and coordinates with external teams.
    
    The Database Administrator manages the central repository and ensures data integrity. 
    The System Administrator handles server maintenance and system updates.
    The Incident Response Team performs rapid containment and remediation activities.
    
    End Users access the system through authenticated interfaces. The IT Department provides technical support.
    The Compliance Officer ensures adherence to regulatory requirements. 
    The Network Administrator configures firewall rules and network policies.
    
    The DevOps Engineer automates deployment processes and manages CI/CD pipelines.
    External Vendors provide specialized security services and threat intelligence.
    The Quality Assurance Team validates system functionality and performance.
    
    The Project Manager coordinates development activities and stakeholder communications.
    Security Engineers design and implement security controls and monitoring capabilities.
    Business Users require seamless access to critical business applications.
    """
    
    print("🚀 Testing Enhanced Stakeholder Extraction")
    print("=" * 60)
    
    # Initialize the extractor
    extractor = EnhancedStakeholderExtractor()
    
    # Extract stakeholders
    stakeholders = extractor.extract_stakeholders_from_text(sample_text, "technical")
    
    # Display results
    print(f"\n📊 EXTRACTION RESULTS")
    print(f"Total Stakeholders Found: {len(stakeholders)}")
    print("-" * 40)
    
    for stakeholder_id, stakeholder in stakeholders.items():
        print(f"\n🎯 {stakeholder_id}: {stakeholder['name']}")
        print(f"   Type: {stakeholder['type']}")
        print(f"   Role: {stakeholder['role']}")
        print(f"   Influence: {stakeholder['influence']}")
        print(f"   Phase: {stakeholder['phase']}")
        print(f"   Confidence: {stakeholder['extraction_confidence']:.2f}")
        print(f"   Mentions: {stakeholder['mentions_count']}")
        
        if stakeholder['interests']:
            print(f"   Interests: {', '.join(stakeholder['interests'])}")
        
        if stakeholder['responsibilities']:
            print(f"   Responsibilities: {', '.join(stakeholder['responsibilities'])}")
        
        if stakeholder['requirements']:
            print(f"   Requirements: {', '.join(stakeholder['requirements'])}")
    
    # Get statistics
    stats = extractor.get_extraction_statistics(stakeholders)
    
    print(f"\n📈 EXTRACTION STATISTICS")
    print("-" * 40)
    print(f"Total Stakeholders: {stats['total_stakeholders']}")
    print(f"Average Confidence: {stats['average_confidence']:.2f}")
    print(f"Total Mentions: {stats['total_mentions']}")
    print(f"Stakeholders with Requirements: {stats['stakeholders_with_requirements']}")
    print(f"Stakeholders with Responsibilities: {stats['stakeholders_with_responsibilities']}")
    
    print(f"\n📋 BY TYPE:")
    for stakeholder_type, count in stats['by_type'].items():
        print(f"   {stakeholder_type}: {count}")
    
    print(f"\n🎯 BY INFLUENCE:")
    for influence, count in stats['by_influence'].items():
        print(f"   {influence}: {count}")
    
    print(f"\n🏗️ BY ARCADIA PHASE:")
    for phase, count in stats['by_phase'].items():
        print(f"   {phase}: {count}")
    
    # Export to JSON for further analysis
    output_file = "stakeholder_extraction_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "stakeholders": stakeholders,
            "statistics": stats
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results exported to: {output_file}")

def test_with_real_document():
    """Test with a real document if available"""
    
    # Check if there are example documents
    examples_dir = project_root / "data" / "examples"
    
    if examples_dir.exists():
        for doc_file in examples_dir.glob("*.md"):
            print(f"\n🔍 Testing with real document: {doc_file.name}")
            print("-" * 50)
            
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                extractor = EnhancedStakeholderExtractor()
                stakeholders = extractor.extract_stakeholders_from_text(content, "technical")
                
                print(f"Found {len(stakeholders)} stakeholders in {doc_file.name}")
                
                # Show top 5 stakeholders
                for i, (stakeholder_id, stakeholder) in enumerate(stakeholders.items()):
                    if i >= 5:  # Limit to top 5
                        break
                    print(f"   {stakeholder_id}: {stakeholder['name']} ({stakeholder['type']})")
                
                if len(stakeholders) > 5:
                    print(f"   ... and {len(stakeholders) - 5} more")
                
            except Exception as e:
                print(f"Error processing {doc_file.name}: {e}")
    else:
        print("No example documents found to test with.")

def test_stakeholder_patterns():
    """Test specific stakeholder pattern recognition"""
    
    test_patterns = [
        "The Network Administrator configures the firewall rules.",
        "SOC Analysts monitor security events continuously.",
        "Database Administrator is responsible for data backup procedures.",
        "The Security Manager oversees incident response activities.",
        "DevOps Engineers automate the deployment process.",
        "End Users access the system through web interfaces.",
        "Quality Assurance Team validates all system components.",
        "The IT Department provides technical support to users.",
        "External Vendors supply threat intelligence feeds.",
        "Business Analysts define functional requirements."
    ]
    
    print(f"\n🧪 PATTERN RECOGNITION TEST")
    print("=" * 50)
    
    extractor = EnhancedStakeholderExtractor()
    
    for i, text in enumerate(test_patterns, 1):
        print(f"\n{i}. Testing: '{text}'")
        stakeholders = extractor.extract_stakeholders_from_text(text, "technical")
        
        if stakeholders:
            for stakeholder_id, stakeholder in stakeholders.items():
                print(f"   ✅ Found: {stakeholder['name']} (Type: {stakeholder['type']}, Confidence: {stakeholder['extraction_confidence']:.2f})")
        else:
            print("   ❌ No stakeholders detected")

def main():
    """Main test function"""
    print("🎯 Enhanced Stakeholder Extraction Test Suite")
    print("=" * 60)
    
    # Test 1: Sample text
    test_with_sample_text()
    
    # Test 2: Pattern recognition
    test_stakeholder_patterns()
    
    # Test 3: Real documents
    test_with_real_document()
    
    print(f"\n✅ All tests completed!")
    print("Check the generated 'stakeholder_extraction_results.json' for detailed results.")

if __name__ == "__main__":
    main() 