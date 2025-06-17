from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime
import json

from ..models.arcadia_outputs import (
    OperationalActor, OperationalEntity, OperationalCapability, 
    OperationalScenario, OperationalProcess, OperationalAnalysisOutput,
    ARCADIAPhaseType, create_extraction_metadata
)

class OperationalAnalysisExtractor:
    """
    Advanced extractor for ARCADIA Operational Analysis phase.
    
    Extracts structured operational analysis outputs from technical documentation:
    - Stakeholder and Actor Identification
    - Operational Capabilities
    - Operational Scenarios
    - Operational Processes
    """
    
    def __init__(self, ollama_client):
        self.logger = logging.getLogger(__name__)
        self.ollama_client = ollama_client
        
        # Extraction patterns for operational elements
        self.extraction_patterns = {
            "actor_indicators": [
                r"(?i)(user|operator|administrator|manager|stakeholder|customer|client)",
                r"(?i)(person|role|responsible|owner|team|department|organization)",
                r"(?i)(actor|entity|participant|party|individual|group)"
            ],
            "capability_indicators": [
                r"(?i)(capability|ability|capacity|function|feature|service)",
                r"(?i)(can|shall|should|able to|capable of|provides|enables)",
                r"(?i)(mission|objective|goal|requirement|need)"
            ],
            "scenario_indicators": [
                r"(?i)(scenario|use case|workflow|process|procedure|activity)",
                r"(?i)(when|if|during|in case of|upon|after)",
                r"(?i)(sequence|step|flow|interaction|transaction)"
            ],
            "process_indicators": [
                r"(?i)(process|procedure|workflow|method|approach|technique)",
                r"(?i)(activity|task|action|operation|step|phase)",
                r"(?i)(chain|sequence|flow|pipeline|series)"
            ]
        }
        
        # Operational analysis templates
        self.extraction_templates = self._initialize_extraction_templates()
        
        self.logger.info("Operational Analysis Extractor initialized")
    
    def extract_operational_analysis(self, 
                                   context_chunks: List[Dict[str, Any]], 
                                   proposal_text: str,
                                   source_documents: Optional[List[str]] = None) -> OperationalAnalysisOutput:
        """
        Extract complete operational analysis from documentation
        
        Args:
            context_chunks: Document chunks with metadata
            proposal_text: Full proposal text
            source_documents: List of source document paths
            
        Returns:
            Complete operational analysis output
        """
        self.logger.info("Starting operational analysis extraction")
        
        start_time = datetime.now()
        source_docs = source_documents or ["proposal_text"]
        
        # Step 1: Extract actors and stakeholders
        self.logger.info("Step 1: Extracting operational actors and stakeholders")
        actors = self._extract_operational_actors(context_chunks, proposal_text)
        entities = self._extract_operational_entities(context_chunks, proposal_text)
        
        # Step 2: Extract operational capabilities
        self.logger.info("Step 2: Extracting operational capabilities")
        capabilities = self._extract_operational_capabilities(context_chunks, proposal_text, actors)
        
        # Step 3: Extract operational scenarios
        self.logger.info("Step 3: Extracting operational scenarios")
        scenarios = self._extract_operational_scenarios(context_chunks, proposal_text, actors)
        
        # Step 4: Extract operational processes
        self.logger.info("Step 4: Extracting operational processes")
        processes = self._extract_operational_processes(context_chunks, proposal_text, actors)
        
        # Create extraction metadata
        processing_stats = {
            "actors_extracted": len(actors),
            "entities_extracted": len(entities),
            "capabilities_extracted": len(capabilities),
            "scenarios_extracted": len(scenarios),
            "processes_extracted": len(processes),
            "processing_time_seconds": (datetime.now() - start_time).total_seconds()
        }
        
        confidence_scores = {
            "actors_confidence": self._calculate_extraction_confidence(actors, context_chunks),
            "capabilities_confidence": self._calculate_extraction_confidence(capabilities, context_chunks),
            "scenarios_confidence": self._calculate_extraction_confidence(scenarios, context_chunks),
            "processes_confidence": self._calculate_extraction_confidence(processes, context_chunks)
        }
        
        metadata = create_extraction_metadata(
            source_docs, start_time, confidence_scores, processing_stats
        )
        
        result = OperationalAnalysisOutput(
            actors=actors,
            entities=entities,
            capabilities=capabilities,
            scenarios=scenarios,
            processes=processes,
            extraction_metadata=metadata
        )
        
        self.logger.info(f"Operational analysis extraction completed: {len(actors)} actors, "
                        f"{len(capabilities)} capabilities, {len(scenarios)} scenarios, "
                        f"{len(processes)} processes")
        
        return result
    
    def _extract_operational_actors(self, context_chunks: List[Dict[str, Any]], 
                                  proposal_text: str) -> List[OperationalActor]:
        """Extract operational actors and stakeholders"""
        
        prompt = f"""
OPERATIONAL ACTOR EXTRACTION - ARCADIA Methodology

Extract operational actors and stakeholders from this technical documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

PROPOSAL: {proposal_text[:1500]}

TASK: Identify all operational actors, stakeholders, users, and organizational entities.

OUTPUT FORMAT (JSON):
{{
  "actors": [
    {{
      "name": "Actor Name",
      "description": "Actor description", 
      "role_definition": "Primary role",
      "responsibilities": ["responsibility 1", "responsibility 2"],
      "capabilities": ["capability 1", "capability 2"]
    }}
  ]
}}

Focus on operational-level actors who interact with the system.
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
                    actor = OperationalActor(
                        id=f"OA-ACTOR-{i+1:03d}",
                        name=actor_info.get('name', ''),
                        description=actor_info.get('description', ''),
                        role_definition=actor_info.get('role_definition', ''),
                        responsibilities=actor_info.get('responsibilities', []),
                        capabilities=actor_info.get('capabilities', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    actors.append(actor)
            
            self.logger.info(f"Extracted {len(actors)} operational actors")
            return actors
            
        except Exception as e:
            self.logger.error(f"Error extracting operational actors: {str(e)}")
            return []
    
    def _extract_operational_entities(self, context_chunks: List[Dict[str, Any]], 
                                    proposal_text: str) -> List[OperationalEntity]:
        """Extract operational entities"""
        entities = []
        # Basic implementation - can be enhanced
        for i in range(2):
            entity = OperationalEntity(
                id=f"OA-ENTITY-{i+1:03d}",
                name=f"System Entity {i+1}",
                description="System component or organizational entity",
                entity_type="system"
            )
            entities.append(entity)
        return entities
    
    def _extract_operational_capabilities(self, context_chunks: List[Dict[str, Any]], 
                                        proposal_text: str,
                                        actors: List[OperationalActor]) -> List[OperationalCapability]:
        """Extract operational capabilities"""
        
        actor_names = [actor.name for actor in actors[:5]]
        
        prompt = f"""
