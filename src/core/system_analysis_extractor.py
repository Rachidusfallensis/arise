from typing import List, Dict, Any, Optional, Union
import logging
import re
from datetime import datetime
import json

from ..models.arcadia_outputs import (
    SystemActor, SystemBoundary, SystemFunction, SystemCapability, 
    FunctionalChain, SystemAnalysisOutput, ARCADIAPhaseType,
    create_extraction_metadata
)

class SystemAnalysisExtractor:
    """
    Advanced extractor for ARCADIA System Analysis phase.
    
    Extracts structured system analysis outputs from technical documentation:
    - System Actors and Context
    - System Functions  
    - System Capabilities
    - Functional Chains
    """
    
    def __init__(self, ollama_client):
        self.logger = logging.getLogger(__name__)
        self.ollama_client = ollama_client
        
        # Extraction patterns for system elements
        self.extraction_patterns = {
            "system_function_indicators": [
                r"(?i)(function|functionality|feature|service|operation)",
                r"(?i)(process|execute|perform|handle|manage|control)",
                r"(?i)(system shall|system must|system should|system will)"
            ],
            "system_actor_indicators": [
                r"(?i)(external system|interface|connector|adapter)",
                r"(?i)(subsystem|component|module|service)",
                r"(?i)(actor|entity|participant|external)"
            ],
            "capability_indicators": [
                r"(?i)(capability|capacity|ability|functionality)",
                r"(?i)(provides|enables|supports|delivers|implements)",
                r"(?i)(requirement|objective|goal|need)"
            ]
        }
        
        self.logger.info("System Analysis Extractor initialized")
    
    def extract_system_analysis(self, 
                               context_chunks: List[Dict[str, Any]], 
                               proposal_text: str,
                               operational_actors: Optional[List] = None,
                               operational_analysis: Optional[Any] = None,
                               source_documents: Optional[List[str]] = None) -> SystemAnalysisOutput:
        """
        Enhanced system analysis extraction for ARCADIA System Analysis phase:
        - Define Actors, Missions and Capabilities 
        - Refine Operational Activities and describe interactions
        - System Functions, functional Exchanges 
        - Allocate System Functions to System and Actors
        - Functional and Non Functional Requirements
        
        Args:
            context_chunks: Document chunks with metadata
            proposal_text: Full proposal text
            operational_actors: Actors from operational analysis for traceability
            operational_analysis: Complete operational analysis for refinement
            source_documents: List of source document paths
            
        Returns:
            Enhanced system analysis output with refined activities and requirements
        """
        self.logger.info("Starting enhanced system analysis extraction (Formalize System Requirements)")
        
        start_time = datetime.now()
        source_docs = source_documents or ["proposal_text"]
        
        # Step 1: Define System Actors, Missions and Capabilities  
        self.logger.info("Step 1: Defining System Actors, Missions and Capabilities")
        system_actors = self._extract_system_actors(context_chunks, proposal_text)
        system_capabilities = self._extract_system_capabilities(context_chunks, proposal_text, [])
        
        # Step 2: Extract System Functions
        self.logger.info("Step 2: Extracting System Functions") 
        system_functions = self._extract_system_functions(context_chunks, proposal_text, system_actors)
        
        # Step 3: Define system boundary
        self.logger.info("Step 3: Defining system boundary and context")
        system_boundary = self._extract_system_boundary(context_chunks, proposal_text)
        
        # Step 7: Extract functional chains
        functional_chains = self._extract_functional_chains(context_chunks, proposal_text, system_functions)
        
        # Create extraction metadata
        processing_stats = {
            "actors_extracted": len(system_actors),
            "functions_extracted": len(system_functions),
            "capabilities_extracted": len(system_capabilities),
            "functional_chains_extracted": len(functional_chains),
            "processing_time_seconds": (datetime.now() - start_time).total_seconds()
        }
        
        confidence_scores = {
            "actors_confidence": self._calculate_confidence_score(system_actors),
            "functions_confidence": self._calculate_confidence_score(system_functions),
            "capabilities_confidence": self._calculate_confidence_score(system_capabilities),
            "chains_confidence": self._calculate_confidence_score(functional_chains)
        }
        
        metadata = create_extraction_metadata(
            source_docs, start_time, confidence_scores, processing_stats
        )
        
        result = SystemAnalysisOutput(
            system_boundary=system_boundary,
            actors=system_actors,
            functions=system_functions,
            capabilities=system_capabilities,
            functional_chains=functional_chains,
            extraction_metadata=metadata
        )
        
        self.logger.info(f"System analysis extraction completed: {len(system_actors)} actors, "
                        f"{len(system_functions)} functions, {len(system_capabilities)} capabilities, "
                        f"{len(functional_chains)} functional chains")
        
        return result
    
    def _extract_system_boundary(self, context_chunks: List[Dict[str, Any]], 
                                proposal_text: str) -> SystemBoundary:
        """Extract system boundary definition"""
        
        prompt = f"""
SYSTEM BOUNDARY EXTRACTION - ARCADIA Methodology

Extract system boundary and context definition from this documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

PROPOSAL: {proposal_text[:1500]}

TASK: Define clear system boundary, scope, and environmental context.

OUTPUT FORMAT (JSON):
{{
  "boundary": {{
    "scope_definition": "Clear definition of system scope and boundaries",
    "included_elements": ["element 1", "element 2"],
    "excluded_elements": ["excluded element 1", "excluded element 2"],
    "external_dependencies": ["dependency 1", "dependency 2"],
    "environmental_factors": ["factor 1", "factor 2"]
  }}
}}

Focus on defining what is inside vs outside the system.
"""
        
        try:
            response = self.ollama_client.generate(
                model="llama3:instruct",
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            boundary_data = self._parse_boundary_response(response.get('response', ''))
            
            if boundary_data:
                return SystemBoundary(
                    scope_definition=boundary_data.get('scope_definition', 'System boundary definition'),
                    included_elements=boundary_data.get('included_elements', []),
                    excluded_elements=boundary_data.get('excluded_elements', []),
                    external_dependencies=boundary_data.get('external_dependencies', []),
                    environmental_factors=boundary_data.get('environmental_factors', [])
                )
            else:
                return SystemBoundary(scope_definition="Default system boundary from proposal analysis")
                
        except Exception as e:
            self.logger.error(f"Error extracting system boundary: {str(e)}")
            return SystemBoundary(scope_definition="Error in boundary extraction")
    
    def _extract_system_actors(self, context_chunks: List[Dict[str, Any]], 
                              proposal_text: str) -> List[SystemActor]:
        """Extract system-level actors and interfaces"""
        
        prompt = f"""
SYSTEM ACTOR EXTRACTION - ARCADIA Methodology

Extract system-level actors and their interfaces from this documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

PROPOSAL: {proposal_text[:1500]}

TASK: Identify system actors, external systems, and interface specifications.

OUTPUT FORMAT (JSON):
{{
  "actors": [
    {{
      "name": "Actor Name",
      "description": "Actor description",
      "actor_type": "external|internal|interface",
      "interfaces": [
        {{"name": "interface name", "type": "data|control|physical", "description": "interface description"}}
      ],
      "dependencies": ["dependency names"]
    }}
  ]
}}

Focus on system-level actors and their technical interfaces.
"""
        
        try:
            response = self.ollama_client.generate(
                model="llama3:instruct",
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            actors_data = self._parse_json_response(response.get('response', ''), 'actors')
            actors = []
            
            for i, actor_info in enumerate(actors_data):
                if isinstance(actor_info, dict) and 'name' in actor_info:
                    actor = SystemActor(
                        id=f"SA-ACTOR-{i+1:03d}",
                        name=actor_info.get('name', ''),
                        description=actor_info.get('description', ''),
                        actor_type=actor_info.get('actor_type', 'external'),
                        interfaces=actor_info.get('interfaces', []),
                        dependencies=actor_info.get('dependencies', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    actors.append(actor)
            
            self.logger.info(f"Extracted {len(actors)} system actors")
            return actors
            
        except Exception as e:
            self.logger.error(f"Error extracting system actors: {str(e)}")
            return []
    
    def _extract_system_functions(self, context_chunks: List[Dict[str, Any]], 
                                 proposal_text: str,
                                 system_actors: List[SystemActor]) -> List[SystemFunction]:
        """Extract system functions and their hierarchies"""
        
        actor_names = [actor.name for actor in system_actors[:5]]
        
        prompt = f"""
SYSTEM FUNCTION EXTRACTION - ARCADIA Methodology

Extract system functions and their hierarchical relationships.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN ACTORS: {', '.join(actor_names)}

TASK: Extract system functions, their decomposition, and actor allocations.

OUTPUT FORMAT (JSON):
{{
  "functions": [
    {{
      "name": "Function Name",
      "description": "Function description",
      "function_type": "primary|secondary|support",
      "parent_function": "parent function name if applicable",
      "sub_functions": ["sub-function names"],
      "allocated_actors": ["actor names"],
      "functional_exchanges": [
        {{"from": "source", "to": "target", "exchange_type": "data|energy|material", "description": "exchange description"}}
      ],
      "performance_requirements": ["performance requirement 1", "performance requirement 2"]
    }}
  ]
}}

Focus on system-level functions that deliver capabilities.
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
                    # Map actor names to IDs
                    allocated_actor_ids = []
                    for actor_name in func_info.get('allocated_actors', []):
                        matching_actors = [a for a in system_actors if a.name.lower() == actor_name.lower()]
                        if matching_actors:
                            allocated_actor_ids.append(matching_actors[0].id)
                    
                    function = SystemFunction(
                        id=f"SA-FUNCTION-{i+1:03d}",
                        name=func_info.get('name', ''),
                        description=func_info.get('description', ''),
                        function_type=func_info.get('function_type', 'primary'),
                        parent_function=func_info.get('parent_function', None),
                        sub_functions=func_info.get('sub_functions', []),
                        allocated_actors=allocated_actor_ids,
                        functional_exchanges=func_info.get('functional_exchanges', []),
                        performance_requirements=func_info.get('performance_requirements', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    functions.append(function)
            
            self.logger.info(f"Extracted {len(functions)} system functions")
            return functions
            
        except Exception as e:
            self.logger.error(f"Error extracting system functions: {str(e)}")
            return []
    
    def _extract_system_capabilities(self, context_chunks: List[Dict[str, Any]], 
                                   proposal_text: str,
                                   system_functions: List[SystemFunction]) -> List[SystemCapability]:
        """Extract system capabilities and their realizations"""
        
        function_names = [func.name for func in system_functions[:5]]
        
        prompt = f"""
SYSTEM CAPABILITY EXTRACTION - ARCADIA Methodology

Extract system capabilities and their function realizations.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN FUNCTIONS: {', '.join(function_names)}

TASK: Extract system capabilities and map them to implementing functions.

OUTPUT FORMAT (JSON):
{{
  "capabilities": [
    {{
      "name": "Capability Name",
      "description": "Capability description",
      "realized_operational_capabilities": ["operational capability names"],
      "implementing_functions": ["function names"],
      "performance_requirements": [
        {{"requirement": "performance requirement", "metric": "measurement", "target": "target value"}}
      ]
    }}
  ]
}}

Focus on system capabilities that realize operational needs.
"""
        
        try:
            response = self.ollama_client.generate(
                model="llama3:instruct",
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            capabilities_data = self._parse_json_response(response.get('response', ''), 'capabilities')
            capabilities = []
            
            for i, cap_info in enumerate(capabilities_data):
                if isinstance(cap_info, dict) and 'name' in cap_info:
                    # Map function names to IDs
                    implementing_function_ids = []
                    for func_name in cap_info.get('implementing_functions', []):
                        matching_functions = [f for f in system_functions if f.name.lower() == func_name.lower()]
                        if matching_functions:
                            implementing_function_ids.append(matching_functions[0].id)
                    
                    capability = SystemCapability(
                        id=f"SA-CAPABILITY-{i+1:03d}",
                        name=cap_info.get('name', ''),
                        description=cap_info.get('description', ''),
                        realized_operational_capabilities=cap_info.get('realized_operational_capabilities', []),
                        implementing_functions=implementing_function_ids,
                        performance_requirements=cap_info.get('performance_requirements', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    capabilities.append(capability)
            
            self.logger.info(f"Extracted {len(capabilities)} system capabilities")
            return capabilities
            
        except Exception as e:
            self.logger.error(f"Error extracting system capabilities: {str(e)}")
            return []
    
    def _extract_functional_chains(self, context_chunks: List[Dict[str, Any]], 
                                  proposal_text: str,
                                  system_functions: List[SystemFunction]) -> List[FunctionalChain]:
        """Extract functional chains and scenarios"""
        
        function_names = [func.name for func in system_functions[:5]]
        
        prompt = f"""
FUNCTIONAL CHAIN EXTRACTION - ARCADIA Methodology

Extract functional chains showing end-to-end scenarios.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN FUNCTIONS: {', '.join(function_names)}

TASK: Extract functional chains that show complete scenarios from trigger to outcome.

OUTPUT FORMAT (JSON):
{{
  "chains": [
    {{
      "name": "Chain Name",
      "description": "Chain description",
      "scenario_context": "Scenario context or use case",
      "function_sequence": [
        {{"step": 1, "function": "function name", "description": "what happens", "inputs": ["input1"], "outputs": ["output1"]}}
      ],
      "alternative_paths": [
        {{"condition": "alternative condition", "sequence": [{{"step": 1, "function": "alt function"}}]}}
      ],
      "validation_criteria": ["criteria 1", "criteria 2"]
    }}
  ]
}}

Focus on complete end-to-end functional scenarios.
"""
        
        try:
            response = self.ollama_client.generate(
                model="llama3:instruct",
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            chains_data = self._parse_json_response(response.get('response', ''), 'chains')
            chains = []
            
            for i, chain_info in enumerate(chains_data):
                if isinstance(chain_info, dict) and 'name' in chain_info:
                    chain = FunctionalChain(
                        id=f"SA-CHAIN-{i+1:03d}",
                        name=chain_info.get('name', ''),
                        description=chain_info.get('description', ''),
                        scenario_context=chain_info.get('scenario_context', ''),
                        function_sequence=chain_info.get('function_sequence', []),
                        alternative_paths=chain_info.get('alternative_paths', []),
                        validation_criteria=chain_info.get('validation_criteria', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    chains.append(chain)
            
            self.logger.info(f"Extracted {len(chains)} functional chains")
            return chains
            
        except Exception as e:
            self.logger.error(f"Error extracting functional chains: {str(e)}")
            return []
    
    def _prepare_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context text for prompts"""
        context_texts = []
        for chunk in context_chunks:
            content = chunk.get('content', '')
            if len(content) > 400:
                content = content[:400] + "..."
            context_texts.append(content)
        return "\n\n---\n\n".join(context_texts)
    
    def _parse_boundary_response(self, response: str) -> Dict[str, Any]:
        """Parse boundary-specific JSON response"""
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if 'boundary' in data:
                    return data['boundary']
                else:
                    # Try to find boundary data directly
                    return data
        except Exception as e:
            self.logger.warning(f"Failed to parse boundary response: {str(e)}")
        return {}
    
    def _parse_json_response(self, response: str, key: str) -> List[Dict[str, Any]]:
        """Parse JSON from LLM response"""
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if key in data:
                    return data[key]
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON response: {str(e)}")
        return []
    
    def _calculate_confidence_score(self, extracted_elements: List) -> float:
        """Calculate confidence score for extracted elements"""
        if not extracted_elements:
            return 0.0
        
        # Simple confidence calculation
        total_confidence = 0.0
        for element in extracted_elements:
            if hasattr(element, 'source_references') and element.source_references:
                total_confidence += min(len(element.source_references) * 0.3, 1.0)
            else:
                total_confidence += 0.6  # Default confidence
        
        return total_confidence / len(extracted_elements) 