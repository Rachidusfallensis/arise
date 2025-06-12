import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CriticalityIndicator:
    """Represents indicators that influence requirement priority"""
    keyword: str
    priority_weight: float  # 0.0 to 1.0
    category: str  # 'safety', 'security', 'regulatory', 'operational', 'enhancement'
    arcadia_relevance: List[str]  # Which ARCADIA phases this applies to


class ARCADIAPriorityAnalyzer:
    """
    Analyzes proposal content to assign ARCADIA-compliant priorities based on:
    - Stakeholder needs analysis
    - Mission-critical functions
    - Regulatory/compliance requirements
    - System safety requirements
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_criticality_indicators()
    
    def _initialize_criticality_indicators(self):
        """Initialize criticality indicators with weights and categories"""
        self.criticality_indicators = {
            "MUST": [
                CriticalityIndicator("safety-critical", 1.0, "safety", ["operational", "system"]),
                CriticalityIndicator("mission-critical", 1.0, "operational", ["operational", "system"]),
                CriticalityIndicator("regulatory compliance", 1.0, "regulatory", ["operational", "system", "logical"]),
                CriticalityIndicator("security-critical", 1.0, "security", ["system", "logical"]),
                CriticalityIndicator("data protection", 0.9, "security", ["system", "logical"]),
                CriticalityIndicator("fail-safe", 0.9, "safety", ["system", "logical"]),
                CriticalityIndicator("backup", 0.9, "operational", ["system", "logical"]),
                CriticalityIndicator("recovery", 0.9, "operational", ["system", "logical"]),
                CriticalityIndicator("emergency", 0.9, "safety", ["operational", "system"]),
                CriticalityIndicator("mandatory", 0.9, "regulatory", ["operational", "system", "logical"]),
                CriticalityIndicator("required by law", 0.9, "regulatory", ["operational", "system", "logical"]),
                CriticalityIndicator("core function", 0.8, "operational", ["system", "logical"]),
                CriticalityIndicator("essential", 0.8, "operational", ["operational", "system"]),
                CriticalityIndicator("critical path", 0.8, "operational", ["system", "logical"]),
                CriticalityIndicator("business continuity", 0.8, "operational", ["operational", "system"])
            ],
            "SHOULD": [
                CriticalityIndicator("important", 0.7, "operational", ["operational", "system"]),
                CriticalityIndicator("performance", 0.7, "operational", ["system", "logical"]),
                CriticalityIndicator("scalability", 0.7, "operational", ["system", "logical"]),
                CriticalityIndicator("usability", 0.6, "operational", ["system", "logical"]),
                CriticalityIndicator("maintainability", 0.6, "operulatory", ["logical", "physical"]),
                CriticalityIndicator("reliability", 0.6, "operational", ["system", "logical"]),
                CriticalityIndicator("stakeholder need", 0.6, "operational", ["operational", "system"]),
                CriticalityIndicator("best practice", 0.5, "regulatory", ["system", "logical"]),
                CriticalityIndicator("industry standard", 0.5, "regulatory", ["system", "logical"]),
                CriticalityIndicator("recommended", 0.5, "operational", ["operational", "system"])
            ],
            "COULD": [
                CriticalityIndicator("enhancement", 0.4, "operational", ["system", "logical"]),
                CriticalityIndicator("nice-to-have", 0.4, "operational", ["operational", "system"]),
                CriticalityIndicator("optimization", 0.4, "operational", ["system", "logical"]),
                CriticalityIndicator("convenience", 0.3, "operational", ["system", "logical"]),
                CriticalityIndicator("future", 0.3, "operational", ["operational", "system"]),
                CriticalityIndicator("optional", 0.3, "operational", ["operational", "system"]),
                CriticalityIndicator("desirable", 0.3, "operational", ["operational", "system"]),
                CriticalityIndicator("potential", 0.2, "operational", ["operational", "system"]),
                CriticalityIndicator("if time permits", 0.2, "operational", ["operational", "system"]),
                CriticalityIndicator("if resources available", 0.2, "operational", ["operational", "system"])
            ]
        }
        
        # Component-specific priority mappings
        self.component_priority_mapping = {
            "ai model": 0.8,
            "machine learning": 0.8,
            "algorithm": 0.75,
            "database": 0.7,
            "api": 0.65,
            "interface": 0.6,
            "ui": 0.5,
            "dashboard": 0.55,
            "frontend": 0.5,
            "backend": 0.7,
            "infrastructure": 0.75,
            "network": 0.7,
            "storage": 0.65,
            "backup": 0.8,  # High priority for data safety
            "recovery": 0.85,  # High priority for business continuity
        }
    
    def analyze_requirement_priority(self, 
                                   requirement_text: str, 
                                   context: str, 
                                   phase: str,
                                   stakeholder_needs: Optional[List[str]] = None) -> Tuple[str, float, Dict]:
        """
        Analyze requirement text and context to assign appropriate priority
        
        Args:
            requirement_text: The requirement description
            context: Surrounding context from proposal
            phase: ARCADIA phase (operational, system, logical, physical)
            stakeholder_needs: List of identified stakeholder needs
            
        Returns:
            Tuple of (priority_level, confidence_score, analysis_details)
        """
        combined_text = f"{requirement_text} {context}".lower()
        stakeholder_context = " ".join(stakeholder_needs or []).lower()
        
        analysis_details: Dict = {
            "indicators_found": [],
            "stakeholder_alignment": 0.0,
            "component_specificity": 0.0,
            "regulatory_compliance": 0.0,
            "safety_criticality": 0.0,
            "phase_relevance": 0.0
        }
        
        # 1. Analyze criticality indicators
        priority_scores = {"MUST": 0.0, "SHOULD": 0.0, "COULD": 0.0}
        
        for priority_level, indicators in self.criticality_indicators.items():
            for indicator in indicators:
                if phase in indicator.arcadia_relevance and indicator.keyword in combined_text:
                    priority_scores[priority_level] += indicator.priority_weight
                    analysis_details["indicators_found"].append({
                        "keyword": indicator.keyword,
                        "category": indicator.category,
                        "weight": indicator.priority_weight,
                        "priority": priority_level
                    })
        
                 # 2. Analyze stakeholder alignment
        if stakeholder_needs:
            stakeholder_alignment = self._calculate_stakeholder_alignment(
                requirement_text, stakeholder_context
            )
            analysis_details["stakeholder_alignment"] = stakeholder_alignment
            # High stakeholder alignment increases priority
            if stakeholder_alignment > 0.7:
                priority_scores["MUST"] += 0.3
            elif stakeholder_alignment > 0.4:
                priority_scores["SHOULD"] += 0.2
        
        # 3. Analyze component specificity
        component_score = self._analyze_component_specificity(requirement_text)
        analysis_details["component_specificity"] = component_score
        if component_score > 0.7:
            priority_scores["SHOULD"] += 0.2
        
        # 4. Analyze regulatory/compliance aspects
        regulatory_score = self._analyze_regulatory_compliance(combined_text)
        analysis_details["regulatory_compliance"] = regulatory_score
        if regulatory_score > 0.5:
            priority_scores["MUST"] += regulatory_score * 0.5
        
        # 5. Analyze safety criticality
        safety_score = self._analyze_safety_criticality(combined_text)
        analysis_details["safety_criticality"] = safety_score
        if safety_score > 0.3:
            priority_scores["MUST"] += safety_score * 0.6
        
        # 6. Phase relevance adjustment
        phase_relevance = self._calculate_phase_relevance(requirement_text, phase)
        analysis_details["phase_relevance"] = phase_relevance
        
        # Determine final priority
        max_score = max(priority_scores.values())
        confidence = min(max_score, 1.0)
        
        # Apply minimum thresholds
        if priority_scores["MUST"] >= 0.7:
            return "MUST", confidence, analysis_details
        elif priority_scores["SHOULD"] >= 0.4:
            return "SHOULD", confidence, analysis_details
        else:
            return "COULD", confidence, analysis_details
    
    def _calculate_stakeholder_alignment(self, requirement: str, stakeholder_context: str) -> float:
        """Calculate how well requirement aligns with stakeholder needs"""
        if not stakeholder_context:
            return 0.5  # Neutral if no stakeholder context
        
        requirement_words = set(requirement.lower().split())
        stakeholder_words = set(stakeholder_context.split())
        
        if not requirement_words or not stakeholder_words:
            return 0.5
        
        # Calculate basic word overlap
        intersection = requirement_words.intersection(stakeholder_words)
        base_score = len(intersection) / len(requirement_words.union(stakeholder_words))
        
        # Additional scoring factors
        additional_score = 0.0
        
        # Check for mission-critical alignment
        mission_critical_terms = {
            "mission", "critical", "essential", "core", "primary", "vital",
            "business continuity", "operational", "key", "strategic"
        }
        mission_critical_matches = sum(1 for term in mission_critical_terms 
                                    if term in requirement.lower())
        additional_score += min(mission_critical_matches * 0.1, 0.3)
        
        # Check for stakeholder priority terms
        priority_terms = {
            "must", "shall", "required", "necessary", "mandatory",
            "critical", "essential", "vital", "key", "primary"
        }
        priority_matches = sum(1 for term in priority_terms 
                             if term in requirement.lower())
        additional_score += min(priority_matches * 0.05, 0.2)
        
        # Check for stakeholder impact terms
        impact_terms = {
            "impact", "affect", "influence", "determine", "drive",
            "enable", "support", "facilitate", "ensure", "guarantee"
        }
        impact_matches = sum(1 for term in impact_terms 
                           if term in requirement.lower())
        additional_score += min(impact_matches * 0.05, 0.2)
        
        # Combine scores with weights
        final_score = (base_score * 0.6) + (additional_score * 0.4)
        
        return min(final_score, 1.0)
    
    def _analyze_component_specificity(self, requirement_text: str) -> float:
        """Analyze how specific the requirement is to mentioned components"""
        text_lower = requirement_text.lower()
        specificity_score = 0.0
        
        for component, weight in self.component_priority_mapping.items():
            if component in text_lower:
                specificity_score = max(specificity_score, weight)
        
        # Check for specific technical terms that indicate detailed requirements
        technical_patterns = [
            r'\b\d+\s*(seconds?|minutes?|hours?|ms|milliseconds?)\b',  # Time specifications
            r'\b\d+\s*(gb|mb|kb|bytes?)\b',  # Size specifications
            r'\b\d+\s*(%|percent)\b',  # Percentage specifications
            r'\b(api|protocol|algorithm|interface)\b',  # Technical components
        ]
        
        for pattern in technical_patterns:
            if re.search(pattern, text_lower):
                specificity_score += 0.2
        
        return min(specificity_score, 1.0)
    
    def _analyze_regulatory_compliance(self, text: str) -> float:
        """Analyze regulatory/compliance requirements"""
        regulatory_keywords = {
            # Data Protection & Privacy
            "gdpr": 0.9,
            "hipaa": 0.9,
            "ccpa": 0.9,
            "data protection": 0.85,
            "privacy": 0.8,
            "personal data": 0.85,
            "pii": 0.85,
            "sensitive data": 0.85,
            
            # Security Standards
            "iso 27001": 0.9,
            "nist": 0.9,
            "pci dss": 0.9,
            "security standard": 0.85,
            "cybersecurity": 0.85,
            "information security": 0.85,
            
            # Industry-specific Regulations
            "sox": 0.9,
            "fda": 0.9,
            "fcc": 0.9,
            "aviation": 0.85,
            "medical": 0.85,
            "financial": 0.85,
            
            # General Compliance
            "compliance": 0.8,
            "regulatory": 0.8,
            "audit": 0.75,
            "legal": 0.75,
            "mandatory": 0.8,
            "required by law": 0.8,
            "regulation": 0.8,
            "standard": 0.7,
            "certification": 0.7,
            "accreditation": 0.7
        }
        
        text_lower = text.lower()
        score = 0.0
        matched_keywords = []
        
        # Check for exact matches
        for keyword, weight in regulatory_keywords.items():
            if keyword in text_lower:
                score += weight
                matched_keywords.append(keyword)
        
        # Check for regulatory context
        regulatory_context_terms = [
            "comply with", "meet requirements", "adhere to",
            "in accordance with", "as per", "following",
            "must comply", "shall comply", "required to"
        ]
        
        context_matches = sum(1 for term in regulatory_context_terms 
                            if term in text_lower)
        score += min(context_matches * 0.1, 0.3)
        
        # Check for regulatory impact
        impact_terms = [
            "non-compliance", "violation", "breach",
            "penalty", "fine", "sanction",
            "legal action", "enforcement"
        ]
        
        impact_matches = sum(1 for term in impact_terms 
                           if term in text_lower)
        score += min(impact_matches * 0.15, 0.3)
        
        # Normalize score
        final_score = min(score / 2.0, 1.0)  # Divide by 2 since we have multiple scoring factors
        
        return final_score
    
    def _analyze_safety_criticality(self, text: str) -> float:
        """Analyze safety-critical requirements"""
        safety_keywords = [
            "safety", "critical", "fail-safe", "redundancy", "backup",
            "emergency", "incident", "threat", "vulnerability", "breach",
            "secure", "protection", "recovery", "availability"
        ]
        
        score = 0.0
        for keyword in safety_keywords:
            if keyword in text:
                if keyword in ["safety", "critical", "emergency", "breach"]:
                    score += 0.25  # High weight for critical safety terms
                else:
                    score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_phase_relevance(self, requirement: str, phase: str) -> float:
        """Calculate relevance to specific ARCADIA phase"""
        phase_keywords = {
            "operational": ["stakeholder", "need", "capability", "process", "actor", "scenario"],
            "system": ["function", "interface", "behavior", "system", "service"],
            "logical": ["component", "architecture", "logical", "allocation", "design"],
            "physical": ["implementation", "hardware", "software", "deployment", "physical"]
        }
        
        if phase not in phase_keywords:
            return 0.5
        
        requirement_lower = requirement.lower()
        keywords = phase_keywords[phase]
        
        relevance_count = sum(1 for keyword in keywords if keyword in requirement_lower)
        return min(relevance_count / len(keywords), 1.0)
    
    def generate_priority_rationale(self, priority: str, analysis_details: Dict) -> str:
        """Generate human-readable rationale for priority assignment"""
        rationale_parts = []
        
        # Priority assignment reason
        rationale_parts.append(f"Assigned {priority} priority based on:")
        
        # Indicators found
        if analysis_details["indicators_found"]:
            categories: Dict[str, List[str]] = {}
            for indicator in analysis_details["indicators_found"]:
                cat = indicator["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(indicator["keyword"])
            
            for category, keywords in categories.items():
                rationale_parts.append(f"• {category.title()} indicators: {', '.join(keywords)}")
        
        # Stakeholder alignment
        if analysis_details["stakeholder_alignment"] > 0.7:
            rationale_parts.append("• High alignment with stakeholder needs")
        elif analysis_details["stakeholder_alignment"] > 0.4:
            rationale_parts.append("• Moderate alignment with stakeholder needs")
        
        # Component specificity
        if analysis_details["component_specificity"] > 0.7:
            rationale_parts.append("• Specific technical component requirements")
        
        # Regulatory compliance
        if analysis_details["regulatory_compliance"] > 0.5:
            rationale_parts.append("• Regulatory/compliance requirements identified")
        
        # Safety criticality
        if analysis_details["safety_criticality"] > 0.3:
            rationale_parts.append("• Safety-critical functionality identified")
        
        return " ".join(rationale_parts) 