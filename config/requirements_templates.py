from typing import Dict, Any

# Requirement Templates based on ARCADIA methodology
REQUIREMENT_TEMPLATES = {
    "functional_template": {
        "structure": {
            "id": "{prefix}-{phase}-{number:03d}",
            "type": "Functional",
            "title": "{title}",
            "description": "The system shall {description}",
            "priority": "{priority}",
            "phase": "{arcadia_phase}",
            "stakeholder": "{stakeholder}",
            "verification_method": "{verification}",
            "dependencies": [],
            "rationale": "{rationale}"
        },
        "prompts": {
            "generation": """Based on the following ARCADIA {phase} analysis, generate functional requirements.
            
Context: {context}
Stakeholders: {stakeholders}
Phase Focus: {phase_description}

Generate requirements in the format:
- ID: {prefix}-{phase}-XXX
- The system shall [specific action/capability]
- Priority: MUST/SHOULD/COULD
- Verification: [how to verify this requirement]

Focus on: {phase_keywords}"""
        }
    },
    
    "non_functional_template": {
        "structure": {
            "id": "{prefix}-{category}-{number:03d}",
            "type": "Non-Functional",
            "category": "{nfr_category}",
            "title": "{title}",
            "description": "The system shall {description}",
            "metric": "{metric}",
            "target_value": "{target}",
            "priority": "{priority}",
            "phase": "{arcadia_phase}",
            "verification_method": "{verification}"
        },
        "prompts": {
            "generation": """Based on the following ARCADIA {phase} analysis, generate non-functional requirements.
            
Context: {context}
Quality Attributes: Performance, Security, Usability, Reliability, Scalability
Phase: {phase}

Generate measurable non-functional requirements:
- ID: NFR-{category}-XXX
- The system shall [quality attribute] [measurable criteria]
- Metric: [how to measure]
- Target: [specific value or range]
- Priority: MUST/SHOULD/COULD"""
        }
    },
    
    "stakeholder_template": {
        "structure": {
            "id": "STK-{number:03d}",
            "type": "Stakeholder",
            "name": "{stakeholder_name}",
            "role": "{role}",
            "interests": [],
            "requirements": [],
            "influence": "{influence_level}",
            "phase": "operational"
        },
        "prompts": {
            "identification": """From the following project description, identify and analyze stakeholders:
            
Project Context: {context}

For each stakeholder, provide:
- Name/Role
- Primary interests in the system
- Influence level (High/Medium/Low)
- Specific requirements or needs
- ARCADIA phase relevance"""
        }
    }
}

# CYDERCO Compatibility Mapping
CYDERCO_REQUIREMENTS_MAPPING = {
    "FUNC-DA": "Data Analytics functional requirements",
    "FUNC-NTA": "Network Traffic Analysis requirements", 
    "FUNC-HIDS": "Host Intrusion Detection requirements",
    "FUNC-AI": "AI-driven Analytics requirements",
    "FUNC-TIS": "Threat Intelligence Sharing requirements",
    "NFUNC-DA": "Data Analytics non-functional requirements",
    "NFUNC-NTA": "Network Traffic Analysis non-functional requirements"
}