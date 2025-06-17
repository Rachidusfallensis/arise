import re
import logging
from typing import List, Dict, Set, Tuple, Optional, Any
from collections import defaultdict, Counter
import json

class EnhancedStakeholderExtractor:
    """
    Advanced stakeholder/actor extraction from technical documents
    Designed for MBSE and ARCADIA methodology
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Enhanced stakeholder patterns for technical documents
        self.stakeholder_patterns = {
            # Role-based patterns
            "roles": [
                r"\b([A-Z][a-z]*\s*(?:Engineer|Manager|Analyst|Developer|Administrator|Operator|Architect|Specialist|Lead|Director|Officer|Coordinator|Supervisor|Technician)s?)\b",
                r"\b(System\s*(?:Engineer|Administrator|Analyst|Operator|Manager|Architect)s?)\b",
                r"\b(Software\s*(?:Engineer|Developer|Architect|Analyst|Manager)s?)\b",
                r"\b(Security\s*(?:Engineer|Officer|Analyst|Manager|Administrator)s?)\b",
                r"\b(Network\s*(?:Engineer|Administrator|Analyst|Manager)s?)\b",
                r"\b(Database\s*(?:Administrator|Analyst|Manager|Engineer)s?)\b",
                r"\b(Quality\s*(?:Assurance|Engineer|Manager|Analyst)s?)\b",
                r"\b(Project\s*(?:Manager|Lead|Coordinator)s?)\b",
                r"\b(Product\s*(?:Manager|Owner|Lead)s?)\b",
                r"\b(Business\s*(?:Analyst|Manager|User)s?)\b",
                r"\b(IT\s*(?:Manager|Administrator|Support|Staff)s?)\b"
            ],
            
            # Organizational patterns
            "organizations": [
                r"\b([A-Z][a-z]*\s*(?:Department|Division|Team|Group|Unit|Organization|Agency|Bureau|Office|Service|Company|Corporation|Enterprise)s?)\b",
                r"\b((?:IT|HR|Finance|Marketing|Sales|Legal|Security|Operations|Development|Engineering|Quality|Testing|Support|Maintenance|Management)\s*(?:Department|Team|Group|Division|Unit)s?)\b",
                r"\b(End\s*Users?)\b",
                r"\b(Customers?)\b",
                r"\b(Clients?)\b",
                r"\b(Vendors?)\b",
                r"\b(Suppliers?)\b",
                r"\b(Third[- ]party\s*(?:providers?|vendors?|services?)?)\b"
            ],
            
            # Actor patterns (for use cases and scenarios)
            "actors": [
                r"\b((?:Primary|Secondary|External|Internal|System|Human|Automated)\s*(?:Actor|User|Agent|Entity)s?)\b",
                r"\b((?:Authorized|Unauthorized|Authenticated|Guest|Anonymous)\s*(?:User|Actor|Person)s?)\b",
                r"\b((?:Super|Power|Regular|Normal|Standard|Basic)\s*(?:User|Admin|Administrator)s?)\b"
            ],
            
            # Specific technical roles
            "technical_roles": [
                r"\b(SOC\s*(?:Analyst|Engineer|Manager|Operator)s?)\b",
                r"\b(DevOps\s*(?:Engineer|Specialist|Team)s?)\b",
                r"\b(DataBase\s*(?:Administrator|DBA)s?)\b",
                r"\b(System\s*(?:Admin|Administrator)s?)\b",
                r"\b(Network\s*(?:Admin|Administrator)s?)\b",
                r"\b(Security\s*(?:Admin|Administrator)s?)\b",
                r"\b(Incident\s*(?:Response|Handler|Manager)s?)\b",
                r"\b(Vulnerability\s*(?:Analyst|Manager)s?)\b",
                r"\b(Threat\s*(?:Analyst|Hunter)s?)\b",
                r"\b(Forensic\s*(?:Analyst|Investigator)s?)\b",
                r"\b(Compliance\s*(?:Officer|Manager|Analyst)s?)\b",
                r"\b(Risk\s*(?:Manager|Analyst|Officer)s?)\b"
            ],
            
            # Contextual indicators
            "contextual": [
                r"\b(?:The|A|An)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is responsible for|manages|oversees|handles|performs|executes|monitors|maintains|operates|controls|supervises)\b",
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:will|shall|must|should|needs? to|has to|is required to)\s+(?:perform|execute|manage|monitor|maintain|operate|control|supervise|handle|process|analyze|review)\b",
                r"\b(?:Performed by|Executed by|Managed by|Supervised by|Controlled by|Operated by|Handled by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:has|have)\s+(?:the responsibility|responsibility|access|privileges|permissions|authority|capability)\b"
            ]
        }
        
        # Stakeholder categories for classification
        self.stakeholder_categories = {
            "technical": ["engineer", "developer", "administrator", "analyst", "architect", "specialist", "technician", "operator"],
            "management": ["manager", "director", "lead", "supervisor", "coordinator", "officer", "executive"],
            "business": ["user", "customer", "client", "business", "product", "sales", "marketing"],
            "security": ["security", "soc", "incident", "forensic", "threat", "vulnerability", "compliance", "risk"],
            "operations": ["operations", "devops", "maintenance", "support", "service", "helpdesk"],
            "external": ["vendor", "supplier", "third-party", "contractor", "partner", "regulatory", "auditor"]
        }
        
        # Common stakeholder interest patterns
        self.interest_patterns = {
            "security": ["security", "protection", "threat", "vulnerability", "risk", "compliance", "audit", "incident"],
            "performance": ["performance", "speed", "efficiency", "optimization", "scalability", "response time"],
            "functionality": ["functionality", "features", "capabilities", "requirements", "specifications"],
            "usability": ["usability", "user experience", "interface", "accessibility", "ease of use"],
            "reliability": ["reliability", "availability", "uptime", "stability", "robustness", "fault tolerance"],
            "maintenance": ["maintenance", "support", "updates", "patches", "monitoring", "troubleshooting"],
            "cost": ["cost", "budget", "roi", "investment", "expense", "financial", "economic"],
            "compliance": ["compliance", "regulation", "standard", "policy", "governance", "audit"]
        }
        
        # Stop words to filter out
        self.stop_words = {
            "system", "application", "software", "hardware", "component", "module", "service", "process",
            "data", "information", "document", "file", "report", "log", "event", "activity", "action",
            "method", "function", "procedure", "protocol", "standard", "policy", "rule", "guideline",
            "requirement", "specification", "design", "architecture", "framework", "platform", "solution"
        }
    
    def extract_stakeholders_from_text(self, text: str, document_type: str = "technical") -> Dict[str, Dict]:
        """
        Extract stakeholders from text using advanced pattern matching
        
        Args:
            text: Input text to analyze
            document_type: Type of document (technical, business, requirements, etc.)
            
        Returns:
            Dictionary of extracted stakeholders with metadata
        """
        self.logger.info(f"Starting enhanced stakeholder extraction from {len(text)} characters")
        
        # Step 1: Pattern-based extraction
        raw_stakeholders = self._extract_raw_stakeholders(text)
        self.logger.info(f"Raw stakeholder mentions found: {len(raw_stakeholders)}")
        
        # Step 2: Clean and normalize stakeholder names
        normalized_stakeholders = self._normalize_stakeholders(raw_stakeholders)
        self.logger.info(f"Normalized stakeholders: {len(normalized_stakeholders)}")
        
        # Step 3: Group and deduplicate similar stakeholders
        grouped_stakeholders = self._group_similar_stakeholders(normalized_stakeholders)
        self.logger.info(f"Grouped stakeholders: {len(grouped_stakeholders)}")
        
        # Step 4: Extract stakeholder context and interests
        enriched_stakeholders = self._enrich_stakeholder_context(grouped_stakeholders, text)
        
        # Step 5: Generate structured stakeholder data
        structured_stakeholders = self._generate_structured_stakeholders(enriched_stakeholders)
        
        self.logger.info(f"Final structured stakeholders: {len(structured_stakeholders)}")
        
        return structured_stakeholders
    
    def _extract_raw_stakeholders(self, text: str) -> List[Dict]:
        """Extract raw stakeholder mentions using all pattern categories"""
        raw_stakeholders = []
        
        for category, patterns in self.stakeholder_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    stakeholder_name = match.group(1).strip()
                    if len(stakeholder_name) > 2 and stakeholder_name.lower() not in self.stop_words:
                        raw_stakeholders.append({
                            "name": stakeholder_name,
                            "category": category,
                            "pattern": pattern,
                            "context": text[max(0, match.start()-50):match.end()+50],
                            "position": match.start()
                        })
        
        return raw_stakeholders
    
    def _normalize_stakeholders(self, raw_stakeholders: List[Dict]) -> List[Dict]:
        """Clean and normalize stakeholder names"""
        normalized = []
        
        for stakeholder in raw_stakeholders:
            name = stakeholder["name"]
            
            # Clean up the name
            name = re.sub(r'\s+', ' ', name)  # Multiple spaces to single
            name = name.strip()
            
            # Remove common prefixes/suffixes that don't add value
            name = re.sub(r'^(The|A|An)\s+', '', name, flags=re.IGNORECASE)
            name = re.sub(r'\s+(Team|Group|Department|Division)$', r' \1', name, flags=re.IGNORECASE)
            
            # Skip if too short or generic
            if len(name) < 3 or name.lower() in self.stop_words:
                continue
            
            # Update the stakeholder record
            stakeholder["normalized_name"] = name
            normalized.append(stakeholder)
        
        return normalized
    
    def _group_similar_stakeholders(self, stakeholders: List[Dict]) -> Dict[str, List[Dict]]:
        """Group similar stakeholders together"""
        groups = defaultdict(list)
        
        for stakeholder in stakeholders:
            # Create a key for grouping (simplified name)
            key = self._create_grouping_key(stakeholder["normalized_name"])
            groups[key].append(stakeholder)
        
        # Filter out groups with too few mentions (likely noise)
        filtered_groups = {k: v for k, v in groups.items() if len(v) >= 1}
        
        return filtered_groups
    
    def _create_grouping_key(self, name: str) -> str:
        """Create a key for grouping similar stakeholder names"""
        # Convert to lowercase and remove common variations
        key = name.lower()
        
        # Remove plurals
        key = re.sub(r's$', '', key)
        
        # Remove common role suffixes/prefixes for grouping
        key = re.sub(r'\b(senior|junior|lead|chief|head|principal|associate|assistant)\s+', '', key)
        key = re.sub(r'\s+(team|group|department|division|unit|staff)$', '', key)
        
        return key.strip()
    
    def _enrich_stakeholder_context(self, grouped_stakeholders: Dict[str, List[Dict]], full_text: str) -> Dict[str, Dict]:
        """Enrich stakeholder data with context analysis"""
        enriched = {}
        
        for group_key, stakeholder_group in grouped_stakeholders.items():
            # Get the most representative name from the group
            representative_name = self._get_representative_name(stakeholder_group)
            
            # Analyze interests and responsibilities
            interests = self._analyze_stakeholder_interests(stakeholder_group, full_text)
            responsibilities = self._extract_responsibilities(stakeholder_group, full_text)
            
            # Classify stakeholder type
            stakeholder_type = self._classify_stakeholder_type(representative_name, stakeholder_group)
            
            # Determine influence level
            influence_level = self._determine_influence_level(stakeholder_group, full_text)
            
            # Extract requirements/needs
            requirements = self._extract_stakeholder_requirements(stakeholder_group, full_text)
            
            enriched[group_key] = {
                "name": representative_name,
                "type": stakeholder_type,
                "mentions": len(stakeholder_group),
                "interests": interests,
                "responsibilities": responsibilities,
                "influence": influence_level,
                "requirements": requirements,
                "contexts": [s["context"] for s in stakeholder_group[:3]],  # Keep top 3 contexts
                "categories": list(set(s["category"] for s in stakeholder_group))
            }
        
        return enriched
    
    def _get_representative_name(self, stakeholder_group: List[Dict]) -> str:
        """Get the most representative name from a group of similar stakeholders"""
        names = [s["normalized_name"] for s in stakeholder_group]
        
        # Count occurrences and pick the most common
        name_counts = Counter(names)
        most_common_name = name_counts.most_common(1)[0][0]
        
        return most_common_name
    
    def _analyze_stakeholder_interests(self, stakeholder_group: List[Dict], full_text: str) -> List[str]:
        """Analyze stakeholder interests based on context"""
        interests = []
        
        # Get contexts where this stakeholder is mentioned
        contexts = [s["context"] for s in stakeholder_group]
        combined_context = " ".join(contexts).lower()
        
        # Check for interest patterns
        for interest_type, keywords in self.interest_patterns.items():
            if any(keyword in combined_context for keyword in keywords):
                interests.append(interest_type)
        
        return interests[:5]  # Limit to top 5 interests
    
    def _extract_responsibilities(self, stakeholder_group: List[Dict], full_text: str) -> List[str]:
        """Extract responsibilities from context"""
        responsibilities = []
        
        # Responsibility patterns
        responsibility_patterns = [
            r"responsible for ([^.]+)",
            r"manages ([^.]+)",
            r"oversees ([^.]+)",
            r"handles ([^.]+)",
            r"performs ([^.]+)",
            r"maintains ([^.]+)",
            r"operates ([^.]+)",
            r"monitors ([^.]+)"
        ]
        
        contexts = [s["context"] for s in stakeholder_group]
        for context in contexts:
            for pattern in responsibility_patterns:
                matches = re.findall(pattern, context, re.IGNORECASE)
                responsibilities.extend([match.strip() for match in matches])
        
        # Remove duplicates and limit
        unique_responsibilities = list(set(responsibilities))[:3]
        return unique_responsibilities
    
    def _classify_stakeholder_type(self, name: str, stakeholder_group: List[Dict]) -> str:
        """Classify stakeholder into a type category"""
        name_lower = name.lower()
        
        for category, keywords in self.stakeholder_categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
        
        # Check categories from extraction patterns
        categories = [s["category"] for s in stakeholder_group]
        if "roles" in categories:
            return "technical"
        elif "organizations" in categories:
            return "organizational"
        elif "actors" in categories:
            return "user"
        
        return "general"
    
    def _determine_influence_level(self, stakeholder_group: List[Dict], full_text: str) -> str:
        """Determine stakeholder influence level"""
        name = stakeholder_group[0]["normalized_name"].lower()
        
        # High influence indicators
        high_influence_keywords = ["manager", "director", "lead", "chief", "head", "executive", "officer", "administrator"]
        
        # Medium influence indicators  
        medium_influence_keywords = ["analyst", "engineer", "specialist", "coordinator", "supervisor"]
        
        if any(keyword in name for keyword in high_influence_keywords):
            return "High"
        elif any(keyword in name for keyword in medium_influence_keywords):
            return "Medium"
        else:
            return "Low"
    
    def _extract_stakeholder_requirements(self, stakeholder_group: List[Dict], full_text: str) -> List[str]:
        """Extract specific requirements for this stakeholder"""
        requirements = []
        
        # Requirement patterns
        requirement_patterns = [
            r"needs? to ([^.]+)",
            r"requires? ([^.]+)",
            r"must ([^.]+)",
            r"shall ([^.]+)",
            r"should ([^.]+)",
            r"expects? ([^.]+)"
        ]
        
        contexts = [s["context"] for s in stakeholder_group]
        for context in contexts:
            for pattern in requirement_patterns:
                matches = re.findall(pattern, context, re.IGNORECASE)
                requirements.extend([match.strip() for match in matches])
        
        # Clean and limit requirements
        unique_requirements = list(set(requirements))[:3]
        return unique_requirements
    
    def _generate_structured_stakeholders(self, enriched_stakeholders: Dict[str, Dict]) -> Dict[str, Dict]:
        """Generate final structured stakeholder data"""
        structured = {}
        counter = 1
        
        for group_key, stakeholder_data in enriched_stakeholders.items():
            stakeholder_id = f"STK-{counter:03d}"
            
            structured[stakeholder_id] = {
                "id": stakeholder_id,
                "name": stakeholder_data["name"],
                "type": stakeholder_data["type"],
                "role": self._generate_role_description(stakeholder_data),
                "interests": stakeholder_data["interests"],
                "responsibilities": stakeholder_data["responsibilities"],
                "influence": stakeholder_data["influence"],
                "requirements": stakeholder_data["requirements"],
                "phase": self._determine_arcadia_phase(stakeholder_data),
                "mentions_count": stakeholder_data["mentions"],
                "extraction_confidence": self._calculate_confidence(stakeholder_data),
                "contexts": stakeholder_data["contexts"][:2]  # Keep top 2 contexts
            }
            
            counter += 1
        
        return structured
    
    def _generate_role_description(self, stakeholder_data: Dict) -> str:
        """Generate a role description for the stakeholder"""
        name = stakeholder_data["name"]
        stakeholder_type = stakeholder_data["type"]
        responsibilities = stakeholder_data["responsibilities"]
        
        if responsibilities:
            return f"{name} - {stakeholder_type} responsible for {', '.join(responsibilities[:2])}"
        else:
            return f"{name} - {stakeholder_type} stakeholder"
    
    def _determine_arcadia_phase(self, stakeholder_data: Dict) -> str:
        """Determine the most relevant ARCADIA phase for this stakeholder"""
        stakeholder_type = stakeholder_data["type"]
        interests = stakeholder_data["interests"]
        
        # Map stakeholder types to ARCADIA phases
        type_phase_mapping = {
            "business": "operational",
            "user": "operational", 
            "management": "operational",
            "technical": "system",
            "security": "system",
            "operations": "logical",
            "external": "operational"
        }
        
        return type_phase_mapping.get(stakeholder_type, "operational")
    
    def _calculate_confidence(self, stakeholder_data: Dict) -> float:
        """Calculate confidence score for the stakeholder extraction"""
        base_confidence = 0.5
        
        # Boost confidence based on mentions
        mention_boost = min(0.3, stakeholder_data["mentions"] * 0.1)
        
        # Boost confidence based on responsibilities found
        responsibility_boost = min(0.2, len(stakeholder_data["responsibilities"]) * 0.1)
        
        # Boost confidence based on requirements found
        requirement_boost = min(0.1, len(stakeholder_data["requirements"]) * 0.05)
        
        confidence = base_confidence + mention_boost + responsibility_boost + requirement_boost
        
        return min(1.0, confidence)
    
    def analyze_stakeholder_relationships(self, stakeholders: Dict[str, Dict], text: str) -> Dict[str, List[str]]:
        """Analyze relationships between stakeholders"""
        relationships = defaultdict(list)
        
        # Look for relationship patterns in text
        relationship_patterns = [
            r"(\w+(?:\s+\w+)*)\s+(?:reports to|managed by|supervised by|works with|collaborates with|coordinates with)\s+(\w+(?:\s+\w+)*)",
            r"(\w+(?:\s+\w+)*)\s+(?:and|with)\s+(\w+(?:\s+\w+)*)\s+(?:work together|collaborate|coordinate|interface)"
        ]
        
        stakeholder_names = [s["name"] for s in stakeholders.values()]
        
        for pattern in relationship_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entity1, entity2 = match
                
                # Check if these entities correspond to our stakeholders
                for name in stakeholder_names:
                    if entity1.lower() in name.lower() or name.lower() in entity1.lower():
                        for other_name in stakeholder_names:
                            if other_name != name and (entity2.lower() in other_name.lower() or other_name.lower() in entity2.lower()):
                                relationships[name].append(other_name)
        
        return dict(relationships)
    
    def get_extraction_statistics(self, stakeholders: Dict[str, Dict]) -> Dict[str, Any]:
        """Get statistics about the stakeholder extraction"""
        if not stakeholders:
            return {
                "total_stakeholders": 0,
                "by_type": {},
                "by_influence": {},
                "by_phase": {},
                "average_confidence": 0.0
            }
        
        stats = {
            "total_stakeholders": len(stakeholders),
            "by_type": Counter(s["type"] for s in stakeholders.values()),
            "by_influence": Counter(s["influence"] for s in stakeholders.values()),
            "by_phase": Counter(s["phase"] for s in stakeholders.values()),
            "average_confidence": sum(s["extraction_confidence"] for s in stakeholders.values()) / len(stakeholders),
            "total_mentions": sum(s["mentions_count"] for s in stakeholders.values()),
            "stakeholders_with_requirements": len([s for s in stakeholders.values() if s["requirements"]]),
            "stakeholders_with_responsibilities": len([s for s in stakeholders.values() if s["responsibilities"]])
        }
        
        return stats 