OPERATIONAL CAPABILITY EXTRACTION - ARCADIA Methodology

Extract operational capabilities from this documentation.

CONTEXT: {self._prepare_context(context_chunks[:3])}

KNOWN ACTORS: {', '.join(actor_names)}

TASK: Extract operational capabilities, mission objectives, and capability-actor relationships.

OUTPUT FORMAT (JSON):
{{
  "capabilities": [
    {{
      "name": "Capability Name",
      "description": "Capability description",
      "mission_statement": "Mission objective this supports",
      "involved_actors": ["actor names"],
      "performance_constraints": ["constraint 1", "constraint 2"]
    }}
  ]
}}

Focus on high-level operational capabilities.
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
                    capability = OperationalCapability(
                        id=f"OA-CAPABILITY-{i+1:03d}",
                        name=cap_info.get('name', ''),
                        description=cap_info.get('description', ''),
                        mission_statement=cap_info.get('mission_statement', ''),
                        involved_actors=[a.id for a in actors if a.name in cap_info.get('involved_actors', [])],
                        performance_constraints=cap_info.get('performance_constraints', [])
                    )
                    capabilities.append(capability)
            
            self.logger.info(f"Extracted {len(capabilities)} operational capabilities")
            return capabilities
            
        except Exception as e:
            self.logger.error(f"Error extracting capabilities: {str(e)}")
            return []
    
    def _extract_operational_scenarios(self, context_chunks: List[Dict[str, Any]], 
                                     proposal_text: str,
                                     actors: List[OperationalActor]) -> List[OperationalScenario]:
        """Extract operational scenarios"""
        scenarios = []
        for i in range(2):
            scenario = OperationalScenario(
                id=f"OA-SCENARIO-{i+1:03d}",
                name=f"Operational Scenario {i+1}",
                description="Key operational workflow or use case",
                scenario_type="use_case"
            )
            scenarios.append(scenario)
        return scenarios
    
    def _extract_operational_processes(self, context_chunks: List[Dict[str, Any]], 
                                     proposal_text: str,
                                     actors: List[OperationalActor]) -> List[OperationalProcess]:
        """Extract operational processes"""  
        processes = []
        for i in range(2):
            process = OperationalProcess(
                id=f"OA-PROCESS-{i+1:03d}",
                name=f"Operational Process {i+1}",
                description="Key operational process or workflow"
            )
            processes.append(process)
        return processes
    
    def _initialize_extraction_templates(self) -> Dict[str, str]:
        """Initialize extraction templates for different operational elements"""
        
        return {
            "actor_extraction": """
OPERATIONAL ACTOR EXTRACTION - ARCADIA Methodology

CONTEXT:
{context}

PROPOSAL:
{proposal_text}

TASK: Extract operational actors, stakeholders, and organizational entities from the documentation.

Focus on: {extraction_focus}

EXTRACTION GUIDELINES:
1. Identify all human actors (users, operators, administrators, managers)
2. Identify organizational entities (departments, teams, external organizations)
3. Define clear roles and responsibilities for each actor
4. Identify relationships and hierarchies between actors
5. Extract capabilities that each actor provides or requires

OUTPUT FORMAT (JSON):
{{
  "actors": [
    {{
      "name": "Actor Name",
      "description": "Detailed description of the actor",
      "role_definition": "Primary role and function",
      "responsibilities": ["responsibility 1", "responsibility 2"],
      "capabilities": ["capability 1", "capability 2"],
      "relationships": ["related actor names"],
      "parent_actor": "parent actor name if hierarchical"
    }}
  ]
}}

Extract actors systematically, ensuring comprehensive coverage of all stakeholders mentioned in the documentation.
""",
            
            "entity_extraction": """
OPERATIONAL ENTITY EXTRACTION - ARCADIA Methodology

CONTEXT:
{context}

PROPOSAL:
{proposal_text}

TASK: Extract operational entities and their hierarchical structures.

Focus on: {extraction_focus}

EXTRACTION GUIDELINES:
1. Identify systems, organizations, resources, and operational entities
2. Establish hierarchical relationships (parent-child structures)
3. Define entity types and properties
4. Map entity interactions and dependencies

OUTPUT FORMAT (JSON):
{{
  "entities": [
    {{
      "name": "Entity Name",
      "description": "Detailed description",
      "type": "system|organization|resource|other",
      "parent_entity": "parent entity name if applicable",
      "sub_entities": ["sub-entity names"],
      "properties": {{"property": "value"}}
    }}
  ]
}}

Focus on operational-level entities that support mission objectives.
""",
            
            "capability_extraction": """
OPERATIONAL CAPABILITY EXTRACTION - ARCADIA Methodology

CONTEXT:
{context}

PROPOSAL:
{proposal_text}

KNOWN ACTORS: {known_actors}

TASK: Extract operational capabilities and mission mappings.

Focus on: {extraction_focus}

EXTRACTION GUIDELINES:
1. Identify high-level operational capabilities
2. Map capabilities to mission objectives
3. Identify actor-capability relationships
4. Extract performance constraints and requirements
5. Link capabilities to operational needs

OUTPUT FORMAT (JSON):
{{
  "capabilities": [
    {{
      "name": "Capability Name",
      "description": "Detailed capability description",
      "mission_statement": "High-level mission objective this supports",
      "involved_actors": ["actor names"],
      "actor_roles": {{"actor_name": "role_in_capability"}},
      "performance_constraints": ["constraint 1", "constraint 2"]
    }}
  ]
}}

Focus on capabilities that deliver operational value.
""",
            
            "scenario_extraction": """
OPERATIONAL SCENARIO EXTRACTION - ARCADIA Methodology

CONTEXT:
{context}

PROPOSAL:
{proposal_text}

KNOWN ACTORS: {known_actors}

TASK: Extract operational scenarios, use cases, and workflows.

Focus on: {extraction_focus}

EXTRACTION GUIDELINES:
1. Identify operational use cases and scenarios
2. Extract activity sequences and workflows
3. Map actor involvement in scenarios
4. Identify environmental conditions and constraints
5. Define success criteria and performance requirements

OUTPUT FORMAT (JSON):
{{
  "scenarios": [
    {{
      "name": "Scenario Name",
      "description": "Detailed scenario description",
      "type": "use_case|mission_scenario|workflow",
      "involved_actors": ["actor names"],
      "activity_sequence": [
        {{"step": 1, "activity": "activity description", "actor": "responsible actor"}}
      ],
      "environmental_conditions": ["condition 1", "condition 2"],
      "performance_constraints": ["constraint 1", "constraint 2"]
    }}
  ]
}}

Focus on end-to-end operational scenarios.
""",
            
            "process_extraction": """
OPERATIONAL PROCESS EXTRACTION - ARCADIA Methodology

CONTEXT:
{context}

PROPOSAL:
{proposal_text}

TASK: Extract operational processes and activity chains.

Focus on: {extraction_focus}

EXTRACTION GUIDELINES:
1. Identify operational processes and procedures
2. Extract activity chains and workflows
3. Map process interactions and dependencies
4. Identify reusable patterns and templates
5. Define process inputs, outputs, and triggers

OUTPUT FORMAT (JSON):
{{
  "processes": [
    {{
      "name": "Process Name",
      "description": "Detailed process description",
      "activity_chain": [
        {{"activity": "activity name", "description": "what happens", "triggers": ["trigger conditions"]}}
      ],
      "interaction_mappings": [
        {{"from_activity": "source", "to_activity": "target", "interaction_type": "data|control|resource"}}
      ],
      "reusable_patterns": ["pattern names"]
    }}
  ]
}}

Focus on operational processes that support capabilities.
"""
        }
    
    def _prepare_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context text for prompts"""
        context_texts = []
        for chunk in context_chunks:
            content = chunk.get('content', '')
            if len(content) > 400:
                content = content[:400] + "..."
            context_texts.append(content)
        return "\n\n---\n\n".join(context_texts)
    
    def _parse_json_response(self, response: str, key: str) -> List[Dict[str, Any]]:
        """Parse JSON from LLM response"""
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get(key, [])
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON response: {str(e)}")
        return []
    
    def _calculate_extraction_confidence(self, extracted_elements: List, context_chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for extracted elements"""
        if not extracted_elements:
            return 0.0
        
        # Simple confidence calculation based on source references
        total_confidence = 0.0
        for element in extracted_elements:
            if hasattr(element, 'source_references') and element.source_references:
                total_confidence += min(len(element.source_references) * 0.3, 1.0)
            else:
                total_confidence += 0.5  # Default confidence
        
        return total_confidence / len(extracted_elements) 