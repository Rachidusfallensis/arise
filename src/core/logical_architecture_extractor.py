from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime
import json

from ..models.arcadia_outputs import (
    LogicalComponent, LogicalFunction, LogicalInterface, LogicalScenario,
    LogicalArchitectureOutput, ARCADIAPhaseType, create_extraction_metadata
)

class LogicalArchitectureExtractor:
    """
    Advanced extractor for ARCADIA Logical Architecture phase.
    
    Extracts structured logical architecture outputs from technical documentation:
    - Logical Components and their hierarchies
    - Logical Functions and behavioral specifications
    - Logical Interfaces and data flows
    - Logical Scenarios and interaction patterns
    """
    
    def __init__(self, ollama_client):
        self.logger = logging.getLogger(__name__)
        self.ollama_client = ollama_client
        
        # Extraction patterns for logical architecture elements
        self.extraction_patterns = {
            "component_indicators": [
                r"(?i)(component|module|subsystem|service|block|element)",
                r"(?i)(logical|software|application|layer|tier)",
                r"(?i)(processor|controller|manager|handler|engine|core)"
            ],
            "function_indicators": [
                r"(?i)(function|operation|behavior|algorithm|logic|method)",
                r"(?i)(processing|calculation|computation|transformation|analysis)",
                r"(?i)(shall|must|will|performs|executes|implements|provides)"
            ],
            "interface_indicators": [
                r"(?i)(interface|api|protocol|connection|link|channel)",
                r"(?i)(data|signal|message|communication|exchange|flow)",
                r"(?i)(input|output|receive|send|transmit|consume|produce)"
            ],
            "scenario_indicators": [
                r"(?i)(interaction|sequence|collaboration|communication|dialogue)",
                r"(?i)(scenario|case|mode|state|condition|situation)",
                r"(?i)(behavior|pattern|workflow|protocol|exchange)"
            ]
        }
        
        # Logical architecture templates
        self.extraction_templates = self._initialize_extraction_templates()
        
        self.logger.info("Logical Architecture Extractor initialized")
    
    def extract_logical_architecture(self, 
                                   context_chunks: List[Dict[str, Any]], 
                                   proposal_text: str,
                                   operational_analysis: Optional[Any] = None,
                                   system_analysis: Optional[Any] = None,
                                   source_documents: Optional[List[str]] = None) -> LogicalArchitectureOutput:
        """
        Extract complete logical architecture from documentation
        
        Args:
            context_chunks: Document chunks with metadata
            proposal_text: Full proposal text
            operational_analysis: Previous operational analysis results for traceability
            system_analysis: Previous system analysis results for traceability
            source_documents: List of source document paths
            
        Returns:
            Complete logical architecture output
        """
        self.logger.info("Starting logical architecture extraction")
        
        start_time = datetime.now()
        source_docs = source_documents or ["proposal_text"]
        
        # Prepare previous analysis context for traceability
        previous_context = self._prepare_previous_analysis_context(operational_analysis, system_analysis)
        
        # Step 1: Extract logical components
        self.logger.info("Step 1: Extracting logical components")
        components = self._extract_logical_components(context_chunks, proposal_text, previous_context)
        
        # Step 2: Extract logical functions
        self.logger.info("Step 2: Extracting logical functions")
        functions = self._extract_logical_functions(context_chunks, proposal_text, components, previous_context)
        
        # Step 3: Extract logical interfaces
        self.logger.info("Step 3: Extracting logical interfaces")
        interfaces = self._extract_logical_interfaces(context_chunks, proposal_text, components, previous_context)
        
        # Step 4: Extract logical scenarios
        self.logger.info("Step 4: Extracting logical scenarios")
        scenarios = self._extract_logical_scenarios(context_chunks, proposal_text, components, functions, previous_context)
        
        # Create extraction metadata
        processing_stats = {
            "components_extracted": len(components),
            "functions_extracted": len(functions),
            "interfaces_extracted": len(interfaces),
            "scenarios_extracted": len(scenarios),
            "processing_time_seconds": (datetime.now() - start_time).total_seconds()
        }
        
        confidence_scores = {
            "components_confidence": self._calculate_extraction_confidence(components, context_chunks),
            "functions_confidence": self._calculate_extraction_confidence(functions, context_chunks),
            "interfaces_confidence": self._calculate_extraction_confidence(interfaces, context_chunks),
            "scenarios_confidence": self._calculate_extraction_confidence(scenarios, context_chunks)
        }
        
        metadata = create_extraction_metadata(
            source_docs, start_time, confidence_scores, processing_stats
        )
        
        result = LogicalArchitectureOutput(
            components=components,
            functions=functions,
            interfaces=interfaces,
            scenarios=scenarios,
            extraction_metadata=metadata
        )
        
        self.logger.info(f"Logical architecture extraction completed: {len(components)} components, "
                        f"{len(functions)} functions, {len(interfaces)} interfaces, "
                        f"{len(scenarios)} scenarios")
        
        return result
    
    def _extract_logical_components(self, context_chunks: List[Dict[str, Any]], 
                                  proposal_text: str,
                                  previous_context: str) -> List[LogicalComponent]:
        """Extract logical components and their hierarchical structure"""
        
        prompt = f"""
LOGICAL COMPONENT EXTRACTION - ARCADIA Methodology

Extract logical components from this technical documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

PREVIOUS ANALYSIS CONTEXT:
{previous_context}

PROPOSAL: {proposal_text[:1500]}

TASK: Identify logical components, subsystems, and their hierarchical organization.

OUTPUT FORMAT (JSON):
{{
  "components": [
    {{
      "name": "Component Name",
      "description": "Component description and purpose",
      "component_type": "subsystem|module|service",
      "responsibilities": ["responsibility descriptions"],
      "parent_component": "parent component name if applicable",
      "sub_components": ["sub-component names"],
      "allocated_functions": ["function names this component realizes"]
    }}
  ]
}}

Focus on logical decomposition and function allocation.
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
                    component = LogicalComponent(
                        id=f"LA-COMP-{i+1:03d}",
                        name=comp_info.get('name', ''),
                        description=comp_info.get('description', ''),
                        component_type=comp_info.get('component_type', 'subsystem'),
                        responsibilities=comp_info.get('responsibilities', []),
                        parent_component=comp_info.get('parent_component'),
                        sub_components=comp_info.get('sub_components', []),
                        interfaces=[],  # Will be populated by interface extractor
                        allocated_functions=comp_info.get('allocated_functions', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    components.append(component)
            
            self.logger.info(f"Extracted {len(components)} logical components")
            return components
            
        except Exception as e:
            self.logger.error(f"Error extracting logical components: {str(e)}")
            return []
    
    def _extract_logical_functions(self, context_chunks: List[Dict[str, Any]], 
                                 proposal_text: str,
                                 components: List[LogicalComponent],
                                 previous_context: str) -> List[LogicalFunction]:
        """Extract logical functions and behavioral specifications"""
        
        component_names = [comp.name for comp in components[:5]]
        
        prompt = f"""
