from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

class ArcadiaPhase(Enum):
    """Official ARCADIA phases based on Thales methodology"""
    OPERATIONAL = "operational"
    SYSTEM = "system" 
    LOGICAL = "logical"
    PHYSICAL = "physical"
    BUILDING_STRATEGY = "building_strategy"

class RequirementType(Enum):
    """Types of requirements according to ARCADIA"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    STAKEHOLDER = "stakeholder"
    INTERFACE = "interface"
    CONSTRAINT = "constraint"

@dataclass
class ArcadiaViewpoint:
    """ARCADIA viewpoint for multi-viewpoint analysis"""
    name: str
    description: str
    concerns: List[str]
    keywords: List[str]
    applicable_phases: List[ArcadiaPhase]
    priority: int  # 1 (highest) to 5 (lowest)

# Enhanced ARCADIA Configuration based on official Thales methodology
ARCADIA_PHASES = {
    "operational": {
        "name": "Operational Analysis",
        "code": "OA",
        "description": "Understanding stakeholder needs and operational context",
        "icon": "🎭",
        "engineering_goals": [
            "Understand the real Customer Need to address",
            "Check the Need Consistency, Completeness", 
            "Collect Material for future technical Trade-offs",
            "Ensure realism/relevance of IVVQ operational scenarios"
        ],
        "tasks": [
            "Define Operational Missions and Capabilities",
            "Perform an Operational Need Analysis"
        ],
        "outputs": [
            "Operational Architecture",
            "Stakeholder Requirements", 
            "Operational Capabilities",
            "Operational Scenarios",
            "Use Cases"
        ],
        "keywords": [
            "stakeholder", "actor", "mission", "capability", "operational",
            "use case", "scenario", "need", "goal", "activity", "process",
            "DOTMLPF", "capability gap", "operational context"
        ],
        "requirement_types": ["functional", "non_functional", "stakeholder"],
        "templates": ["stakeholder_template", "capability_template", "mission_template"],
        "stop_criteria": "Agreement with stakeholders on operational need description",
        "verification_focus": ["Need completeness", "Stakeholder agreement", "Operational realism"]
    },
    
    "system": {
        "name": "System Need Analysis", 
        "code": "SA",
        "description": "Defining system requirements and functions",
        "icon": "⚙️",
        "engineering_goals": [
            "Define functional and non-functional need/expectations for system",
            "Check Feasibility of Requirements (tech., cost, schedule)",
            "Find most structuring/constraining Requirements",
            "Evaluate impact on design & integration",
            "Get technical Material to support Negotiation"
        ],
        "tasks": [
            "Perform a Capability Trade-off Analysis",
            "Perform a functional and non-functional Analysis", 
            "Formalise and consolidate Requirements"
        ],
        "outputs": [
            "System Functions",
            "System Requirements",
            "Functional Chains", 
            "System Scenarios",
            "Early Architecture"
        ],
        "keywords": [
            "function", "requirement", "interface", "system", "constraint",
            "mode", "service", "capability", "trade-off", "feasibility",
            "functional chain", "system need", "performance"
        ],
        "requirement_types": ["functional", "performance", "interface"],
        "templates": ["functional_template", "interface_template", "constraint_template"],
        "stop_criteria": "Risk mitigation and sufficient definition for architecture design",
        "verification_focus": ["Requirements consistency", "Functional need validity", "Cost estimation"]
    },
    
    "logical": {
        "name": "Logical Architecture Design",
        "code": "LA", 
        "description": "Designing solution components and interfaces",
        "icon": "🏗️",
        "engineering_goals": [
            "Build coarse-grained breakdown in components",
            "Near optimum Compromise between major Requirements & Constraints",
            "Early define and validate architecture properties",
            "Get technical Material to support Negotiation"
        ],
        "tasks": [
            "Define Architecture Drivers and Viewpoints design Rules",
            "Define notional functional and non-functional Behavior",
            "Build candidate architectural breakdowns in Components", 
            "Select best Compromise Architecture"
        ],
        "outputs": [
            "Logical Components",
            "Component Breakdown",
            "Interfaces Definition",
            "Viewpoint Analysis",
            "Architecture Compromise"
        ],
        "keywords": [
            "component", "logical", "behavior", "interaction", "scenario",
            "exchange", "protocol", "breakdown", "viewpoint", "compromise",
            "architecture driver", "functional allocation", "interface"
        ],
        "requirement_types": ["functional", "behavioral", "interaction"],
        "templates": ["component_template", "behavior_template", "interaction_template"],
        "stop_criteria": "Best compromise architecture proven through multi-viewpoint analysis", 
        "verification_focus": ["Architecture drivers compliance", "Viewpoint reconciliation", "Component coherence"]
    },
    
    "physical": {
        "name": "Physical Architecture Design",
        "code": "PA",
        "description": "Implementing and deploying the solution", 
        "icon": "🔧",
        "engineering_goals": [
            "Manage engineering complexity through structuring architecture",
            "Favour Reuse of legacy Assets and Product Policy",
            "Early validate key features of the solution"
        ],
        "tasks": [
            "Define Architectural Principles and Patterns",
            "Define finalised functional and non-functional Behavior",
            "Consider Reuse of existing Assets",
            "Build candidate detailed Architectures",
            "Select and finalise the Physical Reference Architecture"
        ],
        "outputs": [
            "Physical Components", 
            "Implementation Components",
            "Hosting Components",
            "Behavioral Components",
            "Reference Architecture"
        ],
        "keywords": [
            "physical", "implementation", "deployment", "node", "configuration",
            "hardware", "software", "reuse", "pattern", "hosting",
            "behavioral component", "resource allocation", "technology"
        ],
        "requirement_types": ["implementation", "deployment", "hardware", "software"],
        "templates": ["implementation_template", "deployment_template", "hardware_template"],
        "stop_criteria": "Architecture ready for development by component providers",
        "verification_focus": ["Implementation feasibility", "Resource constraints", "Technology choices"]
    },
    
    "building_strategy": {
        "name": "Building Strategy Definition",
        "code": "BS", 
        "description": "Contracts for development & IVVQ",
        "icon": "📋",
        "engineering_goals": [
            "Define contractual requirements for components and EPBS",
            "Define architectural frame & constraints for development",
            "Define integration, verification, validation strategy"
        ],
        "tasks": [
            "Define & enforce PBS and Component Integration Contract",
            "Define Components IVVQ Strategy"
        ],
        "outputs": [
            "Component Integration Contracts",
            "Product Breakdown Structure (PBS)",
            "IVVQ Strategy",
            "Test Campaigns"
        ],
        "keywords": [
            "PBS", "EPBS", "integration contract", "IVVQ", "configuration item",
            "component contract", "test strategy", "verification", "validation"
        ],
        "requirement_types": ["constraint", "interface"],
        "templates": ["contract_template", "ivvq_template", "pbs_template"],
        "stop_criteria": "Agreement with component providers on contracts and IVVQ strategy",
        "verification_focus": ["Contract completeness", "IVVQ feasibility", "Integration strategy"]
    }
}

# Enhanced Requirement Categories with ARCADIA-specific patterns
REQUIREMENT_CATEGORIES = {
    "functional": {
        "prefix": "FR",
        "description": "System functions and capabilities",
        "patterns": [
            r"(?:the\s+)?system\s+shall\s+([^.]+)",
            r"(?:the\s+)?(?:component|module|subsystem)\s+(?:shall|must|will)\s+([^.]+)", 
            r"capability\s+to\s+([^.]+)",
            r"able\s+to\s+([^.]+)"
        ],
        "validation_keywords": ["shall", "must", "will", "should", "function", "capability", "service"],
        "quality_criteria": ["testable", "unambiguous", "complete", "traceable"],
        "keywords": ["shall", "must", "will", "should"]
    },
    "non_functional": {
        "prefix": "NFR", 
        "description": "Quality attributes and constraints",
        "subcategories": {
            "performance": {"prefix": "PERF", "keywords": ["performance", "speed", "throughput", "latency", "response time"]},
            "security": {"prefix": "SEC", "keywords": ["security", "access", "authentication", "encryption", "protection"]},
            "usability": {"prefix": "USE", "keywords": ["usability", "user interface", "human factors", "ergonomics"]},
            "reliability": {"prefix": "REL", "keywords": ["reliability", "availability", "fault tolerance", "MTBF", "MTTR"]}, 
            "scalability": {"prefix": "SCAL", "keywords": ["scalability", "capacity", "growth", "expansion"]},
            "maintainability": {"prefix": "MAIN", "keywords": ["maintainability", "maintenance", "serviceability", "support"]}
        },
        "patterns": [
            r"(?:performance|speed|throughput)\s+(?:shall|must|should)\s+([^.]+)",
            r"(?:response\s+time|latency)\s+(?:shall|must|should)\s+([^.]+)",
            r"availability\s+(?:shall|must|should)\s+([^.]+)"
        ],
        "quality_criteria": ["measurable", "achievable", "testable", "specific"]
    },
    "stakeholder": {
        "prefix": "STK",
        "description": "Stakeholder-specific requirements and needs",
        "patterns": [
            r"(?:stakeholder|user|actor)\s+([^.]+)\s+(?:shall|must|needs?|expects?|requires?)\s+([^.]+)",
            r"(?:operator|administrator|maintainer)\s+(?:shall|must|should)\s+([^.]+)"
        ],
        "validation_keywords": ["stakeholder", "user", "actor", "operator", "needs", "expects"],
        "quality_criteria": ["user-focused", "business-relevant", "achievable", "prioritized"],
        "keywords": ["stakeholder", "user", "actor"]
    },
    "interface": {
        "prefix": "IF",
        "description": "Interface and interaction requirements", 
        "patterns": [
            r"interface\s+(?:shall|must|should)\s+([^.]+)",
            r"(?:communication|protocol|API)\s+(?:shall|must|should)\s+([^.]+)",
            r"exchange\s+(?:shall|must|should)\s+([^.]+)"
        ],
        "validation_keywords": ["interface", "protocol", "API", "communication", "exchange", "interaction"],
        "quality_criteria": ["complete", "consistent", "implementable", "testable"]
    },
    "constraint": {
        "prefix": "CON",
        "description": "Design and implementation constraints",
        "patterns": [
            r"(?:constraint|limitation|restriction)\s+([^.]+)",
            r"(?:shall|must)\s+(?:comply|conform|adhere)\s+to\s+([^.]+)",
            r"(?:technology|platform|standard)\s+(?:shall|must|should)\s+([^.]+)"
        ],
        "validation_keywords": ["constraint", "limitation", "comply", "standard", "regulation", "compliance"],
        "quality_criteria": ["verifiable", "necessary", "realistic", "traceable"]
    }
}

# ARCADIA Viewpoints for Multi-Viewpoint Analysis
ARCADIA_VIEWPOINTS = {
    "functional": ArcadiaViewpoint(
        name="Functional Consistency",
        description="Functions grouping and allocation coherence",
        concerns=["functional allocation", "service definition", "capability implementation"],
        keywords=["function", "service", "capability", "allocation", "functional chain"],
        applicable_phases=[ArcadiaPhase.SYSTEM, ArcadiaPhase.LOGICAL, ArcadiaPhase.PHYSICAL],
        priority=1
    ),
    "performance": ArcadiaViewpoint(
        name="Performance & Real-time",
        description="Timing constraints and performance requirements",
        concerns=["real-time constraints", "performance", "resource consumption", "latency"],
        keywords=["performance", "real-time", "latency", "throughput", "response time", "critical path"],
        applicable_phases=[ArcadiaPhase.SYSTEM, ArcadiaPhase.LOGICAL, ArcadiaPhase.PHYSICAL],
        priority=2
    ),
    "safety": ArcadiaViewpoint(
        name="Safety & Dependability", 
        description="Safety requirements and fault tolerance",
        concerns=["safety levels", "fault tolerance", "redundancy", "certification"],
        keywords=["safety", "fault", "redundancy", "certification", "criticality", "hazard"],
        applicable_phases=[ArcadiaPhase.LOGICAL, ArcadiaPhase.PHYSICAL],
        priority=1
    ),
    "security": ArcadiaViewpoint(
        name="Security",
        description="Security constraints and protection mechanisms",
        concerns=["access control", "data protection", "threat mitigation", "cryptography"],
        keywords=["security", "access control", "encryption", "threat", "vulnerability", "protection"],
        applicable_phases=[ArcadiaPhase.LOGICAL, ArcadiaPhase.PHYSICAL],
        priority=2
    ),
    "reuse": ArcadiaViewpoint(
        name="Reuse & Product Line",
        description="Asset reuse and product line constraints", 
        concerns=["legacy integration", "COTS usage", "product variability", "compatibility"],
        keywords=["reuse", "COTS", "legacy", "product line", "variability", "compatibility"],
        applicable_phases=[ArcadiaPhase.LOGICAL, ArcadiaPhase.PHYSICAL],
        priority=3
    ),
    "ivvq": ArcadiaViewpoint(
        name="Integration & Verification",
        description="Integration strategy and verification approach",
        concerns=["integration order", "test strategy", "simulation needs", "verification"],
        keywords=["integration", "verification", "validation", "test", "simulation", "qualification"],
        applicable_phases=[ArcadiaPhase.PHYSICAL, ArcadiaPhase.BUILDING_STRATEGY],
        priority=2
    ),
    "deployment": ArcadiaViewpoint(
        name="Deployment & Configuration",
        description="System deployment and configuration management",
        concerns=["deployment constraints", "configuration management", "environment"],
        keywords=["deployment", "configuration", "environment", "installation", "commissioning"],
        applicable_phases=[ArcadiaPhase.PHYSICAL, ArcadiaPhase.BUILDING_STRATEGY],
        priority=3
    )
}

# ARCADIA Concepts Mapping for semantic understanding
ARCADIA_CONCEPTS = {
    "operational_analysis": {
        "missions": "High-level goals and purposes of the system",
        "capabilities": "Quantified operational goals and results expected",
        "operational_activities": "Tasks performed by actors to achieve capabilities", 
        "operational_processes": "Sequences of operational activities",
        "actors": "Entities (human or system) performing operational activities",
        "entities": "Organizational or geographical nodes in operational context",
        "operational_scenarios": "Orchestration of operational activities for given situations"
    },
    "system_analysis": {
        "system_functions": "Functions directly driven by operational need",
        "functional_chains": "Sequences of system functions supporting operational processes",
        "system_scenarios": "Allocation of operational scenarios to system and users",
        "system_capabilities": "System contribution to operational capabilities",
        "system_modes": "Different operational modes of the system",
        "system_states": "Internal states affecting system behavior"
    },
    "logical_architecture": {
        "logical_components": "Coarse-grained breakdown for development structuring",
        "logical_functions": "Functions allocated to logical components", 
        "component_exchanges": "Data flows between logical components",
        "logical_interfaces": "Interfaces between logical components",
        "functional_allocation": "Assignment of functions to components"
    },
    "physical_architecture": {
        "behavioral_components": "Components carrying functional contents",
        "implementation_components": "Resources for behavioral component execution",
        "hosting_components": "Physical resources hosting behavioral components",
        "physical_interfaces": "Physical connections and communication links",
        "deployment_constraints": "Physical deployment and installation constraints"
    }
}

# Enhanced Priority Levels (MoSCoW + ARCADIA context)
PRIORITY_LEVELS = {
    "MUST": {
        "description": "Critical requirements that must be implemented",
        "weight": 5,
        "arcadia_context": "Essential for operational capability achievement"
    },
    "SHOULD": {
        "description": "Important requirements that should be implemented",
        "weight": 3,
        "arcadia_context": "Significant contribution to operational effectiveness"
    },
    "COULD": {
        "description": "Optional requirements that could be implemented",
        "weight": 1,
        "arcadia_context": "Enhancement to operational capability"
    },
    "WONT": {
        "description": "Requirements that will not be implemented in current scope",
        "weight": 0,
        "arcadia_context": "Deferred to future operational evolution"
    }
}

# Traceability Matrix for ARCADIA phases
TRACEABILITY_LINKS = {
    "operational_to_system": [
        ("operational_capability", "system_function"),
        ("operational_activity", "system_function"), 
        ("operational_process", "functional_chain"),
        ("operational_scenario", "system_scenario"),
        ("actor_need", "system_requirement")
    ],
    "system_to_logical": [
        ("system_function", "logical_function"),
        ("functional_chain", "component_allocation"),
        ("system_requirement", "component_requirement"),
        ("system_scenario", "component_scenario")
    ],
    "logical_to_physical": [
        ("logical_component", "behavioral_component"),
        ("logical_interface", "physical_interface"), 
        ("logical_function", "physical_function"),
        ("component_requirement", "implementation_requirement")
    ],
    "requirements_to_verification": [
        ("functional_requirement", "functional_test"),
        ("non_functional_requirement", "performance_test"),
        ("interface_requirement", "integration_test"),
        ("stakeholder_requirement", "acceptance_test")
    ]
}

# ARCADIA-specific vocabulary for enhanced embeddings
ARCADIA_VOCABULARY = {
    "operational": [
        "mission", "capability", "operational activity", "operational process", 
        "actor", "stakeholder", "entity", "operational scenario", "use case",
        "operational need", "capability gap", "DOTMLPF", "operational context"
    ],
    "system": [
        "system function", "functional chain", "system scenario", "system capability",
        "system mode", "system state", "trade-off analysis", "system need",
        "capability analysis", "system requirement", "feasibility"
    ],
    "logical": [
        "logical component", "logical function", "component exchange", "logical interface",
        "functional allocation", "component breakdown", "viewpoint", "architecture driver",
        "compromise architecture", "notional behavior"
    ],
    "physical": [
        "behavioral component", "implementation component", "hosting component", 
        "physical interface", "deployment constraint", "architectural pattern",
        "reuse asset", "reference architecture", "physical allocation"
    ],
    "building_strategy": [
        "PBS", "EPBS", "integration contract", "IVVQ strategy", "configuration item",
        "component contract", "test campaign", "verification strategy", "validation approach"
    ],
    "quality": [
        "viewpoint", "architecture driver", "compromise", "consistency", "coherence",
        "completeness", "traceability", "verification", "validation", "justification"
    ]
}

# Verification Methods aligned with ARCADIA
VERIFICATION_METHODS = {
    "operational_analysis": [
        "Stakeholder review and approval",
        "Operational scenario walk-through", 
        "Capability gap analysis validation",
        "User acceptance of operational need"
    ],
    "system_analysis": [
        "Requirements review and traceability check",
        "Functional analysis verification",
        "Trade-off analysis validation",
        "System scenario simulation"
    ],
    "logical_architecture": [
        "Multi-viewpoint analysis",
        "Component allocation verification",
        "Interface consistency check", 
        "Architecture compromise validation"
    ],
    "physical_architecture": [
        "Implementation feasibility assessment",
        "Resource constraint verification",
        "Physical interface testing",
        "Deployment scenario validation"
    ],
    "building_strategy": [
        "Integration contract review",
        "IVVQ strategy assessment",
        "Component test planning",
        "PBS validation"
    ]
}

# Consistency Checks for ARCADIA phases
CONSISTENCY_CHECKS = {
    "operational_analysis": {
        "external": [
            "Between customer documents and capability analysis products",
            "Between stakeholder needs and operational activities"
        ],
        "internal": [
            "Between outputs of the analysis",
            "Need description coherence and completeness"
        ]
    },
    "system_analysis": {
        "external": [
            "Between operational activities and system functions",
            "Between capabilities and system requirements"
        ],
        "internal": [
            "Between functional and non-functional elements",
            "System need description coherence"
        ]
    },
    "logical_architecture": {
        "external": [
            "Between system requirements and logical architecture",
            "Between system functions and component allocation"
        ],
        "internal": [
            "Between architecture drivers and component breakdown",
            "Between viewpoints and component interfaces"
        ]
    },
    "physical_architecture": {
        "external": [
            "Between logical and physical components",
            "Between operational scenarios and physical architecture"
        ],
        "internal": [
            "Between physical components and reusable assets",
            "Between architectural patterns and implementation"
        ]
    }
}

# Enhanced MBSE Context Types
MBSE_CONTEXT_TYPES = [
    "operational",
    "system", 
    "logical",
    "physical",
    "building_strategy",
    "verification",
    "traceability"
]

# Legacy compatibility - maintain existing structure
def get_phase_info(phase_key: str) -> Optional[Dict[str, Any]]:
    """Get phase information by key for backward compatibility"""
    phase_info = ARCADIA_PHASES.get(phase_key)
    return phase_info if phase_info is not None else None

def get_requirement_category(category_key: str) -> Optional[Dict[str, Any]]:
    """Get requirement category information by key"""
    return REQUIREMENT_CATEGORIES.get(category_key)

def get_phase_keywords(phase_key: str) -> List[str]:
    """Get keywords for a specific phase"""
    phase_info = ARCADIA_PHASES.get(phase_key, {})
    keywords = phase_info.get("keywords", [])
    return list(keywords) if keywords else []

def get_all_keywords() -> Dict[str, List[str]]:
    """Get all keywords organized by phase"""
    result = {}
    for phase, info in ARCADIA_PHASES.items():
        keywords = info.get("keywords", [])
        result[phase] = list(keywords) if keywords else []
    return result