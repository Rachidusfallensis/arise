from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class OperationalCapability:
    """Represents an operational capability in ARCADIA"""
    id: str
    name: str
    description: str
    phase: str
    actors: List[str]
    scenarios: List[str]
    functions: List[str]
    requirements_impact: List[str]
    criticality: str  # HIGH, MEDIUM, LOW

@dataclass
class ARCADIAActor:
    """Represents an actor in ARCADIA methodology"""
    id: str
    name: str
    type: str  # HUMAN, SYSTEM, EXTERNAL
    description: str
    responsibilities: List[str]
    interactions: List[str]
    capabilities: List[str]
    phase_involvement: List[str]

@dataclass
class TraceabilityLink:
    """Represents a traceability link between ARCADIA elements"""
    source_id: str
    source_type: str
    target_id: str
    target_type: str
    relationship: str  # DERIVES_FROM, IMPLEMENTS, VALIDATES, etc.
    phase: str
    confidence: float

class ARCADIAContextEnricher:
    """
    Enriches the RAG context with comprehensive ARCADIA knowledge:
    - Complete traceability matrices
    - Operational capabilities catalog
    - Actor dictionary and interactions
    - Phase-specific templates and patterns
    """
    
    def __init__(self, knowledge_base_path: str = "./data/arcadia_knowledge"):
        self.logger = logging.getLogger(__name__)
        self.knowledge_base_path = Path(knowledge_base_path)
        
        # Initialize ARCADIA knowledge structures
        self.operational_capabilities: Dict[str, OperationalCapability] = {}
        self.actors: Dict[str, ARCADIAActor] = {}
        self.traceability_matrix: List[TraceabilityLink] = []
        self.phase_templates: Dict[str, Dict[str, Any]] = {}
        
        # Load ARCADIA knowledge base
        self._load_arcadia_knowledge()

    def _load_arcadia_knowledge(self):
        """Load comprehensive ARCADIA knowledge base"""
        try:
            self._load_operational_capabilities()
            self._load_actors_dictionary()
            self._load_traceability_matrix()
            self._load_phase_templates()
            self.logger.info("ARCADIA knowledge base loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load ARCADIA knowledge base: {e}")
            self._initialize_default_knowledge()

    def _load_operational_capabilities(self):
        """Load operational capabilities catalog"""
        capabilities_data = {
            "OC-001": OperationalCapability(
                id="OC-001",
                name="Mission Planning",
                description="Capability to plan and coordinate operational missions",
                phase="operational",
                actors=["Mission Commander", "Operations Center", "Planning System"],
                scenarios=["Mission Preparation", "Resource Allocation", "Timeline Planning"],
                functions=["Plan Mission", "Allocate Resources", "Schedule Activities"],
                requirements_impact=["Planning accuracy", "Resource optimization", "Timeline compliance"],
                criticality="HIGH"
            ),
            "OC-002": OperationalCapability(
                id="OC-002",
                name="Real-time Monitoring",
                description="Capability to monitor system status and performance in real-time",
                phase="operational",
                actors=["Operator", "Monitoring System", "Alert Manager"],
                scenarios=["Status Monitoring", "Anomaly Detection", "Performance Tracking"],
                functions=["Monitor Status", "Detect Anomalies", "Generate Alerts"],
                requirements_impact=["Response time", "Detection accuracy", "Alert reliability"],
                criticality="HIGH"
            ),
            "OC-003": OperationalCapability(
                id="OC-003",
                name="Data Processing",
                description="Capability to process and analyze operational data",
                phase="system",
                actors=["Data Processor", "Analytics Engine", "Data Manager"],
                scenarios=["Data Ingestion", "Real-time Analysis", "Report Generation"],
                functions=["Ingest Data", "Process Information", "Generate Reports"],
                requirements_impact=["Processing speed", "Data accuracy", "Storage capacity"],
                criticality="MEDIUM"
            ),
            "OC-004": OperationalCapability(
                id="OC-004",
                name="Communication Management",
                description="Capability to manage communications between system components",
                phase="logical",
                actors=["Communication Manager", "Network Controller", "Protocol Handler"],
                scenarios=["Message Routing", "Protocol Management", "Network Optimization"],
                functions=["Route Messages", "Manage Protocols", "Optimize Network"],
                requirements_impact=["Communication reliability", "Latency", "Bandwidth utilization"],
                criticality="HIGH"
            ),
            "OC-005": OperationalCapability(
                id="OC-005",
                name="Resource Management",
                description="Capability to manage and allocate system resources",
                phase="physical",
                actors=["Resource Manager", "Allocation Engine", "Performance Monitor"],
                scenarios=["Resource Allocation", "Load Balancing", "Capacity Planning"],
                functions=["Allocate Resources", "Balance Load", "Plan Capacity"],
                requirements_impact=["Resource efficiency", "System performance", "Scalability"],
                criticality="MEDIUM"
            )
        }
        
        self.operational_capabilities = capabilities_data
        self.logger.info(f"Loaded {len(capabilities_data)} operational capabilities")

    def _load_actors_dictionary(self):
        """Load comprehensive actors dictionary"""
        actors_data = {
            "ACT-001": ARCADIAActor(
                id="ACT-001",
                name="Mission Commander",
                type="HUMAN",
                description="Human operator responsible for mission planning and execution oversight",
                responsibilities=[
                    "Define mission objectives",
                    "Approve operational plans",
                    "Monitor mission execution",
                    "Make critical decisions"
                ],
                interactions=[
                    "Operations Center",
                    "Planning System",
                    "Field Operators"
                ],
                capabilities=["Mission Planning", "Decision Making", "Risk Assessment"],
                phase_involvement=["operational", "system"]
            ),
            "ACT-002": ARCADIAActor(
                id="ACT-002",
                name="Operations Center",
                type="SYSTEM",
                description="Central system for coordinating and monitoring operations",
                responsibilities=[
                    "Coordinate operational activities",
                    "Monitor system status",
                    "Manage communications",
                    "Generate operational reports"
                ],
                interactions=[
                    "Mission Commander",
                    "Field Systems",
                    "Monitoring Systems"
                ],
                capabilities=["Real-time Monitoring", "Communication Management", "Data Processing"],
                phase_involvement=["operational", "system", "logical"]
            ),
            "ACT-003": ARCADIAActor(
                id="ACT-003",
                name="Field Operator",
                type="HUMAN",
                description="Human operator working in the field environment",
                responsibilities=[
                    "Execute field operations",
                    "Report status updates",
                    "Handle local incidents",
                    "Maintain equipment"
                ],
                interactions=[
                    "Operations Center",
                    "Field Equipment",
                    "Local Systems"
                ],
                capabilities=["Equipment Operation", "Status Reporting", "Incident Response"],
                phase_involvement=["operational", "physical"]
            ),
            "ACT-004": ARCADIAActor(
                id="ACT-004",
                name="Data Processing System",
                type="SYSTEM",
                description="Automated system for processing and analyzing operational data",
                responsibilities=[
                    "Process incoming data",
                    "Perform data analysis",
                    "Generate insights",
                    "Store processed information"
                ],
                interactions=[
                    "Data Sources",
                    "Analytics Engine",
                    "Storage Systems"
                ],
                capabilities=["Data Processing", "Analytics", "Information Management"],
                phase_involvement=["system", "logical", "physical"]
            ),
            "ACT-005": ARCADIAActor(
                id="ACT-005",
                name="External System",
                type="EXTERNAL",
                description="External system that interfaces with the main system",
                responsibilities=[
                    "Provide external data",
                    "Accept system outputs",
                    "Maintain interface protocols",
                    "Ensure data quality"
                ],
                interactions=[
                    "Interface Manager",
                    "Data Exchange System",
                    "Protocol Handler"
                ],
                capabilities=["Data Exchange", "Protocol Compliance", "Interface Management"],
                phase_involvement=["logical", "physical"]
            )
        }
        
        self.actors = actors_data
        self.logger.info(f"Loaded {len(actors_data)} ARCADIA actors")

    def _load_traceability_matrix(self):
        """Load comprehensive traceability matrix"""
        traceability_data = [
            TraceabilityLink(
                source_id="OC-001",
                source_type="OPERATIONAL_CAPABILITY",
                target_id="SF-001",
                target_type="SYSTEM_FUNCTION",
                relationship="IMPLEMENTS",
                phase="operational_to_system",
                confidence=0.95
            ),
            TraceabilityLink(
                source_id="SF-001",
                source_type="SYSTEM_FUNCTION",
                target_id="LC-001",
                target_type="LOGICAL_COMPONENT",
                relationship="ALLOCATED_TO",
                phase="system_to_logical",
                confidence=0.90
            ),
            TraceabilityLink(
                source_id="LC-001",
                source_type="LOGICAL_COMPONENT",
                target_id="PC-001",
                target_type="PHYSICAL_COMPONENT",
                relationship="REALIZED_BY",
                phase="logical_to_physical",
                confidence=0.85
            ),
            TraceabilityLink(
                source_id="ACT-001",
                source_type="ACTOR",
                target_id="OC-001",
                target_type="OPERATIONAL_CAPABILITY",
                relationship="RESPONSIBLE_FOR",
                phase="operational",
                confidence=1.0
            ),
            TraceabilityLink(
                source_id="OC-002",
                source_type="OPERATIONAL_CAPABILITY",
                target_id="NFR-001",
                target_type="NON_FUNCTIONAL_REQUIREMENT",
                relationship="CONSTRAINS",
                phase="operational",
                confidence=0.88
            )
        ]
        
        self.traceability_matrix = traceability_data
        self.logger.info(f"Loaded {len(traceability_data)} traceability links")

    def _load_phase_templates(self):
        """Load phase-specific templates and patterns"""
        self.phase_templates = {
            "operational": {
                "requirement_patterns": [
                    "The {actor} shall be able to {capability} in order to {purpose}",
                    "During {scenario}, the system shall {action} within {constraint}",
                    "The operational capability {capability} requires {resource} to achieve {outcome}"
                ],
                "verification_methods": [
                    "Stakeholder review and approval",
                    "Operational scenario walkthrough",
                    "Mission effectiveness assessment",
                    "Capability demonstration"
                ],
                "key_aspects": [
                    "Mission objectives",
                    "Operational scenarios",
                    "Stakeholder needs",
                    "Capability requirements",
                    "Performance expectations"
                ]
            },
            "system": {
                "requirement_patterns": [
                    "The system shall {function} to support {operational_capability}",
                    "When {condition}, the system shall {response} within {timeframe}",
                    "The system function {function} shall interface with {external_system}"
                ],
                "verification_methods": [
                    "System functional testing",
                    "Interface verification",
                    "Performance testing",
                    "Trade-off analysis validation"
                ],
                "key_aspects": [
                    "System functions",
                    "Functional chains",
                    "System interfaces",
                    "Performance requirements",
                    "System boundaries"
                ]
            },
            "logical": {
                "requirement_patterns": [
                    "The {component} shall implement {function} with {quality_attributes}",
                    "Component {component} shall communicate with {other_component} via {interface}",
                    "The logical architecture shall support {system_function} through {component_allocation}"
                ],
                "verification_methods": [
                    "Component allocation verification",
                    "Interface consistency check",
                    "Architecture review",
                    "Design pattern validation"
                ],
                "key_aspects": [
                    "Component allocation",
                    "Logical interfaces",
                    "Data flows",
                    "Component interactions",
                    "Architecture patterns"
                ]
            },
            "physical": {
                "requirement_patterns": [
                    "The {physical_component} shall realize {logical_component} using {technology}",
                    "Physical component {component} shall operate in {environment} with {constraints}",
                    "The implementation shall meet {performance_criteria} under {operational_conditions}"
                ],
                "verification_methods": [
                    "Physical implementation testing",
                    "Environmental testing",
                    "Performance benchmarking",
                    "Integration testing"
                ],
                "key_aspects": [
                    "Physical components",
                    "Technology choices",
                    "Environmental constraints",
                    "Implementation details",
                    "Deployment scenarios"
                ]
            }
        }
        
        self.logger.info("Loaded phase-specific templates")

    def _initialize_default_knowledge(self):
        """Initialize with default knowledge if loading fails"""
        self.logger.warning("Initializing with default ARCADIA knowledge")
        # Initialize with minimal default data
        self.operational_capabilities = {}
        self.actors = {}
        self.traceability_matrix = []
        self.phase_templates = {}

    def enrich_context_for_requirements_generation(self, 
                                                  phase: str, 
                                                  existing_context: List[Dict[str, Any]],
                                                  requirement_types: List[str]) -> List[Dict[str, Any]]:
        """
        Enrich existing context with relevant ARCADIA knowledge for requirements generation
        """
        enriched_context = existing_context.copy()
        
        # Add operational capabilities context
        if "functional" in requirement_types:
            capabilities_context = self._get_capabilities_context(phase)
            enriched_context.extend(capabilities_context)
        
        # Add actors context
        actors_context = self._get_actors_context(phase)
        enriched_context.extend(actors_context)
        
        # Add traceability context
        traceability_context = self._get_traceability_context(phase)
        enriched_context.extend(traceability_context)
        
        # Add phase-specific templates
        template_context = self._get_template_context(phase)
        enriched_context.extend(template_context)
        
        self.logger.info(f"Enriched context with {len(enriched_context) - len(existing_context)} ARCADIA knowledge chunks")
        
        return enriched_context

    def _get_capabilities_context(self, phase: str) -> List[Dict[str, Any]]:
        """Get operational capabilities context relevant to the phase"""
        relevant_capabilities = [
            cap for cap in self.operational_capabilities.values()
            if cap.phase == phase
        ]
        
        context_chunks = []
        
        # Add capabilities catalog
        if relevant_capabilities:
            capabilities_text = "OPERATIONAL CAPABILITIES CATALOG:\n\n"
            for cap in relevant_capabilities:
                capabilities_text += f"• {cap.name} ({cap.id}):\n"
                capabilities_text += f"  Description: {cap.description}\n"
                capabilities_text += f"  Criticality: {cap.criticality}\n"
                capabilities_text += f"  Actors: {', '.join(cap.actors)}\n"
                capabilities_text += f"  Key Functions: {', '.join(cap.functions)}\n"
                capabilities_text += f"  Requirements Impact: {', '.join(cap.requirements_impact)}\n\n"
            
            context_chunks.append({
                "content": capabilities_text,
                "source": "arcadia_capabilities",
                "type": "operational_capabilities",
                "metadata": {
                    "phase": phase,
                    "capability_count": len(relevant_capabilities),
                    "enrichment_type": "capabilities_catalog"
                }
            })
        
        return context_chunks

    def _get_actors_context(self, phase: str) -> List[Dict[str, Any]]:
        """Get actors context relevant to the phase"""
        relevant_actors = [
            actor for actor in self.actors.values()
            if phase in actor.phase_involvement
        ]
        
        context_chunks = []
        
        if relevant_actors:
            actors_text = "ARCADIA ACTORS DICTIONARY:\n\n"
            for actor in relevant_actors:
                actors_text += f"• {actor.name} ({actor.id}) - {actor.type}:\n"
                actors_text += f"  Description: {actor.description}\n"
                actors_text += f"  Responsibilities: {', '.join(actor.responsibilities)}\n"
                actors_text += f"  Key Interactions: {', '.join(actor.interactions)}\n"
                actors_text += f"  Capabilities: {', '.join(actor.capabilities)}\n\n"
            
            context_chunks.append({
                "content": actors_text,
                "source": "arcadia_actors",
                "type": "actors_dictionary",
                "metadata": {
                    "phase": phase,
                    "actor_count": len(relevant_actors),
                    "enrichment_type": "actors_dictionary"
                }
            })
        
        return context_chunks

    def _get_traceability_context(self, phase: str) -> List[Dict[str, Any]]:
        """Get traceability context relevant to the phase"""
        relevant_links = [
            link for link in self.traceability_matrix
            if link.phase == phase or phase in link.phase
        ]
        
        context_chunks = []
        
        if relevant_links:
            traceability_text = "ARCADIA TRACEABILITY MATRIX:\n\n"
            traceability_text += "Phase-relevant traceability relationships:\n"
            
            for link in relevant_links:
                traceability_text += f"• {link.source_type} '{link.source_id}' {link.relationship} "
                traceability_text += f"{link.target_type} '{link.target_id}' (confidence: {link.confidence:.2f})\n"
            
            traceability_text += "\nTraceability Guidelines:\n"
            traceability_text += "- Requirements should trace to operational capabilities\n"
            traceability_text += "- System functions should implement operational capabilities\n"
            traceability_text += "- Components should be allocated to realize functions\n"
            traceability_text += "- Actors should be responsible for relevant capabilities\n"
            
            context_chunks.append({
                "content": traceability_text,
                "source": "arcadia_traceability",
                "type": "traceability_matrix",
                "metadata": {
                    "phase": phase,
                    "link_count": len(relevant_links),
                    "enrichment_type": "traceability_matrix"
                }
            })
        
        return context_chunks

    def _get_template_context(self, phase: str) -> List[Dict[str, Any]]:
        """Get phase-specific template context"""
        phase_template = self.phase_templates.get(phase, {})
        
        context_chunks = []
        
        if phase_template:
            template_text = f"ARCADIA {phase.upper()} PHASE TEMPLATES:\n\n"
            
            # Add requirement patterns
            if "requirement_patterns" in phase_template:
                template_text += "Requirement Patterns:\n"
                for pattern in phase_template["requirement_patterns"]:
                    template_text += f"• {pattern}\n"
                template_text += "\n"
            
            # Add verification methods
            if "verification_methods" in phase_template:
                template_text += "Phase-Specific Verification Methods:\n"
                for method in phase_template["verification_methods"]:
                    template_text += f"• {method}\n"
                template_text += "\n"
            
            # Add key aspects
            if "key_aspects" in phase_template:
                template_text += "Key Aspects to Address:\n"
                for aspect in phase_template["key_aspects"]:
                    template_text += f"• {aspect}\n"
                template_text += "\n"
            
            context_chunks.append({
                "content": template_text,
                "source": "arcadia_templates",
                "type": "phase_templates",
                "metadata": {
                    "phase": phase,
                    "template_elements": len(phase_template),
                    "enrichment_type": "phase_templates"
                }
            })
        
        return context_chunks

    def get_capability_requirements_mapping(self, phase: str) -> Dict[str, List[str]]:
        """Get mapping of capabilities to their requirement implications"""
        relevant_capabilities = [
            cap for cap in self.operational_capabilities.values()
            if cap.phase == phase
        ]
        
        mapping = {}
        for cap in relevant_capabilities:
            mapping[cap.name] = cap.requirements_impact
        
        return mapping

    def get_actor_responsibility_matrix(self, phase: str) -> Dict[str, List[str]]:
        """Get matrix of actors and their responsibilities for the phase"""
        relevant_actors = [
            actor for actor in self.actors.values()
            if phase in actor.phase_involvement
        ]
        
        matrix = {}
        for actor in relevant_actors:
            matrix[actor.name] = actor.responsibilities
        
        return matrix

    def get_traceability_paths(self, source_type: str, target_type: str) -> List[TraceabilityLink]:
        """Get traceability paths between specific element types"""
        return [
            link for link in self.traceability_matrix
            if link.source_type == source_type and link.target_type == target_type
        ]

    def validate_requirement_traceability(self, requirement: Dict[str, Any], phase: str) -> Dict[str, Any]:
        """Validate requirement traceability against ARCADIA knowledge"""
        validation_result: Dict[str, Any] = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
            "traceability_score": 0.0
        }
        
        req_text = requirement.get("description", "").lower()
        
        # Check capability traceability
        capability_mentions = 0
        for cap_name in self.operational_capabilities.keys():
            if cap_name.lower().replace("-", " ") in req_text:
                capability_mentions += 1
        
        # Check actor traceability
        actor_mentions = 0
        for actor_name in [actor.name.lower() for actor in self.actors.values()]:
            if actor_name in req_text:
                actor_mentions += 1
        
        # Calculate traceability score
        traceability_score = min(1.0, (capability_mentions * 0.4 + actor_mentions * 0.3 + 0.3))
        validation_result["traceability_score"] = traceability_score
        
        # Generate suggestions
        if capability_mentions == 0:
            validation_result["suggestions"].append(
                "Consider linking requirement to relevant operational capabilities"
            )
        
        if actor_mentions == 0:
            validation_result["suggestions"].append(
                "Consider specifying responsible actors for this requirement"
            )
        
        if traceability_score < 0.5:
            validation_result["is_valid"] = False
            validation_result["issues"].append(
                f"Low traceability score ({traceability_score:.2f}). Requirement may lack ARCADIA context."
            )
        
        return validation_result

    def export_knowledge_summary(self) -> Dict[str, Any]:
        """Export summary of loaded ARCADIA knowledge"""
        return {
            "operational_capabilities": {
                "count": len(self.operational_capabilities),
                "by_phase": {
                    phase: len([cap for cap in self.operational_capabilities.values() if cap.phase == phase])
                    for phase in ["operational", "system", "logical", "physical"]
                },
                "by_criticality": {
                    criticality: len([cap for cap in self.operational_capabilities.values() if cap.criticality == criticality])
                    for criticality in ["HIGH", "MEDIUM", "LOW"]
                }
            },
            "actors": {
                "count": len(self.actors),
                "by_type": {
                    actor_type: len([actor for actor in self.actors.values() if actor.type == actor_type])
                    for actor_type in ["HUMAN", "SYSTEM", "EXTERNAL"]
                },
                "by_phase": {
                    phase: len([actor for actor in self.actors.values() if phase in actor.phase_involvement])
                    for phase in ["operational", "system", "logical", "physical"]
                }
            },
            "traceability_links": {
                "count": len(self.traceability_matrix),
                "by_relationship": {
                    relationship: len([link for link in self.traceability_matrix if link.relationship == relationship])
                    for relationship in set(link.relationship for link in self.traceability_matrix)
                }
            },
            "phase_templates": {
                "phases_covered": list(self.phase_templates.keys()),
                "total_patterns": sum(len(template.get("requirement_patterns", [])) for template in self.phase_templates.values()),
                "total_verification_methods": sum(len(template.get("verification_methods", [])) for template in self.phase_templates.values())
            }
        } 