from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from .arcadia_context_enricher import ARCADIAContextEnricher
from .requirements_validation_pipeline import RequirementsValidationPipeline, ValidationReport
from .enhanced_requirements_generator import EnhancedRequirementsGenerator
from .requirements_improvement_service import RequirementsImprovementService
from ..templates.arcadia_phase_templates import ARCADIAPhaseTemplates

@dataclass
class EnhancedRAGResult:
    """Result from enhanced RAG service"""
    requirements: Dict[str, Any]
    validation_report: Optional[ValidationReport]
    enrichment_summary: Dict[str, Any]
    template_compliance: Dict[str, Any]
    quality_score: float
    recommendations: List[str]

class EnhancedRAGService:
    """
    Enhanced RAG service integrating:
    1. ARCADIA context enrichment with traceability matrices, capabilities catalog, and actor dictionary
    2. Automatic validation pipeline with syntactic, semantic, coverage, and quality checks
    3. Phase-specific templates for consistent and compliant requirements generation
    4. Comprehensive quality scoring and improvement recommendations
    """
    
    def __init__(self, ollama_client):
        self.logger = logging.getLogger(__name__)
        self.ollama_client = ollama_client
        
        # Initialize core components
        self.arcadia_enricher = ARCADIAContextEnricher()
        self.validation_pipeline = RequirementsValidationPipeline(self.arcadia_enricher)
        self.enhanced_generator = EnhancedRequirementsGenerator(ollama_client)
        self.improvement_service = RequirementsImprovementService(ollama_client)
        self.phase_templates = ARCADIAPhaseTemplates()
        
        self.logger.info("Enhanced RAG service initialized with all components")

    def generate_enhanced_requirements(self, 
                                     context: List[Dict[str, Any]], 
                                     phase: str, 
                                     proposal_text: str,
                                     requirement_types: List[str],
                                     enable_validation: bool = True,
                                     enable_enrichment: bool = True) -> EnhancedRAGResult:
        """
        Generate requirements with full enhancement pipeline
        """
        self.logger.info(f"Starting enhanced requirements generation for {phase} phase")
        
        # Step 1: Enrich context with ARCADIA knowledge
        enriched_context = context
        enrichment_summary = {}
        
        if enable_enrichment:
            self.logger.info("Enriching context with ARCADIA knowledge")
            enriched_context = self.arcadia_enricher.enrich_context_for_requirements_generation(
                phase, context, requirement_types
            )
            enrichment_summary = self._create_enrichment_summary(context, enriched_context)
        
        # Step 2: Add phase-specific template guidance
        template_context = self._add_template_guidance(phase, requirement_types)
        enriched_context.extend(template_context)
        
        # Step 3: Generate requirements using enhanced generator
        self.logger.info("Generating requirements with enhanced generator")
        requirements_result = self.enhanced_generator.generate_balanced_requirements(
            enriched_context, phase, proposal_text, requirement_types
        )
        
        # Step 4: Validate generated requirements
        validation_report = None
        if enable_validation:
            self.logger.info("Running validation pipeline")
            validation_report = self.validation_pipeline.validate_requirements(
                requirements_result, phase, enriched_context
            )
        
        # Step 5: Check template compliance
        template_compliance = self._check_template_compliance(requirements_result, phase)
        
        # Step 6: Calculate overall quality score
        quality_score = self._calculate_overall_quality_score(
            requirements_result, validation_report, template_compliance
        )
        
        # Step 7: Generate comprehensive recommendations
        recommendations = self._generate_comprehensive_recommendations(
            requirements_result, validation_report, template_compliance, quality_score
        )
        
        # Create enhanced result
        result = EnhancedRAGResult(
            requirements=requirements_result,
            validation_report=validation_report,
            enrichment_summary=enrichment_summary,
            template_compliance=template_compliance,
            quality_score=quality_score,
            recommendations=recommendations
        )
        
        self.logger.info(f"Enhanced requirements generation completed. Quality score: {quality_score:.2f}")
        
        return result

    def _create_enrichment_summary(self, 
                                 original_context: List[Dict[str, Any]], 
                                 enriched_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary of context enrichment"""
        
        original_count = len(original_context)
        enriched_count = len(enriched_context)
        added_count = enriched_count - original_count
        
        # Analyze enrichment types
        enrichment_types: Dict[str, int] = {}
        for chunk in enriched_context[original_count:]:
            enrichment_type = chunk.get("metadata", {}).get("enrichment_type", "unknown")
            enrichment_types[enrichment_type] = enrichment_types.get(enrichment_type, 0) + 1
        
        # Get ARCADIA knowledge summary
        arcadia_summary = self.arcadia_enricher.export_knowledge_summary()
        
        return {
            "original_chunks": original_count,
            "enriched_chunks": enriched_count,
            "added_chunks": added_count,
            "enrichment_types": enrichment_types,
            "arcadia_knowledge": arcadia_summary,
            "enrichment_effectiveness": min(1.0, added_count / max(1, original_count))
        }

    def _add_template_guidance(self, phase: str, requirement_types: List[str]) -> List[Dict[str, Any]]:
        """Add phase-specific template guidance to context"""
        
        template_context = []
        phase_template = self.phase_templates.get_template(phase)
        
        if phase_template:
            # Add general phase guidance
            guidance_text = f"ARCADIA {phase.upper()} PHASE GUIDANCE:\n\n"
            guidance_text += f"Objective: {phase_template.objective}\n\n"
            guidance_text += f"Key Concepts to Address:\n"
            for concept in phase_template.key_concepts:
                guidance_text += f"• {concept}\n"
            guidance_text += "\n"
            
            guidance_text += f"Stakeholders Involved:\n"
            for stakeholder in phase_template.stakeholders:
                guidance_text += f"• {stakeholder}\n"
            guidance_text += "\n"
            
            guidance_text += f"Validation Criteria:\n"
            for criterion in phase_template.validation_criteria:
                guidance_text += f"• {criterion}\n"
            guidance_text += "\n"
            
            guidance_text += f"Traceability Rules:\n"
            for rule in phase_template.traceability_rules:
                guidance_text += f"• {rule}\n"
            
            template_context.append({
                "content": guidance_text,
                "source": "arcadia_phase_templates",
                "type": "phase_guidance",
                "metadata": {
                    "phase": phase,
                    "enrichment_type": "phase_guidance"
                }
            })
            
            # Add requirement-specific templates
            for req_type in requirement_types:
                templates = self.phase_templates.get_requirement_templates(phase, req_type)
                if templates:
                    template_text = f"REQUIREMENT TEMPLATES FOR {req_type.upper()} REQUIREMENTS:\n\n"
                    
                    for i, template in enumerate(templates, 1):
                        template_text += f"{i}. Pattern: {template.pattern}\n"
                        template_text += f"   Description: {template.description}\n"
                        template_text += f"   Example: {template.example}\n"
                        template_text += f"   Variables: {', '.join(template.variables)}\n"
                        template_text += f"   Verification Methods: {', '.join(template.verification_methods[:2])}\n\n"
                    
                    template_context.append({
                        "content": template_text,
                        "source": "arcadia_templates",
                        "type": "requirement_templates",
                        "metadata": {
                            "phase": phase,
                            "requirement_type": req_type,
                            "template_count": len(templates),
                            "enrichment_type": "requirement_templates"
                        }
                    })
        
        return template_context

    def _check_template_compliance(self, requirements_data: Dict[str, Any], phase: str) -> Dict[str, Any]:
        """Check compliance with phase-specific templates"""
        
        compliance_results: Dict[str, Any] = {
            "overall_compliance": 0.0,
            "requirement_compliance": [],
            "phase_alignment": 0.0,
            "template_usage": {},
            "compliance_issues": []
        }
        
        # Extract all requirements
        all_requirements = []
        for req_type, reqs in requirements_data.items():
            if req_type != "stakeholders" and isinstance(reqs, list):
                all_requirements.extend(reqs)
        
        if not all_requirements:
            return compliance_results
        
        # Check each requirement against templates
        compliance_scores = []
        for req in all_requirements:
            req_compliance = self.phase_templates.validate_requirement_against_template(req, phase)
            compliance_scores.append(req_compliance["template_compliance_score"])
            
            compliance_results["requirement_compliance"].append({
                "requirement_id": req.get("id", "UNKNOWN"),
                "compliance_score": req_compliance["template_compliance_score"],
                "is_valid": req_compliance["is_valid"],
                "issues": req_compliance["issues"],
                "suggestions": req_compliance["suggestions"]
            })
            
            # Collect issues
            if not req_compliance["is_valid"]:
                compliance_results["compliance_issues"].extend(req_compliance["issues"])
        
        # Calculate overall compliance
        compliance_results["overall_compliance"] = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
        
        # Check phase alignment
        phase_template = self.phase_templates.get_template(phase)
        if phase_template:
            phase_concepts = [concept.lower() for concept in phase_template.key_concepts]
            concept_mentions = 0
            total_text = ""
            
            for req in all_requirements:
                total_text += req.get("description", "").lower() + " "
            
            for concept in phase_concepts:
                if concept in total_text:
                    concept_mentions += 1
            
            compliance_results["phase_alignment"] = concept_mentions / len(phase_concepts) if phase_concepts else 1.0
        
        # Analyze template usage
        functional_reqs = [req for req in all_requirements if req.get("type") == "Functional"]
        nfr_reqs = [req for req in all_requirements if req.get("type") == "Non-Functional"]
        
        compliance_results["template_usage"] = {
            "functional_requirements": len(functional_reqs),
            "non_functional_requirements": len(nfr_reqs),
            "template_patterns_detected": self._detect_template_patterns(all_requirements, phase),
            "verification_methods_used": self._analyze_verification_methods(all_requirements, phase)
        }
        
        return compliance_results

    def _detect_template_patterns(self, requirements: List[Dict[str, Any]], phase: str) -> Dict[str, int]:
        """Detect which template patterns are used in requirements"""
        
        pattern_usage = {}
        
        for req_type in ["functional", "non_functional"]:
            templates = self.phase_templates.get_requirement_templates(phase, req_type)
            
            for template in templates:
                pattern_key = template.pattern.split()[0:3]  # First 3 words as key
                pattern_name = " ".join(pattern_key)
                pattern_usage[pattern_name] = 0
                
                for req in requirements:
                    req_text = req.get("description", "").lower()
                    if all(word.lower() in req_text for word in pattern_key if word.lower() not in ["the", "shall", "a", "an"]):
                        pattern_usage[pattern_name] += 1
        
        return pattern_usage

    def _analyze_verification_methods(self, requirements: List[Dict[str, Any]], phase: str) -> Dict[str, Any]:
        """Analyze verification methods used vs. recommended"""
        
        used_methods = []
        for req in requirements:
            method = req.get("verification_method", "")
            if method:
                used_methods.append(method)
        
        recommended_functional = self.phase_templates.get_verification_methods(phase, "functional")
        recommended_nfr = self.phase_templates.get_verification_methods(phase, "non_functional")
        all_recommended = recommended_functional + recommended_nfr
        
        # Check alignment with recommendations
        aligned_methods = 0
        for method in used_methods:
            if any(rec_method.lower() in method.lower() for rec_method in all_recommended):
                aligned_methods += 1
        
        return {
            "used_methods": used_methods,
            "recommended_methods": all_recommended,
            "alignment_score": aligned_methods / len(used_methods) if used_methods else 0.0,
            "unique_methods_used": len(set(used_methods)),
            "generic_methods_count": len([m for m in used_methods if m.lower() in ["review and testing", "testing", "validation"]])
        }

    def _calculate_overall_quality_score(self, 
                                       requirements_data: Dict[str, Any],
                                       validation_report: Optional[ValidationReport],
                                       template_compliance: Dict[str, Any]) -> float:
        """Calculate overall quality score combining all metrics"""
        
        scores = []
        
        # Validation score
        if validation_report:
            scores.append(validation_report.overall_score)
        
        # Template compliance score
        scores.append(template_compliance.get("overall_compliance", 0.0))
        
        # Phase alignment score
        scores.append(template_compliance.get("phase_alignment", 0.0))
        
        # Requirements balance score
        balance_score = self._calculate_balance_score(requirements_data)
        scores.append(balance_score)
        
        # Calculate weighted average
        weights = [0.4, 0.25, 0.20, 0.15]  # Validation, compliance, alignment, balance
        weighted_score = sum(score * weight for score, weight in zip(scores, weights))
        
        return weighted_score

    def _calculate_balance_score(self, requirements_data: Dict[str, Any]) -> float:
        """Calculate score based on requirements balance"""
        
        total_reqs = 0
        functional_count = 0
        nfr_count = 0
        
        for req_type, reqs in requirements_data.items():
            if req_type == "stakeholders":
                continue
            if isinstance(reqs, list):
                total_reqs += len(reqs)
                if req_type == "functional":
                    functional_count = len(reqs)
                elif req_type == "non_functional":
                    nfr_count = len(reqs)
        
        if total_reqs == 0:
            return 0.0
        
        functional_ratio = functional_count / total_reqs
        nfr_ratio = nfr_count / total_reqs
        
        # Ideal ratios: 60% functional, 40% NFR
        functional_score = 1.0 - abs(functional_ratio - 0.6)
        nfr_score = 1.0 - abs(nfr_ratio - 0.4)
        
        return (functional_score + nfr_score) / 2

    def _generate_comprehensive_recommendations(self, 
                                              requirements_data: Dict[str, Any],
                                              validation_report: Optional[ValidationReport],
                                              template_compliance: Dict[str, Any],
                                              quality_score: float) -> List[str]:
        """Generate comprehensive improvement recommendations"""
        
        recommendations = []
        
        # Quality-based recommendations
        if quality_score < 0.6:
            recommendations.append("🚨 Overall quality is below acceptable threshold - comprehensive review needed")
        elif quality_score < 0.8:
            recommendations.append("⚠️ Quality has room for improvement - focus on key areas")
        else:
            recommendations.append("✅ Good quality achieved - minor refinements may be beneficial")
        
        # Validation-based recommendations
        if validation_report:
            critical_issues = len([issue for issue in validation_report.issues if issue.level.value == "critical"])
            major_issues = len([issue for issue in validation_report.issues if issue.level.value == "major"])
            
            if critical_issues > 0:
                recommendations.append(f"🔥 Address {critical_issues} critical validation issues immediately")
            
            if major_issues > 0:
                recommendations.append(f"📋 Resolve {major_issues} major validation issues")
            
            # Add top validation recommendations
            recommendations.extend(validation_report.recommendations[:3])
        
        # Template compliance recommendations
        if template_compliance.get("overall_compliance", 0) < 0.7:
            recommendations.append("📐 Improve compliance with ARCADIA phase templates")
        
        if template_compliance.get("phase_alignment", 0) < 0.6:
            recommendations.append("🎯 Better align requirements with phase-specific concepts")
        
        # Verification method recommendations
        verification_analysis = template_compliance.get("template_usage", {}).get("verification_methods_used", {})
        if verification_analysis.get("generic_methods_count", 0) > 0:
            recommendations.append("🔍 Replace generic verification methods with specific, phase-appropriate methods")
        
        # Coverage recommendations
        if validation_report and validation_report.gaps_identified:
            gap_count = len(validation_report.gaps_identified)
            recommendations.append(f"📊 Address {gap_count} coverage gaps in operational capabilities and actors")
        
        # Balance recommendations
        balance_score = self._calculate_balance_score(requirements_data)
        if balance_score < 0.7:
            recommendations.append("⚖️ Improve balance between functional and non-functional requirements")
        
        return recommendations[:10]  # Limit to top 10 recommendations

    def get_enhancement_dashboard_data(self, result: EnhancedRAGResult) -> Dict[str, Any]:
        """Generate comprehensive dashboard data for the enhanced result"""
        
        return {
            "quality_overview": {
                "overall_score": result.quality_score,
                "grade": self._get_quality_grade(result.quality_score),
                "total_requirements": sum(len(reqs) for reqs in result.requirements.values() if isinstance(reqs, list)),
                "recommendations_count": len(result.recommendations)
            },
            "validation_metrics": {
                "validation_score": result.validation_report.overall_score if result.validation_report else 0.0,
                "total_issues": len(result.validation_report.issues) if result.validation_report else 0,
                "critical_issues": len([issue for issue in result.validation_report.issues if issue.level.value == "critical"]) if result.validation_report else 0,
                "auto_fixable": len([issue for issue in result.validation_report.issues if issue.auto_fixable]) if result.validation_report else 0,
                "category_scores": result.validation_report.scores_by_category if result.validation_report else {}
            },
            "template_compliance": {
                "compliance_score": result.template_compliance.get("overall_compliance", 0.0),
                "phase_alignment": result.template_compliance.get("phase_alignment", 0.0),
                "compliance_issues": len(result.template_compliance.get("compliance_issues", [])),
                "template_usage": result.template_compliance.get("template_usage", {})
            },
            "enrichment_effectiveness": {
                "enrichment_score": result.enrichment_summary.get("enrichment_effectiveness", 0.0),
                "added_chunks": result.enrichment_summary.get("added_chunks", 0),
                "enrichment_types": result.enrichment_summary.get("enrichment_types", {}),
                "arcadia_knowledge": result.enrichment_summary.get("arcadia_knowledge", {})
            },
            "top_recommendations": result.recommendations[:5],
            "improvement_priority": self._calculate_improvement_priority(result)
        }

    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def _calculate_improvement_priority(self, result: EnhancedRAGResult) -> List[Dict[str, Any]]:
        """Calculate improvement priorities based on impact and effort"""
        
        priorities = []
        
        # Critical validation issues - high impact, low effort
        if result.validation_report:
            critical_count = len([issue for issue in result.validation_report.issues if issue.level.value == "critical"])
            if critical_count > 0:
                priorities.append({
                    "area": "Critical Validation Issues",
                    "impact": "high",
                    "effort": "low",
                    "count": critical_count,
                    "priority": 1
                })
        
        # Template compliance - medium impact, medium effort
        if result.template_compliance.get("overall_compliance", 0) < 0.7:
            priorities.append({
                "area": "Template Compliance",
                "impact": "medium",
                "effort": "medium",
                "score": result.template_compliance.get("overall_compliance", 0),
                "priority": 2
            })
        
        # Coverage gaps - high impact, high effort
        if result.validation_report and result.validation_report.gaps_identified:
            priorities.append({
                "area": "Coverage Gaps",
                "impact": "high",
                "effort": "high",
                "gaps": len(result.validation_report.gaps_identified),
                "priority": 3
            })
        
        # Quality improvements - variable impact and effort
        if result.quality_score < 0.8:
            priorities.append({
                "area": "Overall Quality",
                "impact": "medium",
                "effort": "medium",
                "score": result.quality_score,
                "priority": 4
            })
        
        return sorted(priorities, key=lambda x: x["priority"])

    def export_enhanced_results(self, result: EnhancedRAGResult, format: str = "json") -> str:
        """Export enhanced results in specified format"""
        
        if format.lower() == "json":
            import json
            export_data = {
                "enhanced_rag_results": {
                    "quality_score": result.quality_score,
                    "requirements": result.requirements,
                    "validation_report": {
                        "overall_score": result.validation_report.overall_score,
                        "total_requirements": result.validation_report.total_requirements,
                        "issues_count": len(result.validation_report.issues),
                        "recommendations": result.validation_report.recommendations
                    } if result.validation_report else None,
                    "enrichment_summary": result.enrichment_summary,
                    "template_compliance": result.template_compliance,
                    "recommendations": result.recommendations,
                    "dashboard_data": self.get_enhancement_dashboard_data(result)
                }
            }
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}") 