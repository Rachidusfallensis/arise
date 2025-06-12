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
            "generation": """Based on the following ARCADIA {phase} analysis, generate functional requirements with appropriate priorities based on criticality analysis.

Context: {context}
Stakeholders: {stakeholders}
Phase Focus: {phase_description}

PRIORITY ASSIGNMENT GUIDELINES (ARCADIA-compliant):
- MUST: Safety-critical, regulatory compliance, core security functions, mission-critical operations
- SHOULD: Important operational features, performance requirements, significant stakeholder needs
- COULD: Enhancement features, convenience functions, nice-to-have capabilities

Generate requirements in the format:
- ID: {prefix}-{phase}-XXX
- The system shall [specific action/capability for mentioned components]
- Priority: MUST/SHOULD/COULD (analyze context for criticality indicators)
- Verification: [specific verification method]
- Rationale: [why this priority was assigned]

Focus on: {phase_keywords}

Make requirements SPECIFIC to components mentioned in the context rather than generic statements."""
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
            "generation": """Based on the following ARCADIA {phase} analysis, generate non-functional requirements with priority analysis.

Context: {context}
Quality Attributes: Performance, Security, Usability, Reliability, Scalability
Phase: {phase}

PRIORITY ASSIGNMENT GUIDELINES:
- MUST: Security requirements, regulatory compliance, safety-critical performance, backup/recovery
- SHOULD: Performance targets, scalability requirements, important usability features
- COULD: Advanced features, optimization requirements, convenience enhancements

Generate measurable non-functional requirements for category: {category}
- ID: NFR-{category}-XXX
- The system shall [quality attribute] [measurable criteria for specific components]
- Metric: [how to measure]
- Target: [specific value or range]
- Priority: MUST/SHOULD/COULD (based on criticality analysis)
- Rationale: [justification for priority assignment]

Focus on specific components mentioned in the context."""
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