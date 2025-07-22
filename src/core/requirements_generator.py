from typing import List, Dict, Any, Optional
import re
from config import arcadia_config, requirements_templates
import logging
from .priority_analyzer import ARCADIAPriorityAnalyzer
from .component_analyzer import ComponentAnalyzer
from .enhanced_stakeholder_extractor import EnhancedStakeholderExtractor

class RequirementsGenerator:
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client
        self.logger = logging.getLogger(__name__)
        self.priority_analyzer = ARCADIAPriorityAnalyzer()
        self.component_analyzer = ComponentAnalyzer()
        self.enhanced_stakeholder_extractor = EnhancedStakeholderExtractor()
        self.requirement_counters = {
            "functional": 1,
            "non_functional": 1,
            "stakeholder": 1
        }
        # Enhanced priority distribution targets based on ARCADIA best practices
        self.priority_targets = {
            "MUST": 0.30,    # 30% critical requirements
            "SHOULD": 0.50,  # 50% important requirements  
            "COULD": 0.20    # 20% nice-to-have requirements
        }
        # Enhanced verification methods by requirement type and phase
        self.verification_methods = {
            "functional": {
                "operational": ["Stakeholder review", "Operational scenario walkthrough", "User acceptance testing"],
                "system": ["Requirements traceability check", "Functional analysis verification", "System scenario simulation"],
                "logical": ["Component allocation verification", "Interface consistency check", "Multi-viewpoint analysis"],
                "physical": ["Implementation feasibility assessment", "Physical interface testing", "Deployment scenario validation"]
            },
            "non_functional": {
                "performance": ["Performance testing", "Load testing", "Stress testing", "Benchmark analysis"],
                "security": ["Security audit", "Penetration testing", "Code review", "Threat modeling"],
                "usability": ["User testing", "Usability inspection", "Accessibility audit", "User experience evaluation"],
                "reliability": ["Reliability testing", "Fault injection", "MTBF analysis", "Failure mode analysis"],
                "scalability": ["Scalability testing", "Capacity planning", "Resource utilization analysis"],
                "maintainability": ["Code quality metrics", "Maintainability index", "Technical debt assessment"]
            }
        }
    
    def generate_stakeholders(self, context: List[Dict], proposal_text: str) -> Dict:
        """Generate stakeholder analysis from proposal using enhanced extraction"""
        self.logger.info("Starting enhanced stakeholder generation process...")
        
        # Use the enhanced stakeholder extractor
        enhanced_stakeholders = self.enhanced_stakeholder_extractor.extract_stakeholders_from_text(
            proposal_text, document_type="technical"
        )
        
        self.logger.info(f"Enhanced extraction found {len(enhanced_stakeholders)} stakeholders")
        
        # If enhanced extraction found stakeholders, use them
        if enhanced_stakeholders:
            return enhanced_stakeholders
        
        # Fallback to original AI-based approach if enhanced extraction finds nothing
        self.logger.info("Falling back to AI-based stakeholder identification...")
        template = requirements_templates.REQUIREMENT_TEMPLATES["stakeholder_template"]  # type: ignore
        
        prompt = template["prompts"]["identification"].format(  # type: ignore
            context=self._prepare_context_text(context)
        )
        
        response = self._call_ai_model(prompt, "requirements_generation")
        ai_stakeholders = self._parse_stakeholder_response(response)
        
        return ai_stakeholders
    
    def generate_functional_requirements(self, 
                                       context: List[Dict], 
                                       phase: str, 
                                       proposal_text: str) -> List[Dict]:
        """Generate functional requirements for specific ARCADIA phase with balanced distribution"""
        template = requirements_templates.REQUIREMENT_TEMPLATES["functional_template"]
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        
        # Analyze components mentioned in the proposal
        components = self.component_analyzer.analyze_components(proposal_text)
        self.logger.info(f"Identified {len(components)} components for {phase} phase: {[c.name for c in components[:5]]}")
        
        # Get component-specific focus
        component_focus = self.component_analyzer.get_component_requirements_focus(components, phase)
        
        # Enhanced prompt with priority balancing guidance
        prompt = template["prompts"]["generation"].format(  # type: ignore
            phase=phase,
            context=self._prepare_context_text(context),
            stakeholders=self._extract_stakeholders_from_context(context),
            phase_description=phase_info.get("description", ""),
            prefix="FR",
            phase_keywords=", ".join(phase_info.get("keywords", []))
        )
        
        # Add enhanced guidance for balanced requirements
        prompt += f"""

COMPONENT-SPECIFIC GUIDANCE:
{component_focus}

ENHANCED GENERATION GUIDELINES:
1. PRIORITY BALANCE (Target: 30% MUST, 50% SHOULD, 20% COULD):
   - Analyze document context for criticality indicators
   - MUST: Only for safety-critical, regulatory, security-essential functions
   - SHOULD: Core operational capabilities and important stakeholder needs
   - COULD: Enhancement features and convenience functions

2. REQUIREMENT COMPLETENESS:
   - Provide complete descriptions (minimum 20 words)
   - Include specific components and measurable criteria
   - Add context from operational capabilities and scenarios

3. VERIFICATION SPECIFICITY:
   - Match verification method to requirement type and phase
   - Use phase-appropriate verification approaches
   - Consider operational scenarios for verification context

4. TRACEABILITY LINKS:
   - Reference operational capabilities where applicable
   - Link to stakeholder needs and scenarios
   - Ensure phase-to-phase traceability

Generate 3-5 well-balanced functional requirements with complete descriptions."""
        
        response = self._call_ai_model(prompt, "requirements_generation")
        
        # Extract stakeholder needs for priority analysis
        stakeholder_needs = self._extract_stakeholder_needs_from_context(context)
        
        requirements = self._parse_requirements_response(
            response, "functional", phase, None, context, stakeholder_needs
        )
        
        # Apply priority balancing post-processing
        requirements = self._balance_priority_distribution(requirements, "functional")
        
        return requirements
    
    def generate_non_functional_requirements(self, 
                                           context: List[Dict], 
                                           phase: str, 
                                           proposal_text: str) -> List[Dict]:
        """Generate balanced non-functional requirements based on context analysis"""
        template = requirements_templates.REQUIREMENT_TEMPLATES["non_functional_template"]
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        
        # Analyze components mentioned in the proposal
        components = self.component_analyzer.analyze_components(proposal_text)
        
        # Context-based NFR category selection (avoid overrepresentation)
        context_text = self._prepare_context_text(context)
        relevant_categories = self._select_relevant_nfr_categories(context_text, proposal_text)
        
        self.logger.info(f"Selected {len(relevant_categories)} relevant NFR categories: {list(relevant_categories.keys())}")
        
        all_nf_requirements = []
        
        for category, priority_weight in relevant_categories.items():
            # Get component-specific focus for this category
            component_focus = self.component_analyzer.get_component_requirements_focus(components, phase)
            
            # Enhanced prompt with context-aware generation
            prompt = template["prompts"]["generation"].format(  # type: ignore
                phase=phase,
                context=context_text,
                category=category,
                phase_keywords=", ".join(phase_info.get("keywords", []))
            )
            
            prompt += f"""

COMPONENT-SPECIFIC GUIDANCE for {category}:
{component_focus}

CONTEXT-AWARE NFR GENERATION:
1. Category Relevance Weight: {priority_weight:.2f}
2. Generate 1-2 requirements for this category (avoid overgeneration)
3. Focus on measurable, specific criteria
4. Link to operational scenarios and capabilities
5. Use appropriate verification methods for {category}

QUALITY REQUIREMENTS:
- Complete descriptions with specific metrics
- Testable acceptance criteria
- Context-appropriate verification methods
- Clear rationale for priority assignment"""
            
            response = self._call_ai_model(prompt, "requirements_generation")
            
            # Extract stakeholder needs for priority analysis
            stakeholder_needs = self._extract_stakeholder_needs_from_context(context)
            
            reqs = self._parse_requirements_response(
                response, "non_functional", phase, category, context, stakeholder_needs
            )
            
            # Limit requirements per category to avoid overrepresentation
            max_reqs_per_category = max(1, int(2 * priority_weight))
            reqs = reqs[:max_reqs_per_category]
            
            all_nf_requirements.extend(reqs)
        
        # Apply priority balancing
        all_nf_requirements = self._balance_priority_distribution(all_nf_requirements, "non_functional")
        
        return all_nf_requirements

    def _select_relevant_nfr_categories(self, context_text: str, proposal_text: str) -> Dict[str, float]:
        """Select relevant NFR categories based on context analysis to avoid overrepresentation"""
        nfr_categories = arcadia_config.REQUIREMENT_CATEGORIES["non_functional"]["subcategories"]  # type: ignore
        combined_text = f"{context_text} {proposal_text}".lower()
        
        category_relevance = {}
        
        for category, info in nfr_categories.items():
            relevance_score = 0.0
            keywords = info.get("keywords", [])
            
            # Calculate keyword presence
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    relevance_score += 1.0
            
            # Normalize by keyword count
            if keywords:
                relevance_score = relevance_score / len(keywords)
            
            # Apply minimum threshold and context boosting
            if relevance_score > 0.1 or category in ["performance", "security"]:  # Always include core categories
                category_relevance[category] = max(0.3, relevance_score)
        
        # Ensure balanced selection (max 4 categories to avoid overrepresentation)
        sorted_categories = sorted(category_relevance.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_categories[:4])

    def _balance_priority_distribution(self, requirements: List[Dict], req_type: str) -> List[Dict]:
        """Balance priority distribution to match ARCADIA best practices"""
        if not requirements:
            return requirements
        
        current_distribution = self._calculate_priority_distribution(requirements)
        total_reqs = len(requirements)
        
        # Calculate target counts
        target_counts = {
            "MUST": int(total_reqs * self.priority_targets["MUST"]),
            "SHOULD": int(total_reqs * self.priority_targets["SHOULD"]),
            "COULD": int(total_reqs * self.priority_targets["COULD"])
        }
        
        # Adjust remaining to reach total
        remaining = total_reqs - sum(target_counts.values())
        target_counts["SHOULD"] += remaining
        
        # Sort requirements by confidence score for intelligent rebalancing
        requirements.sort(key=lambda x: x.get("priority_confidence", 0.5), reverse=True)
        
        # Reassign priorities to match targets
        rebalanced_requirements = []
        priority_counts = {"MUST": 0, "SHOULD": 0, "COULD": 0}
        
        for req in requirements:
            current_priority = req.get("priority", "SHOULD")
            new_priority = current_priority
            
            # Check if we can keep current priority
            if priority_counts[current_priority] < target_counts[current_priority]:
                new_priority = current_priority
            else:
                # Find alternative priority with available slots
                for priority in ["MUST", "SHOULD", "COULD"]:
                    if priority_counts[priority] < target_counts[priority]:
                        new_priority = priority
                        break
            
            req["priority"] = new_priority
            req["priority_rebalanced"] = new_priority != current_priority
            priority_counts[new_priority] += 1
            rebalanced_requirements.append(req)
        
        self.logger.info(f"Priority rebalancing for {req_type}: {priority_counts}")
        return rebalanced_requirements

    def _calculate_priority_distribution(self, requirements: List[Dict]) -> Dict[str, int]:
        """Calculate current priority distribution"""
        distribution = {"MUST": 0, "SHOULD": 0, "COULD": 0}
        for req in requirements:
            priority = req.get("priority", "SHOULD")
            distribution[priority] = distribution.get(priority, 0) + 1
        return distribution

    def _call_ai_model(self, prompt: str, model_type: str) -> str:
        """Call appropriate AI model based on task type"""
        from config import config
        
        model_config = config.AI_MODELS.get(model_type, config.AI_MODELS["requirements_generation"])
        
        try:
            response = self.ollama_client.generate(
                model=model_config["model"],
                prompt=prompt,
                stream=False,
                options={
                    "temperature": model_config["temperature"],
                    "num_predict": model_config["max_tokens"]
                }
            )
            return response['response']
        except Exception as e:
            self.logger.error(f"Error calling AI model: {e}")
            return ""
    
    def _prepare_context_text(self, context: List[Dict]) -> str:
        """Prepare context chunks for AI prompt"""
        return "\n\n".join([chunk["content"] for chunk in context[:5]])  # Limit to 5 chunks
    
    def _extract_stakeholders_from_context(self, context: List[Dict]) -> str:
        """Extract stakeholder mentions from context"""
        stakeholder_patterns = [
            r"stakeholder[s]?",
            r"user[s]?",
            r"actor[s]?",
            r"team[s]?",
            r"organization[s]?",
            r"SOC[s]?",
            r"analyst[s]?"
        ]
        
        stakeholders = set()
        for chunk in context:
            content = chunk["content"].lower()
            for pattern in stakeholder_patterns:
                matches = re.findall(rf"\b\w*{pattern}\w*\b", content)
                stakeholders.update(matches)
        
        return ", ".join(list(stakeholders)[:10])  # Limit to 10 stakeholders
    
    def _extract_stakeholder_needs_from_context(self, context: List[Dict]) -> List[str]:
        """Extract stakeholder needs and requirements from context"""
        needs = []
        needs_patterns = [
            r"need[s]?\s+([^.\n]+)",
            r"require[s]?\s+([^.\n]+)",
            r"want[s]?\s+([^.\n]+)",
            r"expect[s]?\s+([^.\n]+)",
            r"demand[s]?\s+([^.\n]+)"
        ]
        
        for chunk in context:
            content = chunk["content"].lower()
            for pattern in needs_patterns:
                matches = re.findall(pattern, content)
                needs.extend([match.strip() for match in matches if len(match.strip()) > 5])
        
        return needs[:15]  # Limit to 15 needs
    
    def _parse_stakeholder_response(self, response: str) -> Dict:
        """Parse AI response to extract structured stakeholder data"""
        stakeholders = {}
        
        lines = response.split('\n')
        current_stakeholder = None
        current_stakeholder_data = {}
        
        for line in lines:
            line = line.strip()
            
            # Look for stakeholder line: "- [STAKEHOLDER NAME]: [Role description]"
            if line.startswith('-') and ':' in line:
                # Save previous stakeholder if exists
                if current_stakeholder and current_stakeholder_data:
                    stakeholders[current_stakeholder] = current_stakeholder_data
                
                # Parse new stakeholder
                parts = line[1:].split(':', 1)
                if len(parts) == 2:
                    name = parts[0].strip().strip('[]')  # Remove brackets if present
                    description = parts[1].strip()
                    
                    stakeholder_id = f"STK-{self.requirement_counters['stakeholder']:03d}"
                    self.requirement_counters['stakeholder'] += 1
                    
                    current_stakeholder_data = {
                        "id": stakeholder_id,
                        "name": name,
                        "role": description,
                        "interests": [],
                        "responsibilities": [],
                        "influence": "Medium",
                        "requirements": [],
                        "phase": "operational",
                        "type": "general",
                        "extraction_confidence": 0.7,
                        "mentions_count": 1,
                        "contexts": []
                    }
                    current_stakeholder = stakeholder_id
            
            # Parse additional attributes
            elif current_stakeholder and current_stakeholder_data:
                if line.startswith('Interests:'):
                    interests_text = line.replace('Interests:', '').strip()
                    interests = [i.strip() for i in interests_text.split(',') if i.strip()]
                    current_stakeholder_data["interests"] = interests
                
                elif line.startswith('Influence:'):
                    influence = line.replace('Influence:', '').strip()
                    if influence in ['High', 'Medium', 'Low']:
                        current_stakeholder_data["influence"] = influence
                
                elif line.startswith('Requirements:'):
                    requirements_text = line.replace('Requirements:', '').strip()
                    requirements = [r.strip() for r in requirements_text.split(',') if r.strip()]
                    current_stakeholder_data["requirements"] = requirements
                
                elif line.startswith('Phase:'):
                    phase = line.replace('Phase:', '').strip()
                    if phase in ['operational', 'system', 'logical', 'physical']:
                        current_stakeholder_data["phase"] = phase
        
        # Don't forget the last stakeholder
        if current_stakeholder and current_stakeholder_data:
            stakeholders[current_stakeholder] = current_stakeholder_data
        
        self.logger.info(f"Parsed {len(stakeholders)} stakeholders from AI response")
        return stakeholders
    
    def _parse_requirements_response(self, 
                                   response: str, 
                                   req_type: str, 
                                   phase: str, 
                                   category: Optional[str] = None,
                                   context: Optional[List[Dict]] = None,
                                   stakeholder_needs: Optional[List[str]] = None) -> List[Dict]:
        """Enhanced parsing with complete descriptions and specific verification methods"""
        requirements = []
        
        # Enhanced patterns for better extraction
        req_patterns = [
            r"(?:FR|NFR|FUNC|NFUNC)-[\w-]+-\d+",  # Existing ID format
            r"[Tt]he system shall ([^.]+(?:\.[^.]*){0,2})",  # Extended requirement text (up to 3 sentences)
            r"Priority:\s*(MUST|SHOULD|COULD)",    # Priority
            r"Verification:\s*([^.\n]+)",           # Verification method
            r"Rationale:\s*([^.\n]+)"              # Rationale
        ]
        
        lines = response.split('\n')
        current_req = None
        
        for line in lines:
            line = line.strip()
            
            # Enhanced "The system shall" pattern matching
            shall_match = re.search(r"[Tt]he system shall ([^.]+(?:\.[^.]*){0,2})", line)
            if shall_match:
                requirement_text = shall_match.group(1).strip()
                
                # Skip if requirement is too short or generic
                if len(requirement_text.split()) < 5:
                    continue
                
                # Generate requirement ID
                if req_type == "functional":
                    req_id = f"FR-{phase.upper()[:3]}-{self.requirement_counters['functional']:03d}"
                    self.requirement_counters['functional'] += 1
                else:
                    cat_prefix = category.upper()[:4] if category else "NFR"
                    req_id = f"NFR-{cat_prefix}-{self.requirement_counters['non_functional']:03d}"
                    self.requirement_counters['non_functional'] += 1
                
                # Use priority analyzer for intelligent priority assignment
                context_text = self._prepare_context_text(context or [])
                priority, confidence, analysis_details = self.priority_analyzer.analyze_requirement_priority(
                    requirement_text, context_text, phase, stakeholder_needs
                )
                
                # Check if AI model provided explicit priority
                priority_match = re.search(r"Priority:\s*(MUST|SHOULD|COULD)", line)
                if priority_match:
                    explicit_priority = priority_match.group(1)
                    # Use explicit priority if it's more restrictive than analyzed priority
                    priority_order = {"MUST": 3, "SHOULD": 2, "COULD": 1}
                    if priority_order.get(explicit_priority, 0) > priority_order.get(priority, 0):
                        priority = explicit_priority
                
                # Enhanced verification method selection
                verification = self._select_verification_method(req_type, phase, category, requirement_text)
                
                # Extract custom verification if provided
                verification_match = re.search(r"Verification:\s*([^.\n]+)", line)
                if verification_match:
                    custom_verification = verification_match.group(1).strip()
                    if len(custom_verification) > 10:  # Use if substantial
                        verification = custom_verification
                
                # Generate enhanced priority rationale
                priority_rationale = self.priority_analyzer.generate_priority_rationale(priority, analysis_details)
                
                # Enhanced title generation (avoid truncation)
                title = requirement_text if len(requirement_text) <= 60 else f"{requirement_text[:57]}..."
                
                # Complete description with context
                description = f"The system shall {requirement_text}"
                if len(description) < 50:  # Enhance short descriptions
                    description += f" This requirement addresses {phase} phase needs and supports operational capabilities."
                
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
                    "rationale": priority_rationale,
                    "operational_capability_link": self._extract_capability_link(requirement_text, context_text),
                    "stakeholder_traceability": self._extract_stakeholder_links(requirement_text, stakeholder_needs or [])
                }
                
                if req_type == "non_functional" and category:
                    requirement["category"] = category
                    requirement["metric"] = self._extract_metric(requirement_text)
                    requirement["target_value"] = self._extract_target_value(requirement_text)
                
                requirements.append(requirement)
        
        return requirements

    def _select_verification_method(self, req_type: str, phase: str, category: Optional[str], requirement_text: str) -> str:
        """Select appropriate verification method based on requirement characteristics"""
        if req_type == "functional":
            methods = self.verification_methods["functional"].get(phase, ["Review and testing"])
            # Select based on requirement content
            text_lower = requirement_text.lower()
            if "interface" in text_lower or "communication" in text_lower:
                return "Interface testing and integration verification"
            elif "user" in text_lower or "operator" in text_lower:
                return "User acceptance testing and operational validation"
            elif "performance" in text_lower or "response" in text_lower:
                return "Performance testing and system validation"
            else:
                return methods[0] if methods else "Functional testing and verification"
        
        elif req_type == "non_functional" and category:
            methods = self.verification_methods["non_functional"].get(category, ["Testing and analysis"])
            return methods[0] if methods else "Performance testing and analysis"
        
        return "Review and testing"

    def _extract_capability_link(self, requirement_text: str, context: str) -> str:
        """Extract operational capability links for traceability"""
        capability_keywords = ["capability", "mission", "operational", "function", "service"]
        text_lower = requirement_text.lower()
        
        for keyword in capability_keywords:
            if keyword in text_lower:
                return f"Linked to operational {keyword} requirements"
        
        return "General operational capability support"

    def _extract_stakeholder_links(self, requirement_text: str, stakeholder_needs: List[str]) -> List[str]:
        """Extract stakeholder traceability links"""
        links = []
        text_lower = requirement_text.lower()
        
        for need in stakeholder_needs[:5]:  # Limit to top 5 needs
            need_words = need.lower().split()
            if any(word in text_lower for word in need_words if len(word) > 3):
                links.append(f"Addresses stakeholder need: {need[:50]}...")
        
        return links

    def _extract_metric(self, requirement_text: str) -> str:
        """Extract measurable metric from NFR text"""
        metric_patterns = [
            r"(\d+(?:\.\d+)?)\s*(seconds?|minutes?|hours?|ms|milliseconds?)",
            r"(\d+(?:\.\d+)?)\s*(%|percent)",
            r"(\d+(?:\.\d+)?)\s*(MB|GB|TB|bytes?)",
            r"(\d+(?:\.\d+)?)\s*(users?|requests?|transactions?)"
        ]
        
        for pattern in metric_patterns:
            match = re.search(pattern, requirement_text, re.IGNORECASE)
            if match:
                return f"{match.group(1)} {match.group(2)}"
        
        return "Quantitative measure TBD"

    def _extract_target_value(self, requirement_text: str) -> str:
        """Extract target value from NFR text"""
        value_patterns = [
            r"(?:less than|<|under|below)\s*(\d+(?:\.\d+)?)",
            r"(?:greater than|>|above|over)\s*(\d+(?:\.\d+)?)",
            r"(?:at least|minimum|min)\s*(\d+(?:\.\d+)?)",
            r"(?:maximum|max|up to)\s*(\d+(?:\.\d+)?)"
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, requirement_text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "Target value TBD"

    def validate_requirements(self, requirements: List[Dict]) -> Dict:
        """Validate generated requirements for quality and completeness"""
        validation_results = {
            "valid_requirements": [],
            "invalid_requirements": [],
            "warnings": [],
            "quality_score": 0.0
        }
        
        for req in requirements:
            issues = []
            
            # Check mandatory fields
            if not req.get("id"):
                issues.append("Missing requirement ID")
            if not req.get("description"):
                issues.append("Missing requirement description")
            if not req.get("priority") or req["priority"] not in ["MUST", "SHOULD", "COULD"]:
                issues.append("Invalid or missing priority")
            
            # Check requirement quality
            description = req.get("description", "")
            if not re.search(r"\bshall\b", description, re.IGNORECASE):
                issues.append("Requirement should use 'shall' for mandatory statements")
            
            if len(description.split()) < 5:
                issues.append("Requirement description too short")
            
            if issues:
                req["validation_issues"] = issues
                validation_results["invalid_requirements"].append(req)  # type: ignore
            else:
                validation_results["valid_requirements"].append(req)  # type: ignore
        
        # Calculate quality score
        total_reqs = len(requirements)
        valid_reqs = len(validation_results["valid_requirements"])  # type: ignore
        validation_results["quality_score"] = (valid_reqs / total_reqs) * 100 if total_reqs > 0 else 0
        
        return validation_results