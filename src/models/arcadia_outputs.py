from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from enum import Enum
import json
from datetime import datetime

class ARCADIAPhaseType(Enum):
    """ARCADIA methodology phases"""
    OPERATIONAL = "operational"
    SYSTEM = "system"
    LOGICAL = "logical"
    PHYSICAL = "physical"

class RequirementType(Enum):
    """Types of requirements in ARCADIA methodology"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    STAKEHOLDER = "stakeholder"
    INTERFACE = "interface"
    CONSTRAINT = "constraint"

class Priority(Enum):
    """MoSCoW priority levels for ARCADIA requirements"""
    MUST = "MUST"
    SHOULD = "SHOULD"
    COULD = "COULD"
    WONT = "WONT"

# ==============================================================================
# 1. OPERATIONAL ANALYSIS PHASE OUTPUTS
# ==============================================================================

@dataclass
class OperationalActor:
    """Operational actors identified from documentation"""
    id: str
    name: str
    description: str
    role_definition: str
    responsibilities: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)  # Actor IDs
    containment_hierarchy: Optional[str] = None  # Parent actor ID
    source_references: List[str] = field(default_factory=list)
    
@dataclass
class OperationalEntity:
    """Operational entities and their hierarchical structure"""
    id: str
    name: str
    description: str
    entity_type: str  # "system", "organization", "resource", etc.
    parent_entity: Optional[str] = None
    sub_entities: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    source_references: List[str] = field(default_factory=list)

@dataclass
class OperationalCapability:
    """Operational capabilities mapped to mission requirements"""
    id: str
    name: str
    description: str
    mission_statement: str
    involved_actors: List[str] = field(default_factory=list)  # Actor IDs
    capability_involvements: Dict[str, str] = field(default_factory=dict)  # Actor ID -> Role
    performance_constraints: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class OperationalScenario:
    """Operational workflows and use cases"""
    id: str
    name: str
    description: str
    scenario_type: str  # "use_case", "mission_scenario", "workflow"
    involved_actors: List[str] = field(default_factory=list)
    activity_sequence: List[Dict[str, Any]] = field(default_factory=list)
    environmental_conditions: List[str] = field(default_factory=list)
    performance_constraints: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class OperationalProcess:
    """Operational processes and activity chains"""
    id: str
    name: str
    description: str
    activity_chain: List[Dict[str, Any]] = field(default_factory=list)
    interaction_mappings: List[Dict[str, str]] = field(default_factory=list)
    reusable_patterns: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class OperationalAnalysisOutput:
    """Complete operational analysis phase output"""
    phase: ARCADIAPhaseType = ARCADIAPhaseType.OPERATIONAL
    actors: List[OperationalActor] = field(default_factory=list)
    entities: List[OperationalEntity] = field(default_factory=list)
    capabilities: List[OperationalCapability] = field(default_factory=list)
    scenarios: List[OperationalScenario] = field(default_factory=list)
    processes: List[OperationalProcess] = field(default_factory=list)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)

# ==============================================================================
# 2. SYSTEM ANALYSIS PHASE OUTPUTS
# ==============================================================================

@dataclass
class SystemActor:
    """System-level actors and interfaces"""
    id: str
    name: str
    description: str
    actor_type: str  # "external", "internal", "interface"
    interfaces: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class SystemBoundary:
    """System boundary definition and context"""
    scope_definition: str
    included_elements: List[str] = field(default_factory=list)
    excluded_elements: List[str] = field(default_factory=list)
    external_dependencies: List[str] = field(default_factory=list)
    environmental_factors: List[str] = field(default_factory=list)

@dataclass
class SystemFunction:
    """System functions extracted from technical descriptions"""
    id: str
    name: str
    description: str
    function_type: str  # "primary", "secondary", "support"
    parent_function: Optional[str] = None
    sub_functions: List[str] = field(default_factory=list)
    allocated_actors: List[str] = field(default_factory=list)
    functional_exchanges: List[Dict[str, Any]] = field(default_factory=list)
    performance_requirements: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class SystemCapability:
    """System capabilities realizing operational capabilities"""
    id: str
    name: str
    description: str
    realized_operational_capabilities: List[str] = field(default_factory=list)
    implementing_functions: List[str] = field(default_factory=list)  # Function IDs
    performance_requirements: List[Dict[str, Any]] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class FunctionalChain:
    """End-to-end functional sequences"""
    id: str
    name: str
    description: str
    scenario_context: str
    function_sequence: List[Dict[str, Any]] = field(default_factory=list)
    alternative_paths: List[Dict[str, Any]] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class SystemAnalysisOutput:
    """Complete system analysis phase output"""
    phase: ARCADIAPhaseType = ARCADIAPhaseType.SYSTEM
    system_boundary: SystemBoundary = field(default_factory=lambda: SystemBoundary(""))
    actors: List[SystemActor] = field(default_factory=list)
    functions: List[SystemFunction] = field(default_factory=list)
    capabilities: List[SystemCapability] = field(default_factory=list)
    functional_chains: List[FunctionalChain] = field(default_factory=list)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)

# ==============================================================================
# 3. LOGICAL ARCHITECTURE PHASE OUTPUTS
# ==============================================================================

@dataclass
class LogicalComponent:
    """Logical subsystems and their responsibilities"""
    id: str
    name: str
    description: str
    component_type: str  # "subsystem", "module", "service"
    responsibilities: List[str] = field(default_factory=list)
    parent_component: Optional[str] = None
    sub_components: List[str] = field(default_factory=list)
    interfaces: List[Dict[str, Any]] = field(default_factory=list)
    allocated_functions: List[str] = field(default_factory=list)  # Function IDs
    source_references: List[str] = field(default_factory=list)

@dataclass
class LogicalFunction:
    """Detailed logical functions derived from system functions"""
    id: str
    name: str
    description: str
    parent_system_function: Optional[str] = None
    sub_functions: List[str] = field(default_factory=list)
    input_interfaces: List[Dict[str, Any]] = field(default_factory=list)
    output_interfaces: List[Dict[str, Any]] = field(default_factory=list)
    behavioral_models: List[Dict[str, Any]] = field(default_factory=list)
    allocated_components: List[str] = field(default_factory=list)  # Component IDs
    source_references: List[str] = field(default_factory=list)

@dataclass
class LogicalInterface:
    """Logical interfaces between components"""
    id: str
    name: str
    description: str
    interface_type: str  # "data", "control", "user", "external", "service", "api"
    provider_component: Optional[str] = None
    consumer_components: List[str] = field(default_factory=list)
    data_specifications: List[str] = field(default_factory=list)
    protocol_specifications: List[str] = field(default_factory=list)
    quality_attributes: Dict[str, Any] = field(default_factory=dict)
    supports_system_interfaces: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class LogicalScenario:
    """Component interactions and behavioral scenarios"""
    id: str
    name: str
    description: str
    scenario_type: str  # "functional", "interface", "performance", "error", "nominal"
    involved_components: List[str] = field(default_factory=list)
    involved_functions: List[str] = field(default_factory=list)
    interaction_sequence: List[Dict[str, Any]] = field(default_factory=list)
    data_flows: List[Dict[str, Any]] = field(default_factory=list)
    performance_characteristics: Dict[str, Any] = field(default_factory=dict)
    realizes_operational_scenarios: List[str] = field(default_factory=list)
    # Keep backward compatibility fields
    participating_components: List[str] = field(default_factory=list)
    message_sequences: List[Dict[str, Any]] = field(default_factory=list)
    state_transitions: List[Dict[str, Any]] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class ArchitectureView:
    """Architecture views and specifications"""
    id: str
    name: str
    description: str
    view_type: str  # "swimlane", "interface", "allocation", "tradeoff"
    components: List[str] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    specifications: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    source_references: List[str] = field(default_factory=list)

@dataclass
class LogicalArchitectureOutput:
    """Complete logical architecture phase output"""
    phase: ARCADIAPhaseType = ARCADIAPhaseType.LOGICAL
    components: List[LogicalComponent] = field(default_factory=list)
    functions: List[LogicalFunction] = field(default_factory=list)
    interfaces: List[LogicalInterface] = field(default_factory=list)
    scenarios: List[LogicalScenario] = field(default_factory=list)
    architecture_views: List[ArchitectureView] = field(default_factory=list)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)

# ==============================================================================
# 4. PHYSICAL ARCHITECTURE PHASE OUTPUTS
# ==============================================================================

@dataclass
class PhysicalComponent:
    """Hardware/software implementation components"""
    id: str
    name: str
    description: str
    component_type: str  # "hardware", "software", "hybrid"
    technology_platform: str
    implementing_logical_components: List[str] = field(default_factory=list)
    interfaces: List[Dict[str, Any]] = field(default_factory=list)
    deployment_configuration: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    source_references: List[str] = field(default_factory=list)

@dataclass
class ImplementationConstraint:
    """Physical implementation constraints"""
    id: str
    name: str
    description: str
    constraint_type: str  # "technology", "performance", "environmental", "safety", "security"
    affected_components: List[str] = field(default_factory=list)
    specifications: Dict[str, Any] = field(default_factory=dict)
    validation_criteria: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class PhysicalFunction:
    """Technology-specific function implementations"""
    id: str
    name: str
    description: str
    implementing_logical_function: Optional[str] = None
    technology_specifics: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    timing_constraints: List[Dict[str, Any]] = field(default_factory=list)
    quality_attributes: List[Dict[str, Any]] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class PhysicalScenario:
    """Physical deployment and operational scenarios"""
    id: str
    name: str
    description: str
    scenario_type: str  # "deployment", "operational", "failure", "maintenance"
    involved_components: List[str] = field(default_factory=list)
    procedures: List[Dict[str, Any]] = field(default_factory=list)
    environmental_conditions: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class PhysicalArchitectureOutput:
    """Complete physical architecture phase output"""
    phase: ARCADIAPhaseType = ARCADIAPhaseType.PHYSICAL
    components: List[PhysicalComponent] = field(default_factory=list)
    constraints: List[ImplementationConstraint] = field(default_factory=list)
    functions: List[PhysicalFunction] = field(default_factory=list)
    scenarios: List[PhysicalScenario] = field(default_factory=list)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)

# ==============================================================================
# 5. CROSS-PHASE ANALYSIS OUTPUTS
# ==============================================================================

@dataclass
class TraceabilityLink:
    """Bidirectional traceability links between elements"""
    id: str
    source_element: str
    target_element: str
    source_phase: ARCADIAPhaseType
    target_phase: ARCADIAPhaseType
    relationship_type: str  # "realizes", "implements", "derives_from", "depends_on"
    confidence_score: float = 0.0
    validation_status: str = "unverified"  # "verified", "unverified", "inconsistent"
    source_references: List[str] = field(default_factory=list)

@dataclass
class GapAnalysisItem:
    """Identified gaps in requirement coverage"""
    id: str
    gap_type: str  # "missing", "inconsistent", "ambiguous", "incomplete"
    phase: ARCADIAPhaseType
    description: str
    affected_elements: List[str] = field(default_factory=list)
    severity: str = "medium"  # "critical", "major", "medium", "minor"
    recommendations: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class ArchitectureConsistencyCheck:
    """Architecture consistency validation"""
    id: str
    check_type: str  # "model_coherence", "interface_compatibility", "constraint_propagation"
    phases_involved: List[ARCADIAPhaseType] = field(default_factory=list)
    status: str = "passed"  # "passed", "failed", "warning"
    description: str = ""
    issues_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)

@dataclass
class QualityMetric:
    """Quality assessment metrics"""
    id: str
    metric_name: str
    metric_type: str  # "requirement_quality", "architecture_quality", "verification", "risk"
    phase: Optional[ARCADIAPhaseType] = None
    score: float = 0.0
    max_score: float = 1.0
    criteria: List[str] = field(default_factory=list)
    assessment_details: Dict[str, Any] = field(default_factory=dict)
    source_references: List[str] = field(default_factory=list)

@dataclass
class CrossPhaseAnalysisOutput:
    """Cross-phase analysis results"""
    traceability_links: List[TraceabilityLink] = field(default_factory=list)
    gap_analysis: List[GapAnalysisItem] = field(default_factory=list)
    consistency_checks: List[ArchitectureConsistencyCheck] = field(default_factory=list)
    quality_metrics: List[QualityMetric] = field(default_factory=list)
    coverage_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    impact_analysis: Dict[str, List[str]] = field(default_factory=dict)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)

# ==============================================================================
# 6. COMPLETE STRUCTURED OUTPUT
# ==============================================================================

@dataclass
class ARCADIAStructuredOutput:
    """Complete structured output from ARCADIA RAG analysis"""
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    operational_analysis: Optional[OperationalAnalysisOutput] = None
    system_analysis: Optional[SystemAnalysisOutput] = None
    logical_architecture: Optional[LogicalArchitectureOutput] = None
    physical_architecture: Optional[PhysicalArchitectureOutput] = None
    cross_phase_analysis: CrossPhaseAnalysisOutput = field(default_factory=CrossPhaseAnalysisOutput)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        def convert_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                result = {}
                for field_name, field_def in obj.__dataclass_fields__.items():
                    value = getattr(obj, field_name)
                    if isinstance(value, list):
                        result[field_name] = [convert_dataclass(item) for item in value]
                    elif isinstance(value, dict):
                        result[field_name] = {k: convert_dataclass(v) for k, v in value.items()}
                    elif hasattr(value, '__dataclass_fields__'):
                        result[field_name] = convert_dataclass(value)
                    elif isinstance(value, Enum):
                        result[field_name] = value.value
                    else:
                        result[field_name] = value
                return result
            return obj
        
        return convert_dataclass(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ARCADIAStructuredOutput':
        """Create from dictionary"""
        # This would need proper deserialization logic
        # For now, return a basic instance
        return cls(generation_metadata=data.get('generation_metadata', {}))

# ==============================================================================
# 7. HELPER FUNCTIONS
# ==============================================================================

def create_extraction_metadata(
    source_documents: List[str],
    extraction_timestamp: datetime,
    confidence_scores: Dict[str, float],
    processing_statistics: Dict[str, Any]
) -> Dict[str, Any]:
    """Create standardized extraction metadata"""
    return {
        "source_documents": source_documents,
        "extraction_timestamp": extraction_timestamp.isoformat(),
        "confidence_scores": confidence_scores,
        "processing_statistics": processing_statistics,
        "arcadia_version": "7.0",
        "extraction_tool": "SAFE-MBSE-RAG"
    }

def validate_traceability_link(link: TraceabilityLink) -> bool:
    """Validate a traceability link"""
    required_fields = ['source_element', 'target_element', 'source_phase', 'target_phase', 'relationship_type']
    return all(getattr(link, field) for field in required_fields)

def calculate_coverage_score(total_elements: int, covered_elements: int) -> float:
    """Calculate coverage percentage"""
    if total_elements == 0:
        return 1.0
    return min(covered_elements / total_elements, 1.0) 