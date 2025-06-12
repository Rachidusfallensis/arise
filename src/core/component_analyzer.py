import re
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class ComponentMention:
    """Represents a specific component mentioned in the proposal"""
    name: str
    type: str  # 'ai', 'database', 'interface', 'security', 'infrastructure', etc.
    context: str  # Surrounding context where it was mentioned
    confidence: float  # 0.0 to 1.0
    arcadia_phase: str  # Which ARCADIA phase it's most relevant to


class ComponentAnalyzer:
    """
    Analyzes proposal text to identify specific components that should generate
    targeted requirements rather than generic ones
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_component_patterns()
    
    def _initialize_component_patterns(self):
        """Initialize patterns for detecting specific components"""
        
        # AI/ML components
        self.ai_patterns = {
            "machine learning model": ["ml model", "machine learning", "ai model", "neural network"],
            "ai algorithm": ["algorithm", "ai algorithm", "classification", "prediction model"],
            "data processing": ["data processing", "data analysis", "preprocessing", "feature extraction"],
            "natural language processing": ["nlp", "text analysis", "language processing", "text mining"],
            "anomaly detection": ["anomaly detection", "outlier detection", "behavior analysis"],
            "threat detection": ["threat detection", "attack detection", "intrusion detection"]
        }
        
        # Database and storage components
        self.database_patterns = {
            "database": ["database", "db", "postgresql", "mysql", "mongodb", "elasticsearch"],
            "data warehouse": ["data warehouse", "warehouse", "data lake", "big data"],
            "storage system": ["storage", "file system", "blob storage", "object storage"],
            "backup system": ["backup", "backup system", "data backup", "recovery system"]
        }
        
        # Interface components
        self.interface_patterns = {
            "api": ["api", "rest api", "web api", "microservice", "endpoint"],
            "user interface": ["ui", "user interface", "frontend", "web interface", "dashboard"],
            "web service": ["web service", "service", "microservice", "web api"],
            "integration interface": ["integration", "connector", "adapter", "bridge"]
        }
        
        # Security components
        self.security_patterns = {
            "authentication system": ["authentication", "auth", "login", "identity management"],
            "authorization system": ["authorization", "access control", "permissions", "rbac"],
            "encryption": ["encryption", "crypto", "cryptographic", "cipher"],
            "security monitoring": ["security monitoring", "siem", "security analytics"],
            "firewall": ["firewall", "network security", "perimeter security"],
            "intrusion detection": ["ids", "intrusion detection", "hids", "nids"]
        }
        
        # Infrastructure components
        self.infrastructure_patterns = {
            "server": ["server", "compute", "virtual machine", "container"],
            "network": ["network", "networking", "network infrastructure", "connectivity"],
            "load balancer": ["load balancer", "load balancing", "traffic distribution"],
            "monitoring system": ["monitoring", "observability", "telemetry", "metrics"],
            "logging system": ["logging", "log management", "audit trail"],
            "deployment system": ["deployment", "ci/cd", "pipeline", "orchestration"]
        }
        
        # Cybersecurity-specific components
        self.cybersecurity_patterns = {
            "soc platform": ["soc", "security operations center", "soc platform"],
            "cyber threat intelligence": ["cti", "threat intelligence", "intelligence feed"],
            "incident response": ["incident response", "ir", "incident management"],
            "vulnerability scanner": ["vulnerability scanner", "vuln scanner", "security scanner"],
            "penetration testing": ["penetration testing", "pentest", "security testing"],
            "forensic tools": ["forensics", "digital forensics", "forensic analysis"]
        }
        
        # Combine all patterns
        self.component_patterns = {
            "ai": self.ai_patterns,
            "database": self.database_patterns,
            "interface": self.interface_patterns,
            "security": self.security_patterns,
            "infrastructure": self.infrastructure_patterns,
            "cybersecurity": self.cybersecurity_patterns
        }
        
        # ARCADIA phase mapping for components
        self.phase_mapping = {
            "ai": ["system", "logical"],
            "database": ["logical", "physical"],
            "interface": ["system", "logical"],
            "security": ["operational", "system", "logical", "physical"],
            "infrastructure": ["physical"],
            "cybersecurity": ["operational", "system", "logical"]
        }
    
    def analyze_components(self, proposal_text: str) -> List[ComponentMention]:
        """
        Analyze proposal text to identify specific components mentioned
        
        Args:
            proposal_text: The full proposal text
            
        Returns:
            List of ComponentMention objects for identified components
        """
        components = []
        text_lower = proposal_text.lower()
        
        for component_type, patterns in self.component_patterns.items():
            for component_name, keywords in patterns.items():
                confidence = self._calculate_component_confidence(text_lower, keywords)
                
                if confidence > 0.3:  # Threshold for component detection
                    context = self._extract_component_context(proposal_text, keywords)
                    
                    # Determine most relevant ARCADIA phase
                    primary_phase = self._determine_primary_phase(component_type, context)
                    
                    components.append(ComponentMention(
                        name=component_name,
                        type=component_type,
                        context=context,
                        confidence=confidence,
                        arcadia_phase=primary_phase
                    ))
        
        # Sort by confidence and remove duplicates
        components = self._deduplicate_components(components)
        return sorted(components, key=lambda x: x.confidence, reverse=True)
    
    def _calculate_component_confidence(self, text: str, keywords: List[str]) -> float:
        """Calculate confidence that a component is mentioned based on keyword matches"""
        matches = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            if keyword in text:
                matches += 1
        
        # Base confidence from keyword matches
        keyword_confidence = matches / total_keywords
        
        # Boost confidence for exact matches of primary keywords
        primary_keyword = keywords[0] if keywords else ""
        if primary_keyword in text:
            keyword_confidence += 0.3
        
        # Check for contextual indicators that suggest technical components
        technical_indicators = ["system", "component", "module", "service", "platform", "tool"]
        for indicator in technical_indicators:
            if any(f"{indicator}" in text and keyword in text for keyword in keywords[:2]):
                keyword_confidence += 0.2
                break
        
        return min(keyword_confidence, 1.0)
    
    def _extract_component_context(self, text: str, keywords: List[str]) -> str:
        """Extract surrounding context for component mentions"""
        sentences = text.split('.')
        context_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords[:3]):  # Check primary keywords
                context_sentences.append(sentence.strip())
        
        return '. '.join(context_sentences[:3])  # Limit to 3 sentences
    
    def _determine_primary_phase(self, component_type: str, context: str) -> str:
        """Determine the primary ARCADIA phase for a component"""
        phases = self.phase_mapping.get(component_type, ["system"])
        
        # Analyze context for phase-specific keywords
        context_lower = context.lower()
        phase_keywords = {
            "operational": ["stakeholder", "need", "process", "workflow", "user", "business"],
            "system": ["function", "behavior", "service", "capability", "interface"],
            "logical": ["architecture", "component", "design", "allocation", "structure"],
            "physical": ["implementation", "deployment", "hardware", "software", "infrastructure"]
        }
        
        phase_scores = {}
        for phase in phases:
            keywords = phase_keywords.get(phase, [])
            score = sum(1 for keyword in keywords if keyword in context_lower)
            phase_scores[phase] = score
        
        # Return phase with highest score, or first available phase
        if phase_scores:
            return max(phase_scores.keys(), key=lambda p: phase_scores[p])
        return phases[0]
    
    def _deduplicate_components(self, components: List[ComponentMention]) -> List[ComponentMention]:
        """Remove duplicate or overlapping component mentions"""
        unique_components = []
        seen_names = set()
        
        for component in components:
            # Check for similar names (fuzzy matching)
            is_duplicate = False
            for seen_name in seen_names:
                if self._names_similar(component.name, seen_name):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_components.append(component)
                seen_names.add(component.name)
        
        return unique_components
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two component names are similar (indicating duplicates)"""
        # Simple similarity check - more sophisticated methods could be used
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        # Consider similar if more than 50% overlap
        return len(intersection) / len(union) > 0.5
    
    def generate_component_specific_prompts(self, components: List[ComponentMention], phase: str) -> List[str]:
        """
        Generate component-specific prompt additions for requirement generation
        
        Args:
            components: List of identified components
            phase: Target ARCADIA phase
            
        Returns:
            List of prompt additions for specific components
        """
        relevant_components = [c for c in components if c.arcadia_phase == phase or phase == "all"]
        
        if not relevant_components:
            return []
        
        prompts = []
        for component in relevant_components[:5]:  # Limit to top 5 components
            prompt_addition = f"""
For the {component.name} ({component.type}):
- Generate specific requirements addressing this component's functionality
- Consider its context: {component.context[:200]}...
- Focus on {phase} phase concerns for this component type
"""
            prompts.append(prompt_addition)
        
        return prompts
    
    def get_component_requirements_focus(self, components: List[ComponentMention], phase: str) -> str:
        """
        Generate focused requirements guidance based on identified components
        """
        relevant_components = [c for c in components if c.arcadia_phase == phase or phase == "all"]
        
        if not relevant_components:
            return "Generate general requirements for the system."
        
        component_types = set(c.type for c in relevant_components)
        component_names = [c.name for c in relevant_components[:5]]
        
        focus_text = f"Focus on generating specific requirements for these identified components: {', '.join(component_names)}. "
        
        if "security" in component_types or "cybersecurity" in component_types:
            focus_text += "Pay special attention to security requirements including authentication, authorization, data protection, and threat detection. "
        
        if "ai" in component_types:
            focus_text += "Include AI/ML specific requirements such as model performance, training data quality, prediction accuracy, and explainability. "
        
        if "database" in component_types:
            focus_text += "Address data management requirements including storage capacity, backup procedures, data integrity, and access patterns. "
        
        if "interface" in component_types:
            focus_text += "Consider interface requirements including API specifications, user experience, integration capabilities, and protocol compliance. "
        
        return focus_text 