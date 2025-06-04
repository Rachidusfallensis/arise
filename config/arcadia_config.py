from typing import Dict, List, Any

# ARCADIA Methodology Phase Definitions
ARCADIA_PHASES = {
    "operational": {
        "name": "Operational Analysis",
        "description": "Understanding stakeholder needs and operational context",
        "icon": "🎭",
        "keywords": ["stakeholder", "actor", "operational", "capability", "mission", "goal", "use case"],
        "requirement_types": ["functional", "non_functional", "stakeholder"],
        "templates": ["stakeholder_template", "capability_template", "mission_template"]
    },
    "system": {
        "name": "System Analysis", 
        "description": "Defining system requirements and functions",
        "icon": "⚙️",
        "keywords": ["function", "requirement", "interface", "system", "constraint", "mode", "service"],
        "requirement_types": ["functional", "performance", "interface"],
        "templates": ["functional_template", "interface_template", "constraint_template"]
    },
    "logical": {
        "name": "Logical Architecture",
        "description": "Designing solution components and interfaces", 
        "icon": "🏗️",
        "keywords": ["component", "logical", "behavior", "interaction", "scenario", "exchange", "protocol"],
        "requirement_types": ["functional", "behavioral", "interaction"],
        "templates": ["component_template", "behavior_template", "interaction_template"]
    },
    "physical": {
        "name": "Physical Architecture",
        "description": "Implementing and deploying the solution",
        "icon": "🔧", 
        "keywords": ["physical", "implementation", "deployment", "node", "configuration", "hardware", "software"],
        "requirement_types": ["implementation", "deployment", "hardware", "software"],
        "templates": ["implementation_template", "deployment_template", "hardware_template"]
    }
}

# Requirement Categories Mapping
REQUIREMENT_CATEGORIES = {
    "functional": {
        "prefix": "FR",
        "description": "System functions and capabilities",
        "keywords": ["shall", "must", "will", "should"]
    },
    "non_functional": {
        "prefix": "NFR", 
        "description": "Quality attributes and constraints",
        "subcategories": {
            "performance": "PERF",
            "security": "SEC",
            "usability": "USE",
            "reliability": "REL",
            "scalability": "SCAL",
            "maintainability": "MAIN"
        }
    },
    "stakeholder": {
        "prefix": "STK",
        "description": "Stakeholder-specific requirements",
        "keywords": ["stakeholder", "user", "actor"]
    }
}

# Priority Levels (aligned with CYDERCO methodology)
PRIORITY_LEVELS = {
    "MUST": {
        "description": "Critical requirements that must be implemented",
        "weight": 5
    },
    "SHOULD": {
        "description": "Important requirements that should be implemented",
        "weight": 3
    },
    "COULD": {
        "description": "Optional requirements that could be implemented",
        "weight": 1
    }
}

# MBSE Context Types
MBSE_CONTEXT_TYPES = [
    "operational",
    "system", 
    "logical",
    "physical",
    "verification",
    "traceability"
]