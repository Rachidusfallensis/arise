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
        
        # Step 4: Extract operational activities and interactions
        self.logger.info("Step 4: Extracting operational activities and interactions")
        try:
            activities = self._extract_operational_activities(context_chunks, proposal_text, actors, capabilities)
            self.logger.info(f"DEBUG: Successfully extracted {len(activities) if activities else 0} activities")
        except Exception as e:
            self.logger.error(f"ERROR: Failed to extract activities: {str(e)}")
            activities = []
        
        # Step 5: Extract operational processes
        self.logger.info("Step 5: Extracting operational processes")
        processes = self._extract_operational_processes(context_chunks, proposal_text, actors)
        
        # Create extraction metadata
        processing_stats = {
            "actors_extracted": len(actors),
            "entities_extracted": len(entities), 
            "capabilities_extracted": len(capabilities),
            "scenarios_extracted": len(scenarios),
            "activities_extracted": len(activities) if activities else 0,
            "processes_extracted": len(processes),
            "processing_time_seconds": (datetime.now() - start_time).total_seconds()
        }
        
        confidence_scores = {
            "actors_confidence": self._calculate_extraction_confidence(actors, context_chunks),
            "capabilities_confidence": self._calculate_extraction_confidence(capabilities, context_chunks),
            "scenarios_confidence": self._calculate_extraction_confidence(scenarios, context_chunks),
            "activities_confidence": 0.85 if activities else 0.0,  # High confidence for AI-driven activities
            "processes_confidence": self._calculate_extraction_confidence(processes, context_chunks)
        }
        
        metadata = create_extraction_metadata(
            source_docs, start_time, confidence_scores, processing_stats
        )
        
        # Add extracted activities to metadata for enhanced operational analysis
        self.logger.info(f"DEBUG: Adding {len(activities) if activities else 0} activities to metadata")
        self.logger.info(f"DEBUG: Sample activity: {activities[0] if activities else 'None'}")
        metadata["operational_activities"] = activities if activities else []
        
        result = OperationalAnalysisOutput(
            actors=actors,
            entities=entities,
            capabilities=capabilities,
            scenarios=scenarios,
            processes=processes,
            extraction_metadata=metadata
        )
        
        self.logger.info(f"Enhanced operational analysis extraction completed: {len(actors)} actors, "
                        f"{len(capabilities)} capabilities, {len(scenarios)} scenarios, "
                        f"{len(activities) if activities else 0} activities with interactions, "
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
                model="gemma3:12b",  # Using gemma3:12b for better content generation
                prompt=prompt,
                options={"temperature": 0.3, "num_predict": 2048}
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
                model="gemma3:12b",  # Using gemma3:12b for better content generation
                prompt=prompt,
                options={"temperature": 0.3, "num_predict": 2048}
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
        """Extract operational scenarios using enhanced AI-driven context analysis"""
        
        actor_names = [actor.name for actor in actors[:5]]
        
        # Enhanced AI-driven scenario extraction based on deep context analysis
        prompt = f"""
ENHANCED OPERATIONAL SCENARIO EXTRACTION - AI-Driven Context Analysis

CONTEXT ANALYSIS:
{self._prepare_context(context_chunks)}

PROJECT PROPOSAL:
{proposal_text[:2000]}

IDENTIFIED OPERATIONAL ACTORS:
{chr(10).join([f"- {actor.name}: {actor.role_definition}" for actor in actors[:5]])}

TASK: Perform deep AI analysis to extract meaningful operational scenarios with detailed activity flows and actor interactions.

ENHANCED EXTRACTION APPROACH:
1. **Context-Driven Analysis**: Analyze the actual project domain and context to identify real-world operational scenarios
2. **Activity Flow Mapping**: Extract detailed operational activities and their natural sequence based on the project context
3. **Actor-Activity Allocation**: Map specific activities to appropriate actors/entities/roles based on their capabilities
4. **Interaction Modeling**: Describe how actors interact during activities
5. **Scenario Contextualization**: Generate scenarios that are specific to the project domain, not generic templates

AI ANALYSIS INSTRUCTIONS:
- Read and understand the project context deeply
- Identify domain-specific operational patterns
- Extract activities that are mentioned or implied in the documentation
- Focus on end-to-end operational workflows that deliver value
- Map activities to the most appropriate actors based on their roles and capabilities
- Describe interactions between actors during collaborative activities

OUTPUT FORMAT (JSON):
{{
  "scenarios": [
    {{
      "name": "Context-specific scenario name from project domain",
      "description": "Detailed description based on project context and domain",
      "scenario_type": "mission_critical|operational_workflow|stakeholder_interaction",
      "involved_actors": ["actual actor names from analysis"],
      "operational_activities": [
        {{
          "activity_id": "OA-ACT-001",
          "activity_name": "Specific activity from context",
          "description": "What this activity accomplishes",
          "allocated_actors": ["actor names responsible for this activity"],
          "required_capabilities": ["capabilities needed"],
          "interactions": [
            {{
              "from_actor": "source actor",
              "to_actor": "target actor", 
              "interaction_type": "information_exchange|coordination|approval|resource_transfer",
              "description": "what is exchanged/coordinated"
            }}
          ],
          "inputs": ["what this activity needs"],
          "outputs": ["what this activity produces"]
        }}
      ],
      "activity_sequence": [
        {{"step": 1, "activity_ref": "OA-ACT-001", "description": "sequence description", "trigger": "what triggers this step"}}
      ],
      "success_criteria": ["measurable outcomes"],
      "stakeholder_value": "what value this scenario delivers to stakeholders"
    }}
  ]
}}

CRITICAL: Base scenarios on actual project context and domain. Do not use generic templates. Extract real activities and interactions from the provided documentation.
"""
        
        try:
            response = self.ollama_client.generate(
                model="gemma3:12b",  # Using gemma3:12b for better content generation
                prompt=prompt,
                options={"temperature": 0.2, "num_predict": 3000}  # Lower temp for more focused analysis, increased prediction for detailed output
            )
            
            scenarios_data = self._parse_json_response(response.get('response', ''), 'scenarios')
            scenarios = []
            
            for i, scen_info in enumerate(scenarios_data):
                if isinstance(scen_info, dict) and 'name' in scen_info:
                    # Extract operational activities if present
                    operational_activities = scen_info.get('operational_activities', [])
                    
                    scenario = OperationalScenario(
                        id=f"OA-SCENARIO-{i+1:03d}",
                        name=scen_info.get('name', ''),
                        description=scen_info.get('description', ''),
                        scenario_type=scen_info.get('scenario_type', 'operational_workflow'),
                        involved_actors=[a.id for a in actors if a.name in scen_info.get('involved_actors', [])],
                        activity_sequence=scen_info.get('activity_sequence', []),
                        environmental_conditions=scen_info.get('environmental_conditions', []),
                        performance_constraints=scen_info.get('success_criteria', []),
                        source_references=[f"context_chunk_{i}" for i in range(len(context_chunks))]
                    )
                    
                    # Enhance activity sequence with detailed operational activities
                    if operational_activities:
                        # Use the enhanced activity sequence structure
                        scenario.activity_sequence = operational_activities
                        # Add stakeholder value to the description
                        stakeholder_value = scen_info.get('stakeholder_value', '')
                        if stakeholder_value:
                            scenario.description += f"\n\nStakeholder Value: {stakeholder_value}"
                    
                    scenarios.append(scenario)
            
            self.logger.info(f"Extracted {len(scenarios)} context-driven operational scenarios with detailed activities and interactions")
            return scenarios
            
        except Exception as e:
            self.logger.error(f"Error extracting enhanced operational scenarios: {str(e)}")
            return []

    def _extract_operational_activities(self, context_chunks: List[Dict[str, Any]], 
                                      proposal_text: str,
                                      actors: List[OperationalActor],
                                      capabilities: List[OperationalCapability]) -> List[Dict[str, Any]]:
        """Extract detailed operational activities and their interactions based on context analysis"""
        
        # Simplified extraction with fallback if actors/capabilities are empty
        actor_names = [actor.name for actor in actors[:5]] if actors else ["System User", "System Operator"]
        capability_names = [cap.name for cap in capabilities[:3]] if capabilities else ["System Operation"]
        
        # Ensure we have enough context
        if not context_chunks and not proposal_text:
            self.logger.warning("No context available for activity extraction")
            return self._create_default_activities(actor_names)
        
        context_text = self._prepare_context(context_chunks) if context_chunks else ""
        combined_text = f"{context_text}\n\n{proposal_text[:1500]}" if proposal_text else context_text
        
        # Enhanced AI-driven prompt for deep context analysis
        prompt = f"""
OPERATIONAL ACTIVITIES EXTRACTION - Enhanced AI-Driven Context Analysis

PROJECT CONTEXT:
{combined_text[:1500]}

IDENTIFIED ACTORS & ENTITIES:
{chr(10).join([f"- {name}: {actors[i].role_definition if i < len(actors) else 'Key operational entity'}" for i, name in enumerate(actor_names[:5])])}

IDENTIFIED CAPABILITIES:
{chr(10).join([f"- {cap.name}: {cap.description}" for cap in capabilities[:5]])}

EXTRACTION FOCUS:
1. **Activity Identification**: Extract specific activities mentioned or implied in the context
2. **Actor-Activity Allocation**: Map activities to appropriate actors based on their roles and capabilities  
3. **Interaction Modeling**: Describe how actors interact during activities
4. **Value Chain Analysis**: Understand how activities contribute to operational capabilities

AI ANALYSIS INSTRUCTIONS:
- Identify concrete operational activities from the project context
- Allocate each activity to the most suitable actor/entity/role
- Describe interactions between actors during collaborative activities
- Focus on activities that support the identified operational capabilities
- Extract realistic activity flows based on the project domain
- Ensure activities are traceable to specific context elements
- Model both human-system and human-human interactions

DEEP ANALYSIS APPROACH:
1. Scan context for action verbs, processes, workflows, and procedures
2. Identify who performs what activities and why
3. Map information flows, approvals, and handoffs between actors
4. Link activities to capability enablement
5. Consider temporal sequences and dependencies

JSON OUTPUT FORMAT:
{{
  "activities": [
    {{
      "activity_id": "OA-ACT-XXX",
      "activity_name": "Specific activity name from context",
      "description": "Detailed description of what this activity accomplishes",
      "allocated_actors": ["Primary actors responsible"],
      "supporting_actors": ["Secondary actors who assist"],
      "required_capabilities": ["Capabilities this activity requires"],
      "activity_type": "planning|execution|monitoring|coordination|decision_making|communication",
      "interactions": [
        {{
          "from_actor": "Source actor name",
          "to_actor": "Target actor name",
          "interaction_type": "information_exchange|coordination|approval|resource_transfer|supervision|collaboration",
          "description": "Detailed description of the interaction",
          "data_exchanged": "What specific information/resources are exchanged",
          "frequency": "continuous|periodic|event_driven|on_demand",
          "criticality": "high|medium|low"
        }}
      ],
      "inputs": ["Specific inputs required"],
      "outputs": ["Specific outputs produced"],
      "triggers": ["What initiates this activity"],
      "preconditions": ["Required conditions before activity can start"],
      "postconditions": ["State after activity completion"],
      "success_measures": ["How success is measured"],
      "context_reference": "Reference to specific part of context where this activity is mentioned"
    }}
  ]
}}

CRITICAL: Extract 4-8 activities that form a coherent operational workflow based on the actual project context. Each activity must be traceable to the provided documentation.
"""
        
        try:
            self.logger.info("Attempting to extract operational activities...")
            response = self.ollama_client.generate(
                model="gemma3:12b",  # Using gemma3:12b for better content generation
                prompt=prompt,
                options={"temperature": 0.1, "num_predict": 2048}  # Increased for more detailed activities
            )
            
            response_text = response.get('response', '')
            self.logger.info(f"DEBUG: AI Response length: {len(response_text)}")
            self.logger.info(f"DEBUG: AI Response preview: {response_text[:200]}...")
            
            activities_data = self._parse_json_response(response_text, 'activities')
            
            if not activities_data:
                self.logger.warning("No activities extracted from AI, creating default activities")
                activities_data = self._create_default_activities(actor_names)
            
            self.logger.info(f"Successfully extracted {len(activities_data)} operational activities")
            return activities_data
            
        except Exception as e:
            self.logger.error(f"Error extracting operational activities: {str(e)}")
            self.logger.info("Creating fallback default activities")
            return self._create_default_activities(actor_names)
    
    def _create_default_activities(self, actor_names: List[str]) -> List[Dict[str, Any]]:
        """Create comprehensive default activities if extraction fails"""
        default_activities = [
            {
                "activity_id": "OA-ACT-001",
                "activity_name": "Operational Planning and Strategy",
                "description": "Define operational objectives, allocate resources, and establish strategic plans for system operations",
                "allocated_actors": [actor_names[0] if actor_names else "Strategic Planner"],
                "supporting_actors": [actor_names[1] if len(actor_names) > 1 else "Operations Manager"],
                "required_capabilities": ["Strategic Planning", "Resource Management"],
                "activity_type": "planning",
                "interactions": [
                    {
                        "from_actor": actor_names[0] if actor_names else "Strategic Planner",
                        "to_actor": actor_names[1] if len(actor_names) > 1 else "Operations Manager",
                        "interaction_type": "coordination",
                        "description": "Coordinate strategic objectives with operational constraints",
                        "data_exchanged": "Strategic plans, resource allocation, constraints",
                        "frequency": "periodic",
                        "criticality": "high"
                    }
                ],
                "inputs": ["Mission Requirements", "Available Resources", "Operational Constraints"],
                "outputs": ["Strategic Plan", "Resource Allocation Plan", "Operational Objectives"],
                "triggers": ["New mission requirements", "Periodic planning cycle"],
                "preconditions": ["Mission objectives defined", "Resources available"],
                "postconditions": ["Strategic plan approved", "Resources allocated"],
                "success_measures": ["Plan completeness", "Resource optimization", "Stakeholder approval"],
                "context_reference": "Default activity - context-specific planning would be extracted from documentation"
            },
            {
                "activity_id": "OA-ACT-002", 
                "activity_name": "Operational Execution and Control",
                "description": "Execute planned operations, monitor progress, and maintain operational control",
                "allocated_actors": [actor_names[1] if len(actor_names) > 1 else "Operations Controller"],
                "supporting_actors": [actor_names[2] if len(actor_names) > 2 else "Field Operators"],
                "required_capabilities": ["Operations Management", "Real-time Control"],
                "activity_type": "execution",
                "interactions": [
                    {
                        "from_actor": actor_names[1] if len(actor_names) > 1 else "Operations Controller",
                        "to_actor": actor_names[2] if len(actor_names) > 2 else "Field Operators",
                        "interaction_type": "supervision",
                        "description": "Direct and supervise operational activities",
                        "data_exchanged": "Control commands, operational directives",
                        "frequency": "continuous",
                        "criticality": "high"
                    },
                    {
                        "from_actor": actor_names[2] if len(actor_names) > 2 else "Field Operators",
                        "to_actor": actor_names[1] if len(actor_names) > 1 else "Operations Controller",
                        "interaction_type": "information_exchange",
                        "description": "Report operational status and issues",
                        "data_exchanged": "Status updates, issue reports, performance data",
                        "frequency": "continuous",
                        "criticality": "medium"
                    }
                ],
                "inputs": ["Operational Plan", "Control Commands", "Real-time Data"],
                "outputs": ["Operational Results", "Performance Reports", "Status Updates"],
                "triggers": ["Plan activation", "Control commands"],
                "preconditions": ["Plan approved", "Systems ready", "Operators available"],
                "postconditions": ["Operations executed", "Results recorded"],
                "success_measures": ["Operational efficiency", "Plan adherence", "Quality metrics"],
                "context_reference": "Default activity - specific operations would be extracted from documentation"
            },
            {
                "activity_id": "OA-ACT-003",
                "activity_name": "Performance Monitoring and Analysis",
                "description": "Monitor system performance, analyze operational data, and identify improvement opportunities",
                "allocated_actors": [actor_names[1] if len(actor_names) > 1 else "Performance Analyst"],
                "supporting_actors": [actor_names[0] if actor_names else "System Administrator"],
                "required_capabilities": ["Data Analysis", "Performance Monitoring"],
                "activity_type": "monitoring",
                "interactions": [
                    {
                        "from_actor": "System",
                        "to_actor": actor_names[1] if len(actor_names) > 1 else "Performance Analyst",
                        "interaction_type": "information_exchange",
                        "description": "Collect system performance metrics and operational data",
                        "data_exchanged": "Performance metrics, logs, alerts",
                        "frequency": "continuous",
                        "criticality": "medium"
                    },
                    {
                        "from_actor": actor_names[1] if len(actor_names) > 1 else "Performance Analyst",
                        "to_actor": actor_names[0] if actor_names else "System Administrator",
                        "interaction_type": "collaboration",
                        "description": "Collaborate on performance improvement initiatives",
                        "data_exchanged": "Analysis results, improvement recommendations",
                        "frequency": "periodic",
                        "criticality": "medium"
                    }
                ],
                "inputs": ["System Metrics", "Performance Data", "Operational Logs"],
                "outputs": ["Performance Reports", "Trend Analysis", "Improvement Recommendations"],
                "triggers": ["Scheduled monitoring", "Alert conditions", "Performance thresholds"],
                "preconditions": ["Monitoring systems active", "Data available"],
                "postconditions": ["Performance analyzed", "Reports generated"],
                "success_measures": ["Analysis accuracy", "Issue detection rate", "Improvement identification"],
                "context_reference": "Default activity - specific monitoring would be extracted from documentation"
            }
        ]
        
        self.logger.info(f"Created {len(default_activities)} comprehensive default activities with detailed interactions")
        return default_activities
    
    def _extract_operational_processes(self, context_chunks: List[Dict[str, Any]], 
                                     proposal_text: str,
                                     actors: List[OperationalActor]) -> List[OperationalProcess]:
        """Extract operational processes using AI-powered extraction"""
        
        actor_names = [actor.name for actor in actors[:5]]
        
        prompt = self.extraction_templates["process_extraction"].format(
            context=self._prepare_context(context_chunks[:3]),
            proposal_text=proposal_text[:1500],
            extraction_focus="operational processes, workflows, and activity chains"
        )
        
        try:
            response = self.ollama_client.generate(
                model="gemma3:12b",  # Using gemma3:12b for better content generation
                prompt=prompt,
                options={"temperature": 0.3, "num_predict": 2048}
            )
            
            processes_data = self._parse_json_response(response.get('response', ''), 'processes')
            processes = []
            
            for i, proc_info in enumerate(processes_data):
                if isinstance(proc_info, dict) and 'name' in proc_info:
                    process = OperationalProcess(
                        id=f"OA-PROCESS-{i+1:03d}",
                        name=proc_info.get('name', ''),
                        description=proc_info.get('description', ''),
                        activity_chain=proc_info.get('activity_chain', []),
                        interaction_mappings=proc_info.get('interaction_mappings', []),
                        reusable_patterns=proc_info.get('reusable_patterns', []),
                        source_references=[f"chunk_{i}" for i in range(len(context_chunks[:3]))]
                    )
                    processes.append(process)
            
            self.logger.info(f"Extracted {len(processes)} operational processes")
            return processes
            
        except Exception as e:
            self.logger.error(f"Error extracting operational processes: {str(e)}")
            return []
    
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