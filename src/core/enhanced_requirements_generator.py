from typing import List, Dict, Any, Optional, Tuple
import re
from config import arcadia_config, requirements_templates
import logging
from .priority_analyzer import ARCADIAPriorityAnalyzer
from .component_analyzer import ComponentAnalyzer

class EnhancedRequirementsGenerator:
    """
    Enhanced Requirements Generator addressing key improvement points:
    1. Balanced priority distribution (30% MUST, 50% SHOULD, 20% COULD)
    2. Context-aware NFR category selection to avoid overrepresentation
    3. Complete requirement descriptions with operational context
    4. Specific verification methods based on requirement type and phase
    5. Enhanced traceability to operational capabilities and scenarios
    """
    
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client
        self.logger = logging.getLogger(__name__)
        self.priority_analyzer = ARCADIAPriorityAnalyzer()
        self.component_analyzer = ComponentAnalyzer()
        self.requirement_counters = {
            "functional": 1,
            "non_functional": 1,
            "stakeholder": 1
        }
        
        # Target priority distribution based on ARCADIA best practices
        self.priority_targets = {
            "MUST": 0.30,    # 30% critical requirements
            "SHOULD": 0.50,  # 50% important requirements  
            "COULD": 0.20    # 20% nice-to-have requirements
        }
        
        # Phase and category-specific verification methods
        self.verification_methods = {
            "functional": {
                "operational": [
                    "Stakeholder review and approval",
                    "Operational scenario walkthrough", 
                    "User acceptance testing",
                    "Capability demonstration"
                ],
                "system": [
                    "Requirements traceability check",
                    "Functional analysis verification",
                    "System scenario simulation",
                    "Trade-off analysis validation"
                ],
                "logical": [
                    "Component allocation verification",
                    "Interface consistency check", 
                    "Multi-viewpoint analysis",
                    "Architecture compromise validation"
                ],
                "physical": [
                    "Implementation feasibility assessment",
                    "Physical interface testing",
                    "Deployment scenario validation",
                    "Resource constraint verification"
                ]
            },
            "non_functional": {
                "performance": [
                    "Performance testing and benchmarking",
                    "Load testing and stress analysis",
                    "Response time measurement",
                    "Throughput analysis"
                ],
                "security": [
                    "Security audit and penetration testing",
                    "Vulnerability assessment",
                    "Threat modeling validation",
                    "Access control verification"
                ],
                "usability": [
                    "User experience testing",
                    "Usability inspection and evaluation",
                    "Accessibility compliance audit",
                    "Human factors assessment"
                ],
                "reliability": [
                    "Reliability testing and MTBF analysis",
                    "Fault injection and tolerance testing",
                    "Failure mode analysis",
                    "Availability measurement"
                ],
                "scalability": [
                    "Scalability testing and capacity planning",
                    "Resource utilization analysis",
                    "Growth scenario validation",
                    "Performance scaling verification"
                ],
                "maintainability": [
                    "Code quality metrics assessment",
                    "Maintainability index calculation",
                    "Technical debt evaluation",
                    "Maintenance effort estimation"
                ]
            }
        }

    def generate_balanced_requirements(self, 
                                     context: List[Dict[str, Any]], 
                                     phase: str, 
                                     proposal_text: str,
                                     requirement_types: List[str]) -> Dict[str, Any]:
        """
        Generate balanced requirements addressing all improvement points
        """
        results = {}
        
        # Generate stakeholders if requested
        if "stakeholder" in requirement_types:
            results["stakeholders"] = self.generate_stakeholders(context, proposal_text)
        
        # Generate functional requirements with balanced priorities
        if "functional" in requirement_types:
            results["functional"] = self.generate_enhanced_functional_requirements(
                context, phase, proposal_text
            )
        
        # Generate context-aware non-functional requirements
        if "non_functional" in requirement_types:
            results["non_functional"] = self.generate_context_aware_nfr(
                context, phase, proposal_text
            )
        
        # Apply overall priority balancing
        all_requirements = []
        for req_type, reqs in results.items():
            if req_type != "stakeholders" and isinstance(reqs, list):
                all_requirements.extend(reqs)
        
        if all_requirements:
            balanced_requirements = self._balance_overall_priority_distribution(all_requirements)
            
            # Redistribute balanced requirements back to categories
            functional_reqs = [req for req in balanced_requirements if req.get("type") == "Functional"]
            nf_reqs = [req for req in balanced_requirements if req.get("type") == "Non-Functional"]
            
            if functional_reqs:
                results["functional"] = functional_reqs
            if nf_reqs:
                results["non_functional"] = nf_reqs
        
        return results

    def generate_enhanced_functional_requirements(self, 
                                                context: List[Dict[str, Any]], 
                                                phase: str, 
                                                proposal_text: str) -> List[Dict[str, Any]]:
        """Generate functional requirements with enhanced context and traceability"""
        
        # Analyze operational context
        operational_capabilities = self._extract_operational_capabilities(context, proposal_text)
        operational_scenarios = self._extract_operational_scenarios(context, proposal_text)
        stakeholder_needs = self._extract_stakeholder_needs(context, proposal_text)
        
        # Build enhanced prompt
        enhanced_prompt = self._build_enhanced_functional_prompt(
            context, phase, proposal_text, operational_capabilities, 
            operational_scenarios, stakeholder_needs
        )
        
        # Generate requirements
        response = self._call_ai_model(enhanced_prompt, "requirements_generation")
        
        # Parse with enhanced extraction
        requirements = self._parse_enhanced_requirements(
            response, "functional", phase, None, context, 
            operational_capabilities, operational_scenarios, stakeholder_needs
        )
        
        return requirements

    def generate_context_aware_nfr(self, 
                                  context: List[Dict[str, Any]], 
                                  phase: str, 
                                  proposal_text: str) -> List[Dict[str, Any]]:
        """Generate context-aware NFR to avoid overrepresentation"""
        
        # Analyze context to select relevant NFR categories
        relevant_categories = self._analyze_nfr_context_relevance(context, proposal_text)
        
        self.logger.info(f"Selected {len(relevant_categories)} relevant NFR categories based on context analysis")
        
        all_nfr = []
        
        for category, relevance_score in relevant_categories.items():
            # Limit requirements per category based on relevance
            max_requirements = max(1, min(3, int(relevance_score * 4)))
            
            # Generate category-specific requirements
            category_requirements = self._generate_category_specific_nfr(
                context, phase, proposal_text, category, relevance_score, max_requirements
            )
            
            all_nfr.extend(category_requirements)
        
        return all_nfr

    def _analyze_nfr_context_relevance(self, 
                                     context: List[Dict[str, Any]], 
                                     proposal_text: str) -> Dict[str, float]:
        """Analyze context to determine relevant NFR categories and their importance"""
        
        combined_text = f"{self._prepare_context_text(context)} {proposal_text}".lower()
        nfr_categories = arcadia_config.REQUIREMENT_CATEGORIES["non_functional"]["subcategories"]
        
        category_scores = {}
        
        for category, info in nfr_categories.items():
            relevance_score = 0.0
            keywords = info.get("keywords", [])
            
            # Calculate keyword-based relevance
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    relevance_score += 1.0
            
            # Normalize by keyword count
            if keywords:
                relevance_score = relevance_score / len(keywords)
            
            # Apply domain-specific boosting
            domain_boost = self._calculate_domain_relevance_boost(category, combined_text)
            relevance_score = min(1.0, relevance_score + domain_boost)
            
            # Include if above threshold or if core category
            if relevance_score > 0.15 or category in ["performance", "security", "reliability"]:
                category_scores[category] = relevance_score
        
        # Limit to top 4 categories to avoid overrepresentation
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_categories[:4])

    def _calculate_domain_relevance_boost(self, category: str, text: str) -> float:
        """Calculate domain-specific relevance boost for NFR categories"""
        
        domain_indicators = {
            "performance": ["real-time", "speed", "fast", "efficient", "optimization"],
            "security": ["secure", "protection", "authentication", "encryption", "access"],
            "reliability": ["reliable", "fault", "failure", "robust", "resilient"],
            "usability": ["user", "interface", "experience", "ergonomic", "intuitive"],
            "scalability": ["scale", "growth", "capacity", "expansion", "volume"],
            "maintainability": ["maintain", "support", "update", "modify", "evolve"]
        }
        
        indicators = domain_indicators.get(category, [])
        boost = sum(0.1 for indicator in indicators if indicator in text)
        
        return min(0.3, boost)  # Cap boost at 0.3

    def _generate_category_specific_nfr(self, 
                                       context: List[Dict[str, Any]], 
                                       phase: str, 
                                       proposal_text: str,
                                       category: str,
                                       relevance_score: float,
                                       max_requirements: int) -> List[Dict[str, Any]]:
        """Generate specific NFR for a category with context awareness"""
        
        # Build category-specific prompt
        prompt = self._build_nfr_category_prompt(
            context, phase, proposal_text, category, relevance_score
        )
        
        # Generate requirements
        response = self._call_ai_model(prompt, "requirements_generation")
        
        # Parse with category-specific extraction
        requirements = self._parse_enhanced_requirements(
            response, "non_functional", phase, category, context
        )
        
        # Limit to max requirements
        return requirements[:max_requirements]

    def _build_enhanced_functional_prompt(self, 
                                        context: List[Dict[str, Any]], 
                                        phase: str, 
                                        proposal_text: str,
                                        operational_capabilities: List[str],
                                        operational_scenarios: List[str],
                                        stakeholder_needs: List[str]) -> str:
        """Build enhanced prompt for functional requirements generation"""
        
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        
        prompt = f"""
Generate functional requirements for ARCADIA {phase} phase with enhanced context awareness.

CONTEXT ANALYSIS:
- Phase: {phase} ({phase_info.get('description', '')})
- Document Context: {self._prepare_context_text(context)}
- Operational Capabilities: {', '.join(operational_capabilities[:5])}
- Operational Scenarios: {', '.join(operational_scenarios[:3])}
- Key Stakeholder Needs: {', '.join(stakeholder_needs[:5])}

ENHANCED GENERATION REQUIREMENTS:

1. PRIORITY DISTRIBUTION TARGET:
   - Generate exactly 30% MUST, 50% SHOULD, 20% COULD requirements
   - Base priority on operational criticality and stakeholder impact
   - MUST: Safety-critical, regulatory compliance, core operational capabilities
   - SHOULD: Important operational features, significant stakeholder needs
   - COULD: Enhancement features, convenience functions

2. REQUIREMENT COMPLETENESS:
   - Minimum 25 words per requirement description
   - Include specific operational context and components
   - Reference operational capabilities and scenarios where applicable
   - Ensure measurable acceptance criteria

3. TRACEABILITY ENHANCEMENT:
   - Link each requirement to specific operational capabilities
   - Reference relevant operational scenarios
   - Trace to stakeholder needs where applicable
   - Ensure phase-to-phase consistency

4. VERIFICATION SPECIFICITY:
   - Select verification method based on requirement content and phase
   - Avoid generic "Review and testing"
   - Consider operational validation approaches

Generate 5-7 well-balanced functional requirements following this structure:
- ID: FR-{phase.upper()[:3]}-XXX
- The system shall [detailed requirement with operational context]
- Priority: MUST/SHOULD/COULD (with clear rationale)
- Verification: [specific method appropriate to requirement and phase]
- Operational Capability Link: [reference to relevant capability]
- Stakeholder Traceability: [link to stakeholder needs]
"""
        
        return prompt

    def _build_nfr_category_prompt(self, 
                                  context: List[Dict[str, Any]], 
                                  phase: str, 
                                  proposal_text: str,
                                  category: str,
                                  relevance_score: float) -> str:
        """Build category-specific prompt for NFR generation"""
        
        prompt = f"""
Generate non-functional requirements for category: {category} (relevance: {relevance_score:.2f})

CONTEXT:
- Phase: {phase}
- Document Context: {self._prepare_context_text(context)}
- Category Focus: {category}

GENERATION GUIDELINES:
1. Generate 1-2 high-quality requirements (avoid overgeneration)
2. Ensure measurable criteria and specific metrics
3. Include operational context and scenarios
4. Use category-appropriate verification methods
5. Base priority on operational criticality

Requirements should be:
- Measurable with specific metrics
- Testable with clear acceptance criteria
- Linked to operational capabilities
- Appropriately prioritized based on context

Generate requirements in format:
- ID: NFR-{category.upper()[:4]}-XXX
- The system shall [measurable requirement with metrics]
- Metric: [how to measure]
- Target Value: [specific target]
- Priority: MUST/SHOULD/COULD (with rationale)
- Verification: [specific testing method for {category}]
"""
        
        return prompt

    def _parse_enhanced_requirements(self, 
                                   response: str, 
                                   req_type: str, 
                                   phase: str, 
                                   category: Optional[str] = None,
                                   context: Optional[List[Dict[str, Any]]] = None,
                                   operational_capabilities: Optional[List[str]] = None,
                                   operational_scenarios: Optional[List[str]] = None,
                                   stakeholder_needs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Enhanced parsing with complete descriptions and specific verification methods"""
        
        requirements = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Enhanced pattern matching for requirements
            shall_match = re.search(r"[Tt]he system shall ([^.]+(?:\.[^.]*){0,3})", line)
            if shall_match:
                requirement_text = shall_match.group(1).strip()
                
                # Skip short or generic requirements
                if len(requirement_text.split()) < 8:
                    continue
                
                # Generate enhanced requirement
                requirement = self._create_enhanced_requirement(
                    requirement_text, req_type, phase, category, context,
                    operational_capabilities, operational_scenarios, stakeholder_needs, line
                )
                
                if requirement:
                    requirements.append(requirement)
        
        return requirements

    def _create_enhanced_requirement(self, 
                                   requirement_text: str,
                                   req_type: str,
                                   phase: str,
                                   category: Optional[str],
                                   context: Optional[List[Dict[str, Any]]],
                                   operational_capabilities: Optional[List[str]],
                                   operational_scenarios: Optional[List[str]],
                                   stakeholder_needs: Optional[List[str]],
                                   full_line: str) -> Optional[Dict[str, Any]]:
        """Create enhanced requirement with complete information"""
        
        # Generate requirement ID
        if req_type == "functional":
            req_id = f"FR-{phase.upper()[:3]}-{self.requirement_counters['functional']:03d}"
            self.requirement_counters['functional'] += 1
        else:
            cat_prefix = category.upper()[:4] if category else "NFR"
            req_id = f"NFR-{cat_prefix}-{self.requirement_counters['non_functional']:03d}"
            self.requirement_counters['non_functional'] += 1
        
        # Analyze priority with enhanced context
        context_text = self._prepare_context_text(context or [])
        priority, confidence, analysis_details = self.priority_analyzer.analyze_requirement_priority(
            requirement_text, context_text, phase, stakeholder_needs or []
        )
        
        # Extract explicit priority if provided
        priority_match = re.search(r"Priority:\s*(MUST|SHOULD|COULD)", full_line)
        if priority_match:
            explicit_priority = priority_match.group(1)
            priority_order = {"MUST": 3, "SHOULD": 2, "COULD": 1}
            if priority_order.get(explicit_priority, 0) >= priority_order.get(priority, 0):
                priority = explicit_priority
        
        # Select appropriate verification method
        verification = self._select_enhanced_verification_method(
            req_type, phase, category, requirement_text
        )
        
        # Extract custom verification if provided
        verification_match = re.search(r"Verification:\s*([^.\n]+)", full_line)
        if verification_match:
            custom_verification = verification_match.group(1).strip()
            if len(custom_verification) > 15:
                verification = custom_verification
        
        # Create enhanced description
        description = f"The system shall {requirement_text}"
        if len(description) < 60:
            description += f" This requirement supports {phase} phase objectives and operational effectiveness."
        
        # Generate enhanced title
        title = requirement_text if len(requirement_text) <= 65 else f"{requirement_text[:62]}..."
        
        # Build enhanced requirement
        requirement = {
            "id": req_id,
            "type": req_type.title(),
            "title": title,
            "description": description,
            "priority": priority,
            "priority_confidence": confidence,
            "priority_analysis": analysis_details,
            "phase": phase,
            "verification_method": verification,
            "dependencies": [],
            "rationale": self.priority_analyzer.generate_priority_rationale(priority, analysis_details),
            "operational_capability_links": self._link_to_capabilities(requirement_text, operational_capabilities or []),
            "operational_scenario_links": self._link_to_scenarios(requirement_text, operational_scenarios or []),
            "stakeholder_traceability": self._link_to_stakeholders(requirement_text, stakeholder_needs or [])
        }
        
        # Add NFR-specific fields
        if req_type == "non_functional" and category:
            requirement.update({
                "category": category,
                "metric": self._extract_enhanced_metric(requirement_text),
                "target_value": self._extract_enhanced_target_value(requirement_text),
                "measurement_method": self._determine_measurement_method(category, requirement_text)
            })
        
        return requirement

    def _select_enhanced_verification_method(self, 
                                           req_type: str, 
                                           phase: str, 
                                           category: Optional[str],
                                           requirement_text: str) -> str:
        """Select appropriate verification method based on requirement characteristics"""
        
        if req_type == "functional":
            methods = self.verification_methods["functional"].get(phase, ["Functional testing"])
            
            # Content-based method selection
            text_lower = requirement_text.lower()
            if "interface" in text_lower or "communication" in text_lower:
                return "Interface testing and integration verification"
            elif "user" in text_lower or "operator" in text_lower:
                return "User acceptance testing and operational validation"
            elif "scenario" in text_lower or "operational" in text_lower:
                return "Operational scenario validation and testing"
            elif "performance" in text_lower or "response" in text_lower:
                return "Performance testing and system validation"
            else:
                return methods[0] if methods else "Functional testing and verification"
        
        elif req_type == "non_functional" and category:
            methods = self.verification_methods["non_functional"].get(category, ["Testing and analysis"])
            return methods[0] if methods else "Performance testing and analysis"
        
        return "Requirements review and validation"

    def _balance_overall_priority_distribution(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Balance overall priority distribution across all requirements"""
        
        if not requirements:
            return requirements
        
        total_reqs = len(requirements)
        target_counts = {
            "MUST": max(1, int(total_reqs * self.priority_targets["MUST"])),
            "SHOULD": max(1, int(total_reqs * self.priority_targets["SHOULD"])),
            "COULD": max(1, int(total_reqs * self.priority_targets["COULD"]))
        }
        
        # Adjust for rounding
        remaining = total_reqs - sum(target_counts.values())
        target_counts["SHOULD"] += remaining
        
        # Sort by confidence for intelligent rebalancing
        requirements.sort(key=lambda x: x.get("priority_confidence", 0.5), reverse=True)
        
        # Rebalance priorities
        priority_counts = {"MUST": 0, "SHOULD": 0, "COULD": 0}
        
        for req in requirements:
            current_priority = req.get("priority", "SHOULD")
            
            # Try to keep current priority if slots available
            if priority_counts[current_priority] < target_counts[current_priority]:
                final_priority = current_priority
            else:
                # Find available slot
                for priority in ["MUST", "SHOULD", "COULD"]:
                    if priority_counts[priority] < target_counts[priority]:
                        final_priority = priority
                        break
                else:
                    final_priority = "SHOULD"  # Fallback
            
            req["priority"] = final_priority
            req["priority_rebalanced"] = final_priority != current_priority
            priority_counts[final_priority] += 1
        
        self.logger.info(f"Priority rebalancing completed: {priority_counts}")
        return requirements

    # Utility methods for enhanced context extraction
    
    def _extract_operational_capabilities(self, context: List[Dict[str, Any]], proposal_text: str) -> List[str]:
        """Extract operational capabilities from context"""
        combined_text = f"{self._prepare_context_text(context)} {proposal_text}"
        
        capability_patterns = [
            r"capability to ([^.]+)",
            r"able to ([^.]+)",
            r"capacity for ([^.]+)",
            r"operational capability ([^.]+)"
        ]
        
        capabilities = []
        for pattern in capability_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            capabilities.extend([match.strip() for match in matches if len(match.strip()) > 5])
        
        return capabilities[:10]  # Limit to top 10

    def _extract_operational_scenarios(self, context: List[Dict[str, Any]], proposal_text: str) -> List[str]:
        """Extract operational scenarios from context"""
        combined_text = f"{self._prepare_context_text(context)} {proposal_text}"
        
        scenario_patterns = [
            r"scenario ([^.]+)",
            r"use case ([^.]+)",
            r"operational situation ([^.]+)",
            r"when ([^.]+)"
        ]
        
        scenarios = []
        for pattern in scenario_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            scenarios.extend([match.strip() for match in matches if len(match.strip()) > 8])
        
        return scenarios[:8]  # Limit to top 8

    def _extract_stakeholder_needs(self, context: List[Dict[str, Any]], proposal_text: str) -> List[str]:
        """Extract stakeholder needs from context"""
        combined_text = f"{self._prepare_context_text(context)} {proposal_text}"
        
        need_patterns = [
            r"need[s]? ([^.]+)",
            r"require[s]? ([^.]+)",
            r"expect[s]? ([^.]+)",
            r"demand[s]? ([^.]+)"
        ]
        
        needs = []
        for pattern in need_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            needs.extend([match.strip() for match in matches if len(match.strip()) > 5])
        
        return needs[:12]  # Limit to top 12

    def _link_to_capabilities(self, requirement_text: str, capabilities: List[str]) -> List[str]:
        """Link requirement to relevant operational capabilities"""
        links = []
        req_lower = requirement_text.lower()
        
        for capability in capabilities[:5]:
            cap_words = capability.lower().split()
            if any(word in req_lower for word in cap_words if len(word) > 3):
                links.append(f"Supports capability: {capability[:60]}...")
        
        return links

    def _link_to_scenarios(self, requirement_text: str, scenarios: List[str]) -> List[str]:
        """Link requirement to relevant operational scenarios"""
        links = []
        req_lower = requirement_text.lower()
        
        for scenario in scenarios[:3]:
            scenario_words = scenario.lower().split()
            if any(word in req_lower for word in scenario_words if len(word) > 3):
                links.append(f"Addresses scenario: {scenario[:60]}...")
        
        return links

    def _link_to_stakeholders(self, requirement_text: str, stakeholder_needs: List[str]) -> List[str]:
        """Link requirement to stakeholder needs"""
        links = []
        req_lower = requirement_text.lower()
        
        for need in stakeholder_needs[:5]:
            need_words = need.lower().split()
            if any(word in req_lower for word in need_words if len(word) > 3):
                links.append(f"Addresses need: {need[:50]}...")
        
        return links

    def _extract_enhanced_metric(self, requirement_text: str) -> str:
        """Extract enhanced measurable metric from requirement text"""
        metric_patterns = [
            r"(\d+(?:\.\d+)?)\s*(seconds?|minutes?|hours?|ms|milliseconds?)",
            r"(\d+(?:\.\d+)?)\s*(%|percent|percentage)",
            r"(\d+(?:\.\d+)?)\s*(MB|GB|TB|KB|bytes?)",
            r"(\d+(?:\.\d+)?)\s*(users?|requests?|transactions?|operations?)",
            r"(\d+(?:\.\d+)?)\s*(times?|instances?|occurrences?)"
        ]
        
        for pattern in metric_patterns:
            match = re.search(pattern, requirement_text, re.IGNORECASE)
            if match:
                return f"{match.group(1)} {match.group(2)}"
        
        return "Quantitative measure to be defined"

    def _extract_enhanced_target_value(self, requirement_text: str) -> str:
        """Extract enhanced target value from requirement text"""
        value_patterns = [
            r"(?:less than|<|under|below|maximum|max)\s*(\d+(?:\.\d+)?)",
            r"(?:greater than|>|above|over|minimum|min|at least)\s*(\d+(?:\.\d+)?)",
            r"(?:exactly|equal to|=)\s*(\d+(?:\.\d+)?)",
            r"(?:between)\s*(\d+(?:\.\d+)?)\s*(?:and)\s*(\d+(?:\.\d+)?)"
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, requirement_text, re.IGNORECASE)
            if match:
                if match.lastindex == 2:  # Between pattern
                    return f"{match.group(1)}-{match.group(2)}"
                else:
                    return match.group(1)
        
        return "Target value to be defined"

    def _determine_measurement_method(self, category: str, requirement_text: str) -> str:
        """Determine appropriate measurement method for NFR category"""
        measurement_methods = {
            "performance": "Performance monitoring and benchmarking",
            "security": "Security assessment and audit",
            "usability": "User testing and evaluation",
            "reliability": "Reliability testing and analysis",
            "scalability": "Load testing and capacity analysis",
            "maintainability": "Code quality metrics and assessment"
        }
        
        return measurement_methods.get(category, "Measurement and analysis")

    # Utility methods (delegate to existing methods)
    
    def generate_stakeholders(self, context: List[Dict[str, Any]], proposal_text: str) -> Dict[str, Any]:
        """Generate stakeholder analysis (delegated to existing implementation)"""
        # This would delegate to the existing stakeholder generation logic
        return {}

    def _call_ai_model(self, prompt: str, model_type: str) -> str:
        """Call AI model (delegated to existing implementation)"""
        # This would delegate to the existing AI model calling logic
        return ""

    def _prepare_context_text(self, context: List[Dict[str, Any]]) -> str:
        """Prepare context text (delegated to existing implementation)"""
        if not context:
            return ""
        return " ".join([chunk.get("content", "") for chunk in context]) 