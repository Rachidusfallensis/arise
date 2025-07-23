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
        
        # Remove static patterns - inference will be completely context-driven
        # AI will analyze project domain and generate appropriate suggestions dynamically
        
        # Cache for phase bridging context to avoid regeneration
        self._phase_bridging_cache = {}
    
    def _generate_phase_bridging_context(self, 
                                       context: List[Dict], 
                                       phase: str, 
                                       proposal_text: str,
                                       previous_phase_requirements: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate AI-powered design inference context for Logical/Physical phases
        based on Operational/System analysis results.
        """
        if phase in ["operational", "system"]:
            # These phases work directly from document content
            return {"bridging_context": "", "inferred_components": [], "design_suggestions": []}
        
        # Check cache first
        cache_key = f"{phase}_{hash(proposal_text)}"
        if cache_key in self._phase_bridging_cache:
            return self._phase_bridging_cache[cache_key]
        
        self.logger.info(f"Generating phase bridging context for {phase} phase")
        
        # Extract key elements from proposal and context
        operational_capabilities = self._extract_operational_capabilities(context, proposal_text)
        system_functions = self._extract_system_functions(context, proposal_text, previous_phase_requirements)
        
        # Generate AI-powered design inference
        inference_prompt = self._build_design_inference_prompt(
            phase, proposal_text, operational_capabilities, system_functions
        )
        
        try:
            response = self._call_ai_model(inference_prompt, "requirements_generation")
            bridging_context = self._parse_design_inference_response(response, phase)
            
            # Cache the result
            self._phase_bridging_cache[cache_key] = bridging_context
            
            self.logger.info(f"Generated {len(bridging_context.get('inferred_components', []))} inferred components for {phase}")
            return bridging_context
            
        except Exception as e:
            self.logger.warning(f"Error generating phase bridging context: {e}")
            return {"bridging_context": "", "inferred_components": [], "design_suggestions": []}
    
    def _build_design_inference_prompt(self, 
                                     phase: str, 
                                     proposal_text: str,
                                     operational_capabilities: List[str],
                                     system_functions: List[str]) -> str:
        """Build context-aware AI prompt for domain-specific design inference"""
        
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        
        # First, let AI analyze the project domain and context
        base_prompt = f"""
CONTEXT-AWARE {phase.upper()} ARCHITECTURE INFERENCE

Analyze this project proposal to understand the specific domain and generate contextually appropriate architectural suggestions.

PROJECT PROPOSAL CONTEXT:
{proposal_text[:2000]}

IDENTIFIED OPERATIONAL CAPABILITIES:
{chr(10).join(f"- {cap}" for cap in operational_capabilities[:10])}

IDENTIFIED SYSTEM FUNCTIONS:
{chr(10).join(f"- {func}" for func in system_functions[:10])}

ANALYSIS INSTRUCTIONS:

STEP 1: DOMAIN IDENTIFICATION
Analyze the project context and identify:
- What is the primary domain? (automotive, cybersecurity, healthcare, manufacturing, finance, etc.)
- What are the key technical challenges specific to this domain?
- What are the unique constraints and requirements for this type of system?

STEP 2: CONTEXT-SPECIFIC {phase.upper()} DESIGN INFERENCE
Based on the identified domain and project context, provide domain-appropriate suggestions:

For {phase.upper()} PHASE ({phase_info.get('description', '')}):

1. DOMAIN-SPECIFIC COMPONENTS:
   - Analyze the specific capabilities and functions
   - Suggest 3-5 {phase} components that are SPECIFIC to this project domain
   - Use domain-appropriate terminology and concepts
   - Ensure components directly address the identified operational capabilities

2. CONTEXTUAL ARCHITECTURAL PATTERNS:
   - Suggest architectural patterns appropriate for this specific domain and project type
   - Consider domain-specific constraints (real-time, safety, security, scalability, etc.)
   - Explain why these patterns fit this particular project context

3. DOMAIN-AWARE DESIGN RATIONALE:
   - Explain how the suggested components specifically address this project's needs
   - Reference domain-specific considerations and best practices
   - Justify architectural decisions based on project context

4. PROJECT-SPECIFIC INTERFACES:
   - Suggest interfaces and interactions relevant to this domain
   - Consider domain-specific protocols, standards, and integration needs
   - Address unique communication and data flow requirements

5. CONTEXTUAL IMPLEMENTATION GUIDANCE:
   - Provide technology suggestions appropriate for this domain
   - Consider domain-specific tools, frameworks, and platforms
   - Address deployment and operational considerations specific to this project type

CRITICAL REQUIREMENTS:
- DO NOT use generic component names like "Data Processing Component" or "UI Component"
- USE domain-specific terminology and component names that reflect the actual project context
- ENSURE all suggestions are directly relevant to the identified project domain
- PROVIDE specific, actionable architectural guidance tailored to this exact project type

ARCADIA {phase.upper()} METHODOLOGY FOCUS:
{', '.join(phase_info.get('keywords', []))}"""

        if phase == "logical":
            base_prompt += """

LOGICAL ARCHITECTURE CONTEXT-SPECIFIC REQUIREMENTS:
- Decompose operational capabilities into domain-specific logical components
- Define component responsibilities that reflect the actual project domain
- Specify logical interfaces using domain-appropriate protocols and data formats
- Consider architectural viewpoints relevant to this specific domain
- Address functional allocation based on domain-specific constraints and patterns"""

        elif phase == "physical":
            base_prompt += """

PHYSICAL ARCHITECTURE CONTEXT-SPECIFIC REQUIREMENTS:
- Map logical components to domain-appropriate physical implementation
- Select technologies and platforms suitable for this specific domain
- Define deployment patterns that address domain-specific operational constraints
- Consider hosting and infrastructure appropriate for this project type
- Address performance, security, and scalability concerns specific to this domain"""

        return base_prompt
    
    def _extract_operational_capabilities(self, context: List[Dict], proposal_text: str) -> List[str]:
        """Extract operational capabilities from context and proposal"""
        capabilities = []
        combined_text = f"{proposal_text} {self._prepare_context_text(context)}"
        
        # Patterns for operational capabilities
        capability_patterns = [
            r"capability to ([^.]+)",
            r"able to ([^.]+)",
            r"can ([^.]+)",
            r"provides? ([^.]+)",
            r"enables? ([^.]+)",
            r"supports? ([^.]+)",
            r"performs? ([^.]+)",
            r"executes? ([^.]+)"
        ]
        
        for pattern in capability_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            capabilities.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        # Also extract explicit capability mentions
        capability_keywords = ["monitor", "detect", "analyze", "process", "manage", "secure", "integrate", "report"]
        for keyword in capability_keywords:
            if keyword in combined_text.lower():
                capabilities.append(f"{keyword} data and systems")
        
        return list(set(capabilities))[:15]  # Limit to 15 unique capabilities
    
    def _extract_system_functions(self, 
                                context: List[Dict], 
                                proposal_text: str,
                                previous_requirements: Optional[List[Dict]] = None) -> List[str]:
        """Extract system functions from context and previous phase requirements"""
        functions = []
        combined_text = f"{proposal_text} {self._prepare_context_text(context)}"
        
        # Extract from previous requirements if available
        if previous_requirements:
            for req in previous_requirements:
                if req.get("type") == "Functional":
                    description = req.get("description", "")
                    if "shall" in description:
                        function = description.split("shall", 1)[1].strip()
                        if len(function) > 10:
                            functions.append(function)
        
        # Extract function patterns from text
        function_patterns = [
            r"system (?:shall|must|will) ([^.]+)",
            r"function to ([^.]+)",
            r"responsible for ([^.]+)",
            r"handles? ([^.]+)",
            r"processes? ([^.]+)",
            r"manages? ([^.]+)"
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            functions.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return list(set(functions))[:15]  # Limit to 15 unique functions
    
    def _parse_design_inference_response(self, response: str, phase: str) -> Dict[str, Any]:
        """Parse AI response to extract structured design inference data"""
        
        # Explicitly type as List[str] to avoid Collection[str] issues
        inferred_components: List[str] = []
        architecture_patterns: List[str] = []
        design_suggestions: List[str] = []
        interface_suggestions: List[str] = []
        implementation_guidance: List[str] = []
        
        result: Dict[str, Any] = {
            "bridging_context": response,
            "inferred_components": inferred_components,
            "architecture_patterns": architecture_patterns,
            "design_suggestions": design_suggestions,
            "interface_suggestions": interface_suggestions,
            "implementation_guidance": implementation_guidance
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            line_lower = line.lower()
            if "inferred components" in line_lower or "components" in line_lower and ":" in line:
                current_section = "components"
                continue
            elif "architectural patterns" in line_lower or "patterns" in line_lower and ":" in line:
                current_section = "patterns"
                continue
            elif "design rationale" in line_lower or "rationale" in line_lower and ":" in line:
                current_section = "suggestions"
                continue
            elif "interface" in line_lower and ":" in line:
                current_section = "interfaces"
                continue
            elif "implementation" in line_lower and ":" in line:
                current_section = "implementation"
                continue
            
            # Extract content based on current section
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                content = line[1:].strip()
                if len(content) > 5:
                    if current_section == "components":
                        result["inferred_components"].append(content)
                    elif current_section == "patterns":
                        result["architecture_patterns"].append(content)
                    elif current_section == "suggestions":
                        result["design_suggestions"].append(content)
                    elif current_section == "interfaces":
                        result["interface_suggestions"].append(content)
                    elif current_section == "implementation":
                        result["implementation_guidance"].append(content)
        
        return result
    
    def _format_list_for_prompt(self, items: Any, max_items: int = 5) -> str:
        """Safely format a list for prompt inclusion, handling mixed data types"""
        if not items:
            return "- None identified"
        
        formatted_items = []
        try:
            # Convert to list if needed and limit items
            if isinstance(items, (list, tuple)):
                item_list = list(items)[:max_items]
            else:
                return "- None identified"
            
            for item in item_list:
                if isinstance(item, str):
                    # Already a string
                    formatted_items.append(f"- {item}")
                elif isinstance(item, dict):
                    # Extract name or description from dict
                    if 'name' in item:
                        formatted_items.append(f"- {item['name']}")
                    elif 'description' in item:
                        formatted_items.append(f"- {item['description']}")
                    else:
                        # Convert dict to string representation
                        formatted_items.append(f"- {str(item)[:100]}...")
                else:
                    # Convert other types to string
                    formatted_items.append(f"- {str(item)}")
                
                if len(formatted_items) >= max_items:
                    break
            
            return chr(10).join(formatted_items) if formatted_items else "- None identified"
            
        except Exception as e:
            self.logger.warning(f"Error formatting list for prompt: {e}")
            return "- Format error encountered"
    
    def _format_filtered_list_for_prompt(self, items: Any, filter_keywords: List[str], max_items: int = 3) -> str:
        """Format a list with keyword filtering, handling mixed data types"""
        if not items or not filter_keywords:
            return "- None identified"
        
        try:
            # Convert to list if needed
            if isinstance(items, (list, tuple)):
                item_list = list(items)
            else:
                return "- None identified"
            
            filtered_items = []
            for item in item_list:
                item_str = ""
                
                if isinstance(item, str):
                    item_str = item
                elif isinstance(item, dict):
                    if 'name' in item:
                        item_str = item['name']
                    elif 'description' in item:
                        item_str = item['description']
                    else:
                        item_str = str(item)
                else:
                    item_str = str(item)
                
                # Check if any keyword matches
                if item_str and any(keyword.lower() in item_str.lower() for keyword in filter_keywords):
                    filtered_items.append(f"- {item_str}")
                    
                    if len(filtered_items) >= max_items:
                        break
            
            return chr(10).join(filtered_items) if filtered_items else "- None matching criteria"
            
        except Exception as e:
            self.logger.warning(f"Error filtering list for prompt: {e}")
            return "- Filter error encountered"
    
    def _create_bridging_summary(self, bridging_context: Dict[str, Any], target_phase: str) -> str:
        """Safely create a bridging summary avoiding Collection[str] issues"""
        try:
            components = bridging_context.get('inferred_components', [])
            patterns = bridging_context.get('architecture_patterns', [])
            
            # Safely count items, handling various data types
            components_count = len(list(components)) if components else 0
            patterns_count = len(list(patterns)) if patterns else 0
            
            return f"Generated {components_count} inferred components and {patterns_count} architectural patterns for {target_phase} phase"
            
        except Exception as e:
            self.logger.warning(f"Error creating bridging summary: {e}")
            return f"Phase bridging completed for {target_phase} phase"
    
    def generate_requirements_with_phase_bridging(self,
                                                context: List[Dict],
                                                target_phase: str,
                                                proposal_text: str,
                                                previous_phases_results: Optional[Dict[str, List[Dict]]] = None) -> Dict[str, Any]:
        """
        Generate requirements with AI-powered phase bridging for Logical/Physical phases.
        
        This method is specifically designed to address the challenge where Logical and Physical
        analysis phases often lack direct information in source documents, requiring inference
        from Operational and System analysis results.
        
        Args:
            context: List of document context chunks
            target_phase: ARCADIA phase to generate requirements for ("logical" or "physical" benefit most)
            proposal_text: The original proposal text
            previous_phases_results: Dictionary containing requirements from previous phases
                                   e.g., {"operational": [...], "system": [...]}
                                   
        Returns:
            Dictionary containing generated requirements with phase bridging insights
        """
        self.logger.info(f"Generating requirements with phase bridging for {target_phase} phase")
        
        # Collect previous phase requirements for bridging context
        previous_requirements = []
        if previous_phases_results:
            for phase_results in previous_phases_results.values():
                previous_requirements.extend(phase_results)
        
        # Generate functional requirements with bridging
        functional_reqs = self.generate_functional_requirements(
            context, target_phase, proposal_text, previous_requirements
        )
        
        # Generate non-functional requirements with bridging
        nf_reqs = self.generate_non_functional_requirements(
            context, target_phase, proposal_text, previous_requirements
        )
        
        # Generate additional bridging context for documentation
        bridging_context = self._generate_phase_bridging_context(
            context, target_phase, proposal_text, previous_requirements
        )
        
        results = {
            "phase": target_phase,
            "requirements": {
                "functional": functional_reqs,
                "non_functional": nf_reqs
            },
            "phase_bridging": {
                "enabled": target_phase in ["logical", "physical"],
                "inferred_components": bridging_context.get("inferred_components", []),
                "architecture_patterns": bridging_context.get("architecture_patterns", []),
                "design_suggestions": bridging_context.get("design_suggestions", []),
                "interface_suggestions": bridging_context.get("interface_suggestions", []),
                "implementation_guidance": bridging_context.get("implementation_guidance", []),
                "bridging_summary": self._create_bridging_summary(bridging_context, target_phase)
            },
            "traceability": {
                "source_phases": list(previous_phases_results.keys()) if previous_phases_results else [],
                "bridging_confidence": "high" if bridging_context.get("inferred_components") else "medium"
            }
        }
        
        try:
            summary = results["phase_bridging"]["bridging_summary"]
            self.logger.info(f"Phase bridging completed: {summary}")
        except (KeyError, TypeError):
            self.logger.info(f"Phase bridging completed for {target_phase} phase")
        return results
    
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
                                       proposal_text: str,
                                       previous_phase_requirements: Optional[List[Dict]] = None) -> List[Dict]:
        """Generate functional requirements for specific ARCADIA phase with balanced distribution and phase bridging"""
        template = requirements_templates.REQUIREMENT_TEMPLATES["functional_template"]
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        
        # Analyze components mentioned in the proposal
        components = self.component_analyzer.analyze_components(proposal_text)
        self.logger.info(f"Identified {len(components)} components for {phase} phase: {[c.name for c in components[:5]]}")
        
        # Get component-specific focus
        component_focus = self.component_analyzer.get_component_requirements_focus(components, phase)
        
        # Generate phase bridging context for Logical/Physical phases
        bridging_context = self._generate_phase_bridging_context(
            context, phase, proposal_text, previous_phase_requirements
        )
        
        # Enhanced prompt with priority balancing guidance
        prompt = template["prompts"]["generation"].format(  # type: ignore
            phase=phase,
            context=self._prepare_context_text(context),
            stakeholders=self._extract_stakeholders_from_context(context),
            phase_description=phase_info.get("description", ""),
            prefix="FR",
            phase_keywords=", ".join(phase_info.get("keywords", []))
        )
        
        # Add phase bridging context for Logical/Physical phases
        if phase in ["logical", "physical"] and bridging_context.get("inferred_components"):
            prompt += f"""

DESIGN INFERENCE CONTEXT for {phase.upper()} PHASE:
Based on operational and system analysis, the following architectural elements have been inferred:

INFERRED COMPONENTS:
{self._format_list_for_prompt(bridging_context.get('inferred_components', []), max_items=5)}

ARCHITECTURAL PATTERNS:
{self._format_list_for_prompt(bridging_context.get('architecture_patterns', []), max_items=3)}

DESIGN SUGGESTIONS:
{self._format_list_for_prompt(bridging_context.get('design_suggestions', []), max_items=3)}

INTERFACE CONSIDERATIONS:
{self._format_list_for_prompt(bridging_context.get('interface_suggestions', []), max_items=3)}

Use these inferred architectural elements to generate specific {phase} requirements that address:
1. Component-specific functionality and responsibilities
2. Interface and integration requirements
3. Architectural pattern compliance
4. Implementation and deployment considerations"""

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

5. PHASE-SPECIFIC FOCUS for {phase.upper()}:
   - Address {phase}-specific concerns and constraints
   - Consider architectural decisions and design patterns
   - Include implementation and technology considerations

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
                                           proposal_text: str,
                                           previous_phase_requirements: Optional[List[Dict]] = None) -> List[Dict]:
        """Generate balanced non-functional requirements based on context analysis with phase bridging"""
        template = requirements_templates.REQUIREMENT_TEMPLATES["non_functional_template"]
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        
        # Analyze components mentioned in the proposal
        components = self.component_analyzer.analyze_components(proposal_text)
        
        # Generate phase bridging context for Logical/Physical phases
        bridging_context = self._generate_phase_bridging_context(
            context, phase, proposal_text, previous_phase_requirements
        )
        
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
            
            # Add phase bridging context for Logical/Physical phases
            if phase in ["logical", "physical"] and bridging_context.get("inferred_components"):
                prompt += f"""

DESIGN INFERENCE CONTEXT for {phase.upper()} {category.upper()} NFR:
Based on architectural inference, consider these elements for {category} requirements:

RELEVANT COMPONENTS:
{self._format_filtered_list_for_prompt(bridging_context.get('inferred_components', []), [category, "component", "service"], max_items=3)}

IMPLEMENTATION GUIDANCE:
{self._format_list_for_prompt(bridging_context.get('implementation_guidance', []), max_items=2)}

Focus {category} requirements on these inferred architectural elements."""

            prompt += f"""

COMPONENT-SPECIFIC GUIDANCE for {category}:
{component_focus}

CONTEXT-AWARE NFR GENERATION:
1. Category Relevance Weight: {priority_weight:.2f}
2. Generate 1-2 requirements for this category (avoid overgeneration)
3. Focus on measurable, specific criteria
4. Link to operational scenarios and capabilities
5. Use appropriate verification methods for {category}
6. Consider {phase}-specific architectural constraints and patterns

QUALITY REQUIREMENTS:
- Complete descriptions with specific metrics
- Testable acceptance criteria
- Context-appropriate verification methods
- Clear rationale for priority assignment
- Address architectural and implementation considerations"""
            
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