#!/usr/bin/env python3
"""
Script de test pour l'extraction avancée de requirements

Ce script démontre les capacités d'analyse linguistique pour identifier:
- Les verbes d'obligation (shall, must, should)
- Les entités système
- Les conditions et contraintes
- Les métriques quantifiables
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.enhanced_requirement_extractor import EnhancedRequirementExtractor, ObligationLevel
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_enhanced_extraction():
    """Test complet de l'extraction avancée"""
    
    print("=" * 80)
    print("TEST D'EXTRACTION AVANCÉE DE REQUIREMENTS")
    print("=" * 80)
    
    # Initialiser l'extracteur
    extractor = EnhancedRequirementExtractor()
    
    # Textes de test avec différents types de requirements
    test_texts = [
        {
            "name": "Système de Transport Intelligent",
            "text": """
The transportation management system shall process traffic data from sensors in real-time.
The system must respond to traffic signal adjustment requests within 2 seconds under normal conditions.
The platform should provide 99.9% availability during peak traffic hours.
When emergency vehicles are detected, the system shall immediately grant priority routing.
The user interface must display traffic status with accuracy of at least 95%.
Storage capacity should be at least 10 TB for historical traffic data.
The monitoring system will generate alerts if response time exceeds 5 seconds.
"""
        },
        {
            "name": "Plateforme de Cybersécurité", 
            "text": """
The cybersecurity platform shall detect anomalies within 5 seconds of occurrence.
The system must encrypt all communications using at least 256-bit encryption.
Response time for threat alerts should be less than 10 seconds under stress conditions.
The monitoring system shall maintain logs with 99.99% availability.
User authentication must require passwords of at least 12 characters.
When critical threats are identified, the system shall automatically isolate affected components.
The security module may implement additional verification steps for high-risk operations.
"""
        },
        {
            "name": "Système d'Automatisation Industrielle",
            "text": """
The automation system shall monitor production line status continuously.
The platform must stop all operations within 0.5 seconds when emergency stop is activated.
Quality control algorithms should achieve accuracy of at least 98% for defect detection.
The system shall generate maintenance alerts 48 hours before predicted equipment failure.
Under normal operating conditions, the system must maintain throughput of at least 1000 units per hour.
Data storage capacity should be sufficient for 5 years of operational history.
If temperature sensors detect values above 85°C, the cooling system will activate automatically.
"""
        }
    ]
    
    # Tester chaque exemple
    for i, test_case in enumerate(test_texts, 1):
        print(f"\n{'-' * 60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'-' * 60}")
        
        # Extraction
        requirements = extractor.extract_enhanced_requirements(test_case['text'])
        
        # Statistiques
        stats = extractor.get_statistics(requirements)
        
        print(f"\n📊 STATISTIQUES:")
        print(f"   • Requirements trouvés: {stats.get('total_requirements', 0)}")
        print(f"   • Confiance moyenne: {stats.get('average_confidence', 0):.2f}")
        print(f"   • Avec métriques: {stats.get('requirements_with_metrics', 0)} ({stats.get('metrics_percentage', 0):.1f}%)")
        
        # Distribution des obligations
        print(f"\n📋 NIVEAUX D'OBLIGATION:")
        obligation_dist = stats.get('obligation_distribution', {})
        for level, count in obligation_dist.items():
            print(f"   • {level}: {count}")
        
        # Contextes des métriques
        metric_contexts = stats.get('metric_contexts', {})
        if metric_contexts:
            print(f"\n📏 CONTEXTES DES MÉTRIQUES:")
            for context, count in metric_contexts.items():
                print(f"   • {context}: {count}")
        
        # Détails des requirements
        print(f"\n📝 REQUIREMENTS DÉTAILLÉS:")
        for j, req in enumerate(requirements, 1):
            print(f"\n   Requirement {j}:")
            print(f"   📄 Texte: {req.text.strip()}")
            print(f"   🔒 Obligation: {req.obligation_level.value} ({req.obligation_verb})")
            print(f"   ⚙️  Confiance: {req.confidence_score:.2f}")
            
            if req.system_entity:
                print(f"   🖥️  Entité: {req.system_entity}")
            
            if req.action:
                print(f"   ▶️  Action: {req.action}")
            
            if req.conditions:
                print(f"   ❓ Conditions: {', '.join(req.conditions)}")
            
            if req.constraints:
                print(f"   ⚠️  Contraintes: {', '.join(req.constraints)}")
            
            if req.metrics:
                print(f"   📊 Métriques:")
                for metric in req.metrics:
                    print(f"      • {metric['full_match']} (contexte: {metric['context']})")
        
        print(f"\n{'=' * 60}")
    
    # Test de performance avec un texte plus long
    print(f"\n{'-' * 60}")
    print("TEST DE PERFORMANCE - TEXTE LONG")
    print(f"{'-' * 60}")
    
    long_text = """
The comprehensive transportation management system shall integrate multiple subsystems for optimal traffic flow management.
The platform must process real-time data from over 1000 sensors distributed across the urban network within 1 second.
Response time for traffic signal optimization should not exceed 2 seconds under peak traffic conditions.
The system shall maintain 99.95% availability during critical hours (7-9 AM and 5-7 PM).
When emergency vehicles are detected, the system must prioritize their routing within 500 milliseconds.
The user interface should display traffic information with refresh rates of at least 2 Hz.
Data storage capacity must accommodate at least 2 years of historical traffic patterns.
The monitoring subsystem shall generate predictive alerts 15 minutes before potential congestion.
Security encryption must use AES-256 or higher for all inter-system communications.
User authentication should require multi-factor verification for administrative access.
The system will automatically backup critical data every 4 hours to ensure data integrity.
Performance degradation alerts shall be triggered if response times exceed baseline by more than 25%.
"""
    
    import time
    start_time = time.time()
    
    long_requirements = extractor.extract_enhanced_requirements(long_text)
    long_stats = extractor.get_statistics(long_requirements)
    
    extraction_time = time.time() - start_time
    
    print(f"\n⏱️  PERFORMANCE:")
    print(f"   • Temps d'extraction: {extraction_time:.3f} secondes")
    print(f"   • Caractères traités: {len(long_text)}")
    print(f"   • Vitesse: {len(long_text)/extraction_time:.0f} caractères/seconde")
    print(f"   • Requirements trouvés: {long_stats.get('total_requirements', 0)}")
    print(f"   • Métriques identifiées: {sum(len(req.metrics) for req in long_requirements)}")
    
    # Test des patterns spécifiques
    print(f"\n{'-' * 60}")
    print("TEST DES PATTERNS SPÉCIFIQUES")
    print(f"{'-' * 60}")
    
    pattern_tests = [
        ("Verbe SHALL", "The system shall process requests within 1 second."),
        ("Verbe MUST", "The application must encrypt data using 256-bit keys."),
        ("Verbe SHOULD", "The interface should provide user feedback within 2 seconds."),
        ("Verbe MAY", "The system may cache frequently accessed data."),
        ("Verbe WILL", "The platform will send notifications upon completion."),
        ("Métrique Performance", "Response time shall be less than 100 milliseconds."),
        ("Métrique Sécurité", "Password length must be at least 16 characters."),
        ("Métrique Fiabilité", "System availability should exceed 99.9%."),
        ("Condition IF", "If the server load exceeds 80%, the system shall scale automatically."),
        ("Condition WHEN", "When user logs in, the system must verify credentials within 2 seconds."),
        ("Contrainte WITHIN", "The backup process must complete within 30 minutes."),
        ("Contrainte UNDER", "Under normal conditions, throughput should be 1000 requests/second.")
    ]
    
    for test_name, test_text in pattern_tests:
        reqs = extractor.extract_enhanced_requirements(test_text)
        if reqs:
            req = reqs[0]
            print(f"\n✅ {test_name}:")
            print(f"   📄 Texte: {test_text}")
            print(f"   🔒 Obligation: {req.obligation_level.value} ({req.obligation_verb})")
            print(f"   ⚙️  Confiance: {req.confidence_score:.2f}")
            if req.metrics:
                print(f"   📊 Métriques: {len(req.metrics)} trouvée(s)")
            if req.conditions:
                print(f"   ❓ Conditions: {len(req.conditions)} trouvée(s)")
            if req.constraints:
                print(f"   ⚠️  Contraintes: {len(req.constraints)} trouvée(s)")
        else:
            print(f"\n❌ {test_name}: Aucun requirement détecté")
    
    print(f"\n{'=' * 80}")
    print("TESTS TERMINÉS AVEC SUCCÈS! ✅")
    print("=" * 80)

if __name__ == "__main__":
    test_enhanced_extraction() 