LOGICAL FUNCTION EXTRACTION - ARCADIA Methodology

Extract logical functions from this documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN COMPONENTS: {', '.join(component_names)}

PREVIOUS ANALYSIS CONTEXT:
{previous_context}

TASK: Extract logical functions, behaviors, and their component allocation.

OUTPUT FORMAT (JSON):
{{
  "functions": [
    {{
      "name": "Function Name",
      "description": "Detailed function description",
      "parent_system_function": "parent system function if applicable",
      "sub_functions": ["sub-function names"],
      "input_specifications": ["input descriptions for input_interfaces"],
      "output_specifications": ["output descriptions for output_interfaces"],
      "behavioral_specifications": ["behavior rules for behavioral_models"],
      "allocated_component": "component name for allocated_components"
    }}
  ]
}}

Focus on logical behavior and component-function mapping.
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
                    function = LogicalFunction(
                        id=f"LA-FUNC-{i+1:03d}",
                        name=func_info.get('name', ''),
                        description=func_info.get('description', ''),
                        parent_system_function=func_info.get('parent_system_function'),
                        sub_functions=func_info.get('sub_functions', []),
                        input_interfaces=[{"type": inp} for inp in func_info.get('input_specifications', [])],
                        output_interfaces=[{"type": out} for out in func_info.get('output_specifications', [])],
                        behavioral_models=[{"spec": spec} for spec in func_info.get('behavioral_specifications', [])],
                        allocated_components=[comp for comp in [func_info.get('allocated_component')] if comp is not None],
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    functions.append(function)
            
            self.logger.info(f"Extracted {len(functions)} logical functions")
            return functions
            
        except Exception as e:
            self.logger.error(f"Error extracting logical functions: {str(e)}")
            return []
    
    def _extract_logical_interfaces(self, context_chunks: List[Dict[str, Any]], 
                                  proposal_text: str,
                                  components: List[LogicalComponent],
                                  previous_context: str) -> List[LogicalInterface]:
        """Extract logical interfaces and data flows"""
        
        component_names = [comp.name for comp in components[:5]]
        
        prompt = f"""
LOGICAL INTERFACE EXTRACTION - ARCADIA Methodology

Extract logical interfaces from this documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN COMPONENTS: {', '.join(component_names)}

PREVIOUS ANALYSIS CONTEXT:
{previous_context}

TASK: Extract logical interfaces, data flows, and communication patterns.

OUTPUT FORMAT (JSON):
{{
  "interfaces": [
    {{
      "name": "Interface Name",
      "description": "Interface description and purpose",
      "interface_type": "data|control|user|external|service|api",
      "provider_component": "component providing the interface",
      "consumer_components": ["components using the interface"],
      "data_specifications": ["data types and structures"],
      "protocol_specifications": ["communication protocols"],
      "quality_attributes": {{"attribute": "value"}},
      "supports_system_interfaces": ["system interface names from previous analysis"]
    }}
  ]
}}

Focus on logical communication and data exchange patterns.
"""
        
        try:
            response = self.ollama_client.generate(
                model="llama3:instruct", 
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            interfaces_data = self._parse_json_response(response.get('response', ''), 'interfaces')
            interfaces = []
            
            for i, intf_info in enumerate(interfaces_data):
                if isinstance(intf_info, dict) and 'name' in intf_info:
                    interface = LogicalInterface(
                        id=f"LA-INTF-{i+1:03d}",
                        name=intf_info.get('name', ''),
                        description=intf_info.get('description', ''),
                        interface_type=intf_info.get('interface_type', 'data'),
                        provider_component=intf_info.get('provider_component'),
                        consumer_components=intf_info.get('consumer_components', []),
                        data_specifications=intf_info.get('data_specifications', []),
                        protocol_specifications=intf_info.get('protocol_specifications', []),
                        quality_attributes=intf_info.get('quality_attributes', {}),
                        supports_system_interfaces=intf_info.get('supports_system_interfaces', [])
                    )
                    interfaces.append(interface)
            
            self.logger.info(f"Extracted {len(interfaces)} logical interfaces")
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Error extracting logical interfaces: {str(e)}")
            return []
    
    def _extract_logical_scenarios(self, context_chunks: List[Dict[str, Any]], 
                                 proposal_text: str,
                                 components: List[LogicalComponent],
                                 functions: List[LogicalFunction],
                                 previous_context: str) -> List[LogicalScenario]:
        """Extract logical scenarios and interaction patterns"""
        
        component_names = [comp.name for comp in components[:3]]
        function_names = [func.name for func in functions[:3]]
        
        prompt = f"""
LOGICAL SCENARIO EXTRACTION - ARCADIA Methodology

Extract logical scenarios from this documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN COMPONENTS: {', '.join(component_names)}
KNOWN FUNCTIONS: {', '.join(function_names)}

PREVIOUS ANALYSIS CONTEXT:
{previous_context}

TASK: Extract logical scenarios, interaction patterns, and behavioral sequences.

OUTPUT FORMAT (JSON):
{{
  "scenarios": [
    {{
      "name": "Scenario Name",
      "description": "Scenario description and purpose",
      "scenario_type": "functional|interface|performance|error|nominal",
      "involved_components": ["component names"],
      "involved_functions": ["function names"],
      "interaction_sequence": [
        {{"step": 1, "component": "component name", "function": "function name", "action": "action description"}}
      ],
      "data_flows": [
        {{"from_component": "source", "to_component": "target", "interface": "interface name", "data": "data description"}}
      ],
      "performance_characteristics": {{"metric": "value"}},
      "realizes_operational_scenarios": ["operational scenario names from previous analysis"]
    }}
  ]
}}

Focus on logical behavior and component interactions.
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
                    scenario = LogicalScenario(
                        id=f"LA-SCEN-{i+1:03d}",
                        name=scen_info.get('name', ''),
                        description=scen_info.get('description', ''),
                        scenario_type=scen_info.get('scenario_type', 'functional'),
                        involved_components=scen_info.get('involved_components', []),
                        involved_functions=scen_info.get('involved_functions', []),
                        interaction_sequence=scen_info.get('interaction_sequence', []),
                        data_flows=scen_info.get('data_flows', []),
                        performance_characteristics=scen_info.get('performance_characteristics', {}),
                        realizes_operational_scenarios=scen_info.get('realizes_operational_scenarios', [])
                    )
                    scenarios.append(scenario)
            
            self.logger.info(f"Extracted {len(scenarios)} logical scenarios")
            return scenarios
            
        except Exception as e:
            self.logger.error(f"Error extracting logical scenarios: {str(e)}")
            return []
    
    def _prepare_previous_analysis_context(self, operational_analysis: Optional[Any], 
                                         system_analysis: Optional[Any]) -> str:
        """Prepare context from previous analysis phases for traceability"""
        context_parts = []
        
        if operational_analysis:
            context_parts.append("OPERATIONAL ANALYSIS CONTEXT:")
            if hasattr(operational_analysis, 'actors') and operational_analysis.actors:
                actors = [f"{actor.name}: {actor.role_definition}" for actor in operational_analysis.actors[:3]]
                context_parts.append(f"Key Actors: {', '.join(actors)}")
            
            if hasattr(operational_analysis, 'capabilities') and operational_analysis.capabilities:
                capabilities = [f"{cap.name}: {cap.mission_statement}" for cap in operational_analysis.capabilities[:3]]
                context_parts.append(f"Key Capabilities: {', '.join(capabilities)}")
        
        if system_analysis:
            context_parts.append("SYSTEM ANALYSIS CONTEXT:")
            if hasattr(system_analysis, 'functions') and system_analysis.functions:
                functions = [f"{func.name}: {func.description}" for func in system_analysis.functions[:3]]
                context_parts.append(f"System Functions: {', '.join(functions)}")
            
            if hasattr(system_analysis, 'capabilities') and system_analysis.capabilities:
                capabilities = [f"{cap.name}: {cap.description}" for cap in system_analysis.capabilities[:3]]
                context_parts.append(f"System Capabilities: {', '.join(capabilities)}")
        
        return "\n".join(context_parts) if context_parts else "No previous analysis context available"
    
    def _initialize_extraction_templates(self) -> Dict[str, str]:
        """Initialize extraction templates for logical architecture elements"""
        
        return {
            "component_extraction": """Focus on logical decomposition and architectural organization.""",
            "function_extraction": """Focus on functional behavior and component allocation.""",
            "interface_extraction": """Focus on logical communication and data exchange."""
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