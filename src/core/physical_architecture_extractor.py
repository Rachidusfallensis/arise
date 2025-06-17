from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime
import json

from ..models.arcadia_outputs import (
    PhysicalComponent, ImplementationConstraint, PhysicalFunction, PhysicalScenario,
    PhysicalArchitectureOutput, ARCADIAPhaseType, create_extraction_metadata
)

class PhysicalArchitectureExtractor:
    """
    Advanced extractor for ARCADIA Physical Architecture phase.
    
    Extracts structured physical architecture outputs from technical documentation:
    - Physical Components (hardware/software implementations)
    - Implementation Constraints and technology limitations
    - Physical Functions with technology specifics
    - Physical Scenarios (deployment, operational, maintenance)
    """
    
    def __init__(self, ollama_client):
        self.logger = logging.getLogger(__name__)
        self.ollama_client = ollama_client
        
        # Extraction patterns for physical architecture elements
        self.extraction_patterns = {
            "component_indicators": [
                r"(?i)(hardware|software|device|equipment|platform|server|workstation)",
                r"(?i)(processor|cpu|memory|storage|network|database|sensor|actuator)",
                r"(?i)(deployment|implementation|installation|configuration|setup)"
            ],
            "constraint_indicators": [
                r"(?i)(constraint|limitation|requirement|standard|specification|compliance)",
                r"(?i)(performance|security|safety|environmental|regulatory|technology)",
                r"(?i)(must|shall|required|mandatory|compliant|certified|approved)"
            ],
            "function_indicators": [
                r"(?i)(implementation|realization|technology|platform|framework|library)",
                r"(?i)(algorithm|code|program|script|driver|firmware|middleware)",
                r"(?i)(resource|memory|cpu|timing|latency|throughput|bandwidth)"
            ],
            "scenario_indicators": [
                r"(?i)(deployment|installation|configuration|maintenance|operation|failure)",
                r"(?i)(startup|shutdown|backup|recovery|upgrade|migration|rollback)",
                r"(?i)(procedure|process|workflow|checklist|guideline|protocol)"
            ]
        }
        
        # Physical architecture templates
        self.extraction_templates = self._initialize_extraction_templates()
        
        self.logger.info("Physical Architecture Extractor initialized")
    
    def extract_physical_architecture(self, 
                                    context_chunks: List[Dict[str, Any]], 
                                    proposal_text: str,
                                    operational_analysis: Optional[Any] = None,
                                    system_analysis: Optional[Any] = None,
                                    logical_architecture: Optional[Any] = None,
                                    source_documents: Optional[List[str]] = None) -> PhysicalArchitectureOutput:
        """
        Extract complete physical architecture from documentation
        
        Args:
            context_chunks: Document chunks with metadata
            proposal_text: Full proposal text
            operational_analysis: Previous operational analysis results
            system_analysis: Previous system analysis results
            logical_architecture: Previous logical architecture results
            source_documents: List of source document paths
            
        Returns:
            Complete physical architecture output
        """
        self.logger.info("Starting physical architecture extraction")
        
        start_time = datetime.now()
        source_docs = source_documents or ["proposal_text"]
        
        # Prepare previous analysis context for traceability
        previous_context = self._prepare_previous_analysis_context(
            operational_analysis, system_analysis, logical_architecture
        )
        
        # Step 1: Extract physical components
        self.logger.info("Step 1: Extracting physical components")
        components = self._extract_physical_components(context_chunks, proposal_text, previous_context)
        
        # Step 2: Extract implementation constraints
        self.logger.info("Step 2: Extracting implementation constraints")
        constraints = self._extract_implementation_constraints(context_chunks, proposal_text, components, previous_context)
        
        # Step 3: Extract physical functions
        self.logger.info("Step 3: Extracting physical functions")
        functions = self._extract_physical_functions(context_chunks, proposal_text, components, previous_context)
        
        # Step 4: Extract physical scenarios
        self.logger.info("Step 4: Extracting physical scenarios")
        scenarios = self._extract_physical_scenarios(context_chunks, proposal_text, components, previous_context)
        
        # Create extraction metadata
        processing_stats = {
            "components_extracted": len(components),
            "constraints_extracted": len(constraints),
            "functions_extracted": len(functions),
            "scenarios_extracted": len(scenarios),
            "processing_time_seconds": (datetime.now() - start_time).total_seconds()
        }
        
        confidence_scores = {
            "components_confidence": self._calculate_extraction_confidence(components, context_chunks),
            "constraints_confidence": self._calculate_extraction_confidence(constraints, context_chunks),
            "functions_confidence": self._calculate_extraction_confidence(functions, context_chunks),
            "scenarios_confidence": self._calculate_extraction_confidence(scenarios, context_chunks)
        }
        
        metadata = create_extraction_metadata(
            source_docs, start_time, confidence_scores, processing_stats
        )
        
        result = PhysicalArchitectureOutput(
            components=components,
            constraints=constraints,
            functions=functions,
            scenarios=scenarios,
            extraction_metadata=metadata
        )
        
        self.logger.info(f"Physical architecture extraction completed: {len(components)} components, "
                        f"{len(constraints)} constraints, {len(functions)} functions, "
                        f"{len(scenarios)} scenarios")
        
        return result
    
    def _extract_physical_components(self, context_chunks: List[Dict[str, Any]], 
                                   proposal_text: str,
                                   previous_context: str) -> List[PhysicalComponent]:
        """Extract physical components (hardware/software implementations)"""
        
        prompt = f"""
PHYSICAL COMPONENT EXTRACTION - ARCADIA Methodology

Extract physical components from this technical documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

PREVIOUS ANALYSIS CONTEXT:
{previous_context}

PROPOSAL: {proposal_text[:1500]}

TASK: Identify physical hardware and software components, their technology platforms, and implementation details.

OUTPUT FORMAT (JSON):
{{
  "components": [
    {{
      "name": "Component Name",
      "description": "Component description and implementation details",
      "component_type": "hardware|software|hybrid",
      "technology_platform": "technology platform or framework",
      "implementing_logical_components": ["logical component names"],
      "interfaces": [{{"name": "interface", "type": "physical interface type"}}],
      "deployment_configuration": {{"property": "value"}},
      "resource_requirements": {{"cpu": "value", "memory": "value", "storage": "value"}}
    }}
  ]
}}

Focus on implementation technology and resource requirements.
"""
        
        try:
            response = self.ollama_client.generate(
                model="llama3:instruct",
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            components_data = self._parse_json_response(response.get('response', ''), 'components')
            components = []
            
            for i, comp_info in enumerate(components_data):
                if isinstance(comp_info, dict) and 'name' in comp_info:
                    component = PhysicalComponent(
                        id=f"PA-COMP-{i+1:03d}",
                        name=comp_info.get('name', ''),
                        description=comp_info.get('description', ''),
                        component_type=comp_info.get('component_type', 'software'),
                        technology_platform=comp_info.get('technology_platform', ''),
                        implementing_logical_components=comp_info.get('implementing_logical_components', []),
                        interfaces=comp_info.get('interfaces', []),
                        deployment_configuration=comp_info.get('deployment_configuration', {}),
                        resource_requirements=comp_info.get('resource_requirements', {}),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    components.append(component)
            
            self.logger.info(f"Extracted {len(components)} physical components")
            return components
            
        except Exception as e:
            self.logger.error(f"Error extracting physical components: {str(e)}")
            return []
    
    def _extract_implementation_constraints(self, context_chunks: List[Dict[str, Any]], 
                                          proposal_text: str,
                                          components: List[PhysicalComponent],
                                          previous_context: str) -> List[ImplementationConstraint]:
        """Extract implementation constraints and technology limitations"""
        
        component_names = [comp.name for comp in components[:5]]
        
        prompt = f"""
IMPLEMENTATION CONSTRAINT EXTRACTION - ARCADIA Methodology

Extract implementation constraints from this documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN COMPONENTS: {', '.join(component_names)}

PREVIOUS ANALYSIS CONTEXT:
{previous_context}

TASK: Extract constraints affecting physical implementation, technology choices, and deployment.

OUTPUT FORMAT (JSON):
{{
  "constraints": [
    {{
      "name": "Constraint Name",
      "description": "Constraint description and impact",
      "constraint_type": "technology|performance|environmental|safety|security|regulatory",
      "affected_components": ["component names"],
      "specifications": {{"parameter": "value", "limit": "threshold"}},
      "validation_criteria": ["validation methods or tests"]
    }}
  ]
}}

Focus on implementation and deployment constraints.
"""
        
        try:
            response = self.ollama_client.generate(
                model="llama3:instruct", 
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            constraints_data = self._parse_json_response(response.get('response', ''), 'constraints')
            constraints = []
            
            for i, const_info in enumerate(constraints_data):
                if isinstance(const_info, dict) and 'name' in const_info:
                    constraint = ImplementationConstraint(
                        id=f"PA-CONST-{i+1:03d}",
                        name=const_info.get('name', ''),
                        description=const_info.get('description', ''),
                        constraint_type=const_info.get('constraint_type', 'technology'),
                        affected_components=const_info.get('affected_components', []),
                        specifications=const_info.get('specifications', {}),
                        validation_criteria=const_info.get('validation_criteria', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    constraints.append(constraint)
            
            self.logger.info(f"Extracted {len(constraints)} implementation constraints")
            return constraints
            
        except Exception as e:
            self.logger.error(f"Error extracting implementation constraints: {str(e)}")
            return []
    
    def _extract_physical_functions(self, context_chunks: List[Dict[str, Any]], 
                                  proposal_text: str,
                                  components: List[PhysicalComponent],
                                  previous_context: str) -> List[PhysicalFunction]:
        """Extract physical functions with technology specifics"""
        
        component_names = [comp.name for comp in components[:5]]
        
        prompt = f"""
PHYSICAL FUNCTION EXTRACTION - ARCADIA Methodology

Extract physical functions from this documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN COMPONENTS: {', '.join(component_names)}

PREVIOUS ANALYSIS CONTEXT:
{previous_context}

TASK: Extract technology-specific function implementations with resource requirements and timing constraints.

OUTPUT FORMAT (JSON):
{{
  "functions": [
    {{
      "name": "Function Name",
      "description": "Function implementation description",
      "implementing_logical_function": "logical function name if applicable",
      "technology_specifics": {{"framework": "value", "language": "value", "platform": "value"}},
      "resource_requirements": {{"cpu": "value", "memory": "value", "bandwidth": "value"}},
      "timing_constraints": [{{"metric": "latency", "value": "threshold"}}],
      "quality_attributes": [{{"attribute": "reliability", "measure": "99.9%"}}]
    }}
  ]
}}

Focus on implementation details and performance characteristics.
"""
        
        try:
            response = self.ollama_client.generate(
                model="llama3:instruct", 
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            functions_data = self._parse_json_response(response.get('response', ''), 'functions')
            functions = []
            
            for i, func_info in enumerate(functions_data):
                if isinstance(func_info, dict) and 'name' in func_info:
                    function = PhysicalFunction(
                        id=f"PA-FUNC-{i+1:03d}",
                        name=func_info.get('name', ''),
                        description=func_info.get('description', ''),
                        implementing_logical_function=func_info.get('implementing_logical_function'),
                        technology_specifics=func_info.get('technology_specifics', {}),
                        resource_requirements=func_info.get('resource_requirements', {}),
                        timing_constraints=func_info.get('timing_constraints', []),
                        quality_attributes=func_info.get('quality_attributes', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    functions.append(function)
            
            self.logger.info(f"Extracted {len(functions)} physical functions")
            return functions
            
        except Exception as e:
            self.logger.error(f"Error extracting physical functions: {str(e)}")
            return []
    
    def _extract_physical_scenarios(self, context_chunks: List[Dict[str, Any]], 
                                  proposal_text: str,
                                  components: List[PhysicalComponent],
                                  previous_context: str) -> List[PhysicalScenario]:
        """Extract physical scenarios (deployment, operational, maintenance)"""
        
        component_names = [comp.name for comp in components[:3]]
        
        prompt = f"""
PHYSICAL SCENARIO EXTRACTION - ARCADIA Methodology

Extract physical scenarios from this documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN COMPONENTS: {', '.join(component_names)}

PREVIOUS ANALYSIS CONTEXT:
{previous_context}

TASK: Extract deployment, operational, and maintenance scenarios with procedures and environmental conditions.

OUTPUT FORMAT (JSON):
{{
  "scenarios": [
    {{
      "name": "Scenario Name",
      "description": "Scenario description and context",
      "scenario_type": "deployment|operational|failure|maintenance",
      "involved_components": ["component names"],
      "procedures": [{{"step": 1, "action": "action description", "component": "component name"}}],
      "environmental_conditions": ["environment specifications"],
      "success_criteria": ["success metrics and validation criteria"]
    }}
  ]
}}

Focus on practical implementation and operational procedures.
"""
        
        try:
            response = self.ollama_client.generate(
                model="llama3:instruct", 
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            scenarios_data = self._parse_json_response(response.get('response', ''), 'scenarios')
            scenarios = []
            
            for i, scen_info in enumerate(scenarios_data):
                if isinstance(scen_info, dict) and 'name' in scen_info:
                    scenario = PhysicalScenario(
                        id=f"PA-SCEN-{i+1:03d}",
                        name=scen_info.get('name', ''),
                        description=scen_info.get('description', ''),
                        scenario_type=scen_info.get('scenario_type', 'operational'),
                        involved_components=scen_info.get('involved_components', []),
                        procedures=scen_info.get('procedures', []),
                        environmental_conditions=scen_info.get('environmental_conditions', []),
                        success_criteria=scen_info.get('success_criteria', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    scenarios.append(scenario)
            
            self.logger.info(f"Extracted {len(scenarios)} physical scenarios")
            return scenarios
            
        except Exception as e:
            self.logger.error(f"Error extracting physical scenarios: {str(e)}")
            return []
    
    def _prepare_previous_analysis_context(self, operational_analysis: Optional[Any], 
                                         system_analysis: Optional[Any],
                                         logical_architecture: Optional[Any]) -> str:
        """Prepare context from previous analysis phases for traceability"""
        context_parts = []
        
        if operational_analysis:
            context_parts.append("OPERATIONAL ANALYSIS CONTEXT:")
            if hasattr(operational_analysis, 'capabilities') and operational_analysis.capabilities:
                capabilities = [f"{cap.name}: {cap.mission_statement}" for cap in operational_analysis.capabilities[:3]]
                context_parts.append(f"Key Capabilities: {', '.join(capabilities)}")
        
        if system_analysis:
            context_parts.append("SYSTEM ANALYSIS CONTEXT:")
            if hasattr(system_analysis, 'functions') and system_analysis.functions:
                functions = [f"{func.name}: {func.description}" for func in system_analysis.functions[:3]]
                context_parts.append(f"System Functions: {', '.join(functions)}")
        
        if logical_architecture:
            context_parts.append("LOGICAL ARCHITECTURE CONTEXT:")
            if hasattr(logical_architecture, 'components') and logical_architecture.components:
                components = [f"{comp.name}: {comp.description}" for comp in logical_architecture.components[:3]]
                context_parts.append(f"Logical Components: {', '.join(components)}")
            
            if hasattr(logical_architecture, 'functions') and logical_architecture.functions:
                functions = [f"{func.name}: {func.description}" for func in logical_architecture.functions[:3]]
                context_parts.append(f"Logical Functions: {', '.join(functions)}")
        
        return "\n".join(context_parts) if context_parts else "No previous analysis context available"
    
    def _initialize_extraction_templates(self) -> Dict[str, str]:
        """Initialize extraction templates for physical architecture elements"""
        
        return {
            "component_extraction": """Focus on hardware/software implementation and technology platforms.""",
            "constraint_extraction": """Focus on implementation and deployment constraints.""",
            "function_extraction": """Focus on technology-specific implementations and performance.""",
            "scenario_extraction": """Focus on deployment, operational, and maintenance procedures."""
        }
    
    def _prepare_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context text for prompts"""
        context_texts = []
        for i, chunk in enumerate(context_chunks):
            content = chunk.get('content', chunk.get('page_content', ''))
            if content:
                context_texts.append(f"Context {i+1}: {content[:300]}...")
        return "\n\n".join(context_texts) if context_texts else "No context available"
    
    def _parse_json_response(self, response: str, key: str) -> List[Dict[str, Any]]:
        """Parse JSON response from LLM"""
        try:
            # Clean up the response to extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return data.get(key, [])
            return []
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON response for {key}: {str(e)}")
            return []
    
    def _calculate_extraction_confidence(self, extracted_elements: List, context_chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for extracted elements"""
        if not extracted_elements or not context_chunks:
            return 0.0
        
        # Simple confidence calculation based on number of elements vs context size
        element_count = len(extracted_elements)
        context_size = sum(len(chunk.get('content', chunk.get('page_content', ''))) for chunk in context_chunks)
        
        # Normalize confidence score
        base_confidence = min(element_count / 5.0, 1.0)  # Expect ~5 elements per analysis
        context_factor = min(context_size / 1000.0, 1.0)  # Good context ~1000 chars
        
        return (base_confidence * 0.7 + context_factor * 0.3) 