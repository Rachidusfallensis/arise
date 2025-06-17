from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ARCADIAPhase(Enum):
    """ARCADIA methodology phases"""
    OPERATIONAL = "operational"
    SYSTEM = "system"
    LOGICAL = "logical"
    PHYSICAL = "physical"

@dataclass
class RequirementTemplate:
    """Template for generating requirements"""
    pattern: str
    description: str
    example: str
    variables: List[str]
    verification_methods: List[str]
    quality_criteria: List[str]

@dataclass
class PhaseTemplate:
    """Complete template for an ARCADIA phase"""
    phase: ARCADIAPhase
    objective: str
    key_concepts: List[str]
    stakeholders: List[str]
    deliverables: List[str]
    requirement_templates: Dict[str, List[RequirementTemplate]]
    validation_criteria: List[str]
    traceability_rules: List[str]

class ARCADIAPhaseTemplates:
    """
    Comprehensive templates for each ARCADIA phase to ensure:
    - Consistent requirement generation
    - Phase-appropriate content
    - Proper traceability
    - Quality validation criteria
    """
    
    def __init__(self):
        self.templates = self._initialize_phase_templates()
    
    def _initialize_phase_templates(self) -> Dict[ARCADIAPhase, PhaseTemplate]:
        """Initialize all phase templates"""
        return {
            ARCADIAPhase.OPERATIONAL: self._create_operational_template(),
            ARCADIAPhase.SYSTEM: self._create_system_template(),
            ARCADIAPhase.LOGICAL: self._create_logical_template(),
            ARCADIAPhase.PHYSICAL: self._create_physical_template()
        }
    
    def _create_operational_template(self) -> PhaseTemplate:
        """Create operational analysis phase template"""
        
        functional_templates = [
            RequirementTemplate(
                pattern="The {stakeholder} shall be able to {capability} in order to {mission_objective}",
                description="Operational capability requirement linking stakeholder needs to mission objectives",
                example="The Mission Commander shall be able to plan operational missions in order to achieve mission success",
                variables=["stakeholder", "capability", "mission_objective"],
                verification_methods=[
                    "Stakeholder interview and validation",
                    "Operational scenario walkthrough",
                    "Mission effectiveness assessment"
                ],
                quality_criteria=[
                    "Clear stakeholder identification",
                    "Measurable capability description",
                    "Traceable to mission objectives"
                ]
            ),
            RequirementTemplate(
                pattern="During {operational_scenario}, the system shall {action} within {performance_constraint}",
                description="Scenario-based operational requirement with performance constraints",
                example="During emergency response scenarios, the system shall alert all operators within 30 seconds",
                variables=["operational_scenario", "action", "performance_constraint"],
                verification_methods=[
                    "Scenario simulation",
                    "Performance testing",
                    "Stakeholder acceptance testing"
                ],
                quality_criteria=[
                    "Specific scenario context",
                    "Clear action definition",
                    "Quantifiable constraints"
                ]
            ),
            RequirementTemplate(
                pattern="The operational capability {capability} requires {resource_type} to achieve {outcome}",
                description="Resource-based capability requirement",
                example="The operational capability Real-time Monitoring requires sensor data to achieve situational awareness",
                variables=["capability", "resource_type", "outcome"],
                verification_methods=[
                    "Resource availability analysis",
                    "Capability demonstration",
                    "Outcome measurement"
                ],
                quality_criteria=[
                    "Capability clearly defined",
                    "Resource requirements specified",
                    "Measurable outcomes"
                ]
            )
        ]
        
        non_functional_templates = [
            RequirementTemplate(
                pattern="The operational performance shall achieve {metric} of {target_value} under {operational_conditions}",
                description="Operational performance requirement with specific metrics",
                example="The operational performance shall achieve availability of 99.5% under normal operational conditions",
                variables=["metric", "target_value", "operational_conditions"],
                verification_methods=[
                    "Performance monitoring",
                    "Statistical analysis",
                    "Operational testing"
                ],
                quality_criteria=[
                    "Quantifiable metrics",
                    "Realistic targets",
                    "Defined conditions"
                ]
            ),
            RequirementTemplate(
                pattern="The system shall ensure {security_aspect} for {asset} against {threat_type}",
                description="Security requirement for operational assets",
                example="The system shall ensure confidentiality for mission data against unauthorized access",
                variables=["security_aspect", "asset", "threat_type"],
                verification_methods=[
                    "Security assessment",
                    "Threat analysis",
                    "Penetration testing"
                ],
                quality_criteria=[
                    "Specific security aspects",
                    "Identified assets",
                    "Defined threats"
                ]
            )
        ]
        
        return PhaseTemplate(
            phase=ARCADIAPhase.OPERATIONAL,
            objective="Define operational needs, capabilities, and stakeholder requirements",
            key_concepts=[
                "Operational capabilities",
                "Stakeholder needs",
                "Mission objectives",
                "Operational scenarios",
                "Performance expectations"
            ],
            stakeholders=[
                "Mission Commander",
                "Field Operators",
                "System Users",
                "Maintenance Personnel",
                "External Entities"
            ],
            deliverables=[
                "Operational capability models",
                "Stakeholder requirements",
                "Operational scenarios",
                "Performance criteria"
            ],
            requirement_templates={
                "functional": functional_templates,
                "non_functional": non_functional_templates
            },
            validation_criteria=[
                "Stakeholder validation completed",
                "Operational scenarios verified",
                "Capability gaps identified",
                "Performance criteria defined"
            ],
            traceability_rules=[
                "Requirements trace to stakeholder needs",
                "Capabilities link to mission objectives",
                "Scenarios validate operational concepts",
                "Performance criteria support capabilities"
            ]
        )
    
    def _create_system_template(self) -> PhaseTemplate:
        """Create system analysis phase template"""
        
        functional_templates = [
            RequirementTemplate(
                pattern="The system shall {function} to support {operational_capability}",
                description="System function requirement supporting operational capabilities",
                example="The system shall process sensor data to support real-time monitoring capability",
                variables=["function", "operational_capability"],
                verification_methods=[
                    "Functional testing",
                    "Capability traceability check",
                    "System integration testing"
                ],
                quality_criteria=[
                    "Clear function definition",
                    "Traceable to operational capability",
                    "Testable implementation"
                ]
            ),
            RequirementTemplate(
                pattern="When {system_condition}, the system shall {response} within {timeframe}",
                description="Conditional system response requirement",
                example="When sensor failure is detected, the system shall switch to backup sensors within 5 seconds",
                variables=["system_condition", "response", "timeframe"],
                verification_methods=[
                    "Condition simulation",
                    "Response time testing",
                    "Fault injection testing"
                ],
                quality_criteria=[
                    "Specific trigger conditions",
                    "Defined system response",
                    "Measurable timeframes"
                ]
            ),
            RequirementTemplate(
                pattern="The system function {function} shall interface with {external_system} via {interface_type}",
                description="System interface requirement",
                example="The system function Data Processing shall interface with External Database via secure API",
                variables=["function", "external_system", "interface_type"],
                verification_methods=[
                    "Interface testing",
                    "Protocol verification",
                    "Integration validation"
                ],
                quality_criteria=[
                    "Function clearly identified",
                    "External system specified",
                    "Interface type defined"
                ]
            )
        ]
        
        non_functional_templates = [
            RequirementTemplate(
                pattern="The system shall process {data_volume} within {processing_time} with {accuracy_level}",
                description="System performance requirement with specific metrics",
                example="The system shall process 1000 sensor readings within 100 milliseconds with 99.9% accuracy",
                variables=["data_volume", "processing_time", "accuracy_level"],
                verification_methods=[
                    "Performance benchmarking",
                    "Load testing",
                    "Accuracy measurement"
                ],
                quality_criteria=[
                    "Quantified data volumes",
                    "Specific time constraints",
                    "Measurable accuracy"
                ]
            ),
            RequirementTemplate(
                pattern="The system shall maintain {reliability_metric} during {operational_period}",
                description="System reliability requirement",
                example="The system shall maintain 99.9% uptime during 24/7 operational periods",
                variables=["reliability_metric", "operational_period"],
                verification_methods=[
                    "Reliability testing",
                    "MTBF analysis",
                    "Availability monitoring"
                ],
                quality_criteria=[
                    "Specific reliability metrics",
                    "Defined operational periods",
                    "Measurable targets"
                ]
            )
        ]
        
        return PhaseTemplate(
            phase=ARCADIAPhase.SYSTEM,
            objective="Define system functions and architecture to realize operational capabilities",
            key_concepts=[
                "System functions",
                "Functional chains",
                "System interfaces",
                "Performance requirements",
                "System boundaries"
            ],
            stakeholders=[
                "System Architects",
                "System Engineers",
                "Operations Personnel",
                "External System Providers"
            ],
            deliverables=[
                "System functional architecture",
                "System requirements specification",
                "Interface definitions",
                "Performance specifications"
            ],
            requirement_templates={
                "functional": functional_templates,
                "non_functional": non_functional_templates
            },
            validation_criteria=[
                "Functions trace to capabilities",
                "Interfaces properly defined",
                "Performance requirements validated",
                "System boundaries established"
            ],
            traceability_rules=[
                "System functions implement operational capabilities",
                "Interfaces support functional chains",
                "Performance requirements enable capabilities",
                "System boundaries align with operational scope"
            ]
        )
    
    def _create_logical_template(self) -> PhaseTemplate:
        """Create logical architecture phase template"""
        
        functional_templates = [
            RequirementTemplate(
                pattern="The {component} shall implement {function} with {quality_attributes}",
                description="Component allocation requirement with quality attributes",
                example="The Data Manager component shall implement data storage function with high availability and security",
                variables=["component", "function", "quality_attributes"],
                verification_methods=[
                    "Component design review",
                    "Quality attribute testing",
                    "Architecture validation"
                ],
                quality_criteria=[
                    "Component clearly identified",
                    "Function properly allocated",
                    "Quality attributes specified"
                ]
            ),
            RequirementTemplate(
                pattern="Component {component} shall communicate with {other_component} via {interface_specification}",
                description="Inter-component communication requirement",
                example="Component Sensor Manager shall communicate with Data Processor via message queue interface",
                variables=["component", "other_component", "interface_specification"],
                verification_methods=[
                    "Interface consistency check",
                    "Communication testing",
                    "Protocol validation"
                ],
                quality_criteria=[
                    "Components identified",
                    "Interface specification complete",
                    "Communication protocol defined"
                ]
            ),
            RequirementTemplate(
                pattern="The logical architecture shall support {system_function} through {component_allocation}",
                description="Architecture support requirement",
                example="The logical architecture shall support real-time processing through distributed component allocation",
                variables=["system_function", "component_allocation"],
                verification_methods=[
                    "Architecture analysis",
                    "Function allocation verification",
                    "Performance validation"
                ],
                quality_criteria=[
                    "System function traceable",
                    "Component allocation justified",
                    "Architecture coherent"
                ]
            )
        ]
        
        non_functional_templates = [
            RequirementTemplate(
                pattern="The {component} shall achieve {performance_metric} under {load_conditions}",
                description="Component performance requirement",
                example="The Data Processor shall achieve 1000 transactions/second under peak load conditions",
                variables=["component", "performance_metric", "load_conditions"],
                verification_methods=[
                    "Component performance testing",
                    "Load simulation",
                    "Benchmark analysis"
                ],
                quality_criteria=[
                    "Component performance quantified",
                    "Load conditions specified",
                    "Metrics measurable"
                ]
            ),
            RequirementTemplate(
                pattern="The logical interface {interface} shall ensure {quality_property} between {components}",
                description="Interface quality requirement",
                example="The logical interface MessageBus shall ensure data integrity between all processing components",
                variables=["interface", "quality_property", "components"],
                verification_methods=[
                    "Interface quality testing",
                    "Data integrity verification",
                    "Component interaction analysis"
                ],
                quality_criteria=[
                    "Interface clearly defined",
                    "Quality property measurable",
                    "Components identified"
                ]
            )
        ]
        
        return PhaseTemplate(
            phase=ARCADIAPhase.LOGICAL,
            objective="Define logical components and their allocation to realize system functions",
            key_concepts=[
                "Logical components",
                "Component allocation",
                "Logical interfaces",
                "Data flows",
                "Component interactions"
            ],
            stakeholders=[
                "Software Architects",
                "Component Designers",
                "Integration Engineers",
                "Quality Assurance"
            ],
            deliverables=[
                "Logical architecture model",
                "Component specifications",
                "Interface definitions",
                "Data flow diagrams"
            ],
            requirement_templates={
                "functional": functional_templates,
                "non_functional": non_functional_templates
            },
            validation_criteria=[
                "Components properly allocated",
                "Interfaces consistently defined",
                "Data flows validated",
                "Quality attributes addressed"
            ],
            traceability_rules=[
                "Components realize system functions",
                "Interfaces support functional chains",
                "Data flows enable system operations",
                "Quality attributes trace to system NFRs"
            ]
        )
    
    def _create_physical_template(self) -> PhaseTemplate:
        """Create physical architecture phase template"""
        
        functional_templates = [
            RequirementTemplate(
                pattern="The {physical_component} shall realize {logical_component} using {technology}",
                description="Physical realization requirement",
                example="The Database Server shall realize Data Manager component using PostgreSQL technology",
                variables=["physical_component", "logical_component", "technology"],
                verification_methods=[
                    "Implementation verification",
                    "Technology validation",
                    "Component realization testing"
                ],
                quality_criteria=[
                    "Physical component identified",
                    "Logical component traced",
                    "Technology appropriate"
                ]
            ),
            RequirementTemplate(
                pattern="Physical component {component} shall operate in {environment} with {constraints}",
                description="Environmental operation requirement",
                example="Physical component Field Sensor shall operate in outdoor environment with temperature range -20°C to +60°C",
                variables=["component", "environment", "constraints"],
                verification_methods=[
                    "Environmental testing",
                    "Constraint verification",
                    "Operational validation"
                ],
                quality_criteria=[
                    "Component specified",
                    "Environment defined",
                    "Constraints measurable"
                ]
            ),
            RequirementTemplate(
                pattern="The implementation shall meet {performance_criteria} under {operational_conditions}",
                description="Implementation performance requirement",
                example="The implementation shall meet 99.9% availability under 24/7 operational conditions",
                variables=["performance_criteria", "operational_conditions"],
                verification_methods=[
                    "Performance testing",
                    "Operational validation",
                    "Availability monitoring"
                ],
                quality_criteria=[
                    "Performance criteria quantified",
                    "Operational conditions specified",
                    "Implementation traceable"
                ]
            )
        ]
        
        non_functional_templates = [
            RequirementTemplate(
                pattern="The physical system shall consume maximum {resource_amount} of {resource_type} during {operation_mode}",
                description="Resource consumption requirement",
                example="The physical system shall consume maximum 500W of electrical power during normal operation mode",
                variables=["resource_amount", "resource_type", "operation_mode"],
                verification_methods=[
                    "Resource monitoring",
                    "Consumption testing",
                    "Efficiency analysis"
                ],
                quality_criteria=[
                    "Resource amount quantified",
                    "Resource type specified",
                    "Operation mode defined"
                ]
            ),
            RequirementTemplate(
                pattern="The deployment shall support {scalability_requirement} within {infrastructure_constraints}",
                description="Deployment scalability requirement",
                example="The deployment shall support horizontal scaling to 100 nodes within cloud infrastructure constraints",
                variables=["scalability_requirement", "infrastructure_constraints"],
                verification_methods=[
                    "Scalability testing",
                    "Infrastructure validation",
                    "Deployment verification"
                ],
                quality_criteria=[
                    "Scalability quantified",
                    "Infrastructure constraints defined",
                    "Deployment feasible"
                ]
            )
        ]
        
        return PhaseTemplate(
            phase=ARCADIAPhase.PHYSICAL,
            objective="Define physical implementation and deployment of logical components",
            key_concepts=[
                "Physical components",
                "Technology choices",
                "Environmental constraints",
                "Implementation details",
                "Deployment scenarios"
            ],
            stakeholders=[
                "Hardware Engineers",
                "Implementation Teams",
                "Deployment Engineers",
                "Operations Personnel"
            ],
            deliverables=[
                "Physical architecture model",
                "Implementation specifications",
                "Deployment plans",
                "Technology selections"
            ],
            requirement_templates={
                "functional": functional_templates,
                "non_functional": non_functional_templates
            },
            validation_criteria=[
                "Physical components specified",
                "Technologies validated",
                "Environmental constraints addressed",
                "Deployment feasibility confirmed"
            ],
            traceability_rules=[
                "Physical components realize logical components",
                "Technologies support functional requirements",
                "Environmental constraints enable operations",
                "Deployment supports system objectives"
            ]
        )
    
    def get_template(self, phase: str) -> Optional[PhaseTemplate]:
        """Get template for specified phase"""
        try:
            arcadia_phase = ARCADIAPhase(phase.lower())
            return self.templates.get(arcadia_phase)
        except ValueError:
            return None
    
    def get_requirement_templates(self, phase: str, req_type: str) -> List[RequirementTemplate]:
        """Get requirement templates for specific phase and type"""
        template = self.get_template(phase)
        if template and req_type in template.requirement_templates:
            return template.requirement_templates[req_type]
        return []
    
    def get_verification_methods(self, phase: str, req_type: str) -> List[str]:
        """Get appropriate verification methods for phase and requirement type"""
        templates = self.get_requirement_templates(phase, req_type)
        methods = []
        for template in templates:
            methods.extend(template.verification_methods)
        return list(set(methods))  # Remove duplicates
    
    def get_quality_criteria(self, phase: str, req_type: str) -> List[str]:
        """Get quality criteria for phase and requirement type"""
        templates = self.get_requirement_templates(phase, req_type)
        criteria = []
        for template in templates:
            criteria.extend(template.quality_criteria)
        return list(set(criteria))  # Remove duplicates
    
    def get_traceability_rules(self, phase: str) -> List[str]:
        """Get traceability rules for specified phase"""
        template = self.get_template(phase)
        return template.traceability_rules if template else []
    
    def get_validation_criteria(self, phase: str) -> List[str]:
        """Get validation criteria for specified phase"""
        template = self.get_template(phase)
        return template.validation_criteria if template else []
    
    def generate_requirement_from_template(self, 
                                         template: RequirementTemplate, 
                                         variables: Dict[str, str]) -> Dict[str, Any]:
        """Generate a requirement from template with provided variables"""
        # Replace variables in pattern
        requirement_text = template.pattern
        for var, value in variables.items():
            requirement_text = requirement_text.replace(f"{{{var}}}", value)
        
        return {
            "description": requirement_text,
            "template_used": template.pattern,
            "template_description": template.description,
            "example": template.example,
            "suggested_verification_methods": template.verification_methods,
            "quality_criteria": template.quality_criteria,
            "variables_used": variables
        }
    
    def validate_requirement_against_template(self, 
                                            requirement: Dict[str, Any], 
                                            phase: str) -> Dict[str, Any]:
        """Validate requirement against phase templates"""
        validation_result = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
            "template_compliance_score": 0.0
        }
        
        template = self.get_template(phase)
        if not template:
            validation_result["issues"].append(f"No template found for phase: {phase}")
            validation_result["is_valid"] = False
            return validation_result
        
        req_text = requirement.get("description", "").lower()
        req_type = requirement.get("type", "functional").lower()
        
        # Check against requirement templates
        templates = self.get_requirement_templates(phase, req_type)
        if not templates:
            validation_result["suggestions"].append(f"No templates available for {req_type} requirements in {phase} phase")
            return validation_result
        
        # Check key concepts presence
        key_concepts = [concept.lower() for concept in template.key_concepts]
        concept_matches = sum(1 for concept in key_concepts if concept in req_text)
        concept_score = concept_matches / len(key_concepts) if key_concepts else 0
        
        # Check quality criteria
        quality_criteria = self.get_quality_criteria(phase, req_type)
        criteria_score = self._evaluate_quality_criteria(requirement, quality_criteria)
        
        # Calculate overall compliance score
        validation_result["template_compliance_score"] = (concept_score + criteria_score) / 2
        
        # Generate suggestions
        if concept_score < 0.3:
            validation_result["suggestions"].append(
                f"Consider including phase-specific concepts: {', '.join(template.key_concepts[:3])}"
            )
        
        if criteria_score < 0.5:
            validation_result["suggestions"].append(
                f"Improve requirement quality based on criteria: {', '.join(quality_criteria[:3])}"
            )
        
        if validation_result["template_compliance_score"] < 0.6:
            validation_result["is_valid"] = False
            validation_result["issues"].append(
                f"Low template compliance score: {validation_result['template_compliance_score']:.2f}"
            )
        
        return validation_result
    
    def _evaluate_quality_criteria(self, requirement: Dict[str, Any], criteria: List[str]) -> float:
        """Evaluate requirement against quality criteria"""
        if not criteria:
            return 1.0
        
        score = 0.0
        req_text = requirement.get("description", "").lower()
        
        for criterion in criteria:
            if "clear" in criterion.lower() and any(word in req_text for word in ["shall", "must", "will"]):
                score += 1
            elif "measurable" in criterion.lower() and any(char.isdigit() for char in req_text):
                score += 1
            elif "specific" in criterion.lower() and len(req_text.split()) > 10:
                score += 1
            elif "traceable" in criterion.lower() and requirement.get("traceability_links"):
                score += 1
        
        return score / len(criteria)
    
    def export_templates_summary(self) -> Dict[str, Any]:
        """Export summary of all phase templates"""
        summary = {}
        
        for phase, template in self.templates.items():
            summary[phase.value] = {
                "objective": template.objective,
                "key_concepts": template.key_concepts,
                "stakeholders": template.stakeholders,
                "deliverables": template.deliverables,
                "functional_templates": len(template.requirement_templates.get("functional", [])),
                "non_functional_templates": len(template.requirement_templates.get("non_functional", [])),
                "validation_criteria": template.validation_criteria,
                "traceability_rules": template.traceability_rules
            }
        
        return summary 