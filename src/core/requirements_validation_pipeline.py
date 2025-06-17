from typing import Dict, List, Any, Optional, Tuple, Set
import re
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from .arcadia_context_enricher import ARCADIAContextEnricher

class ValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"

class ValidationCategory(Enum):
    """Validation categories"""
    SYNTACTIC = "syntactic"
    SEMANTIC = "semantic"
    COVERAGE = "coverage"
    QUALITY = "quality"
    TRACEABILITY = "traceability"

@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    id: str
    category: ValidationCategory
    level: ValidationLevel
    title: str
    description: str
    requirement_id: Optional[str] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    confidence: float = 1.0

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    overall_score: float
    total_requirements: int
    issues: List[ValidationIssue] = field(default_factory=list)
    scores_by_category: Dict[str, float] = field(default_factory=dict)
    coverage_analysis: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    gaps_identified: List[str] = field(default_factory=list)

class RequirementsValidationPipeline:
    """
    Comprehensive validation pipeline for generated requirements:
    1. Syntactic Parsing: Format and completeness validation
    2. Semantic Validation: ARCADIA methodology compliance
    3. Coverage Analysis: Gap identification
    4. Quality Scoring: Priority-based correction recommendations
    """
    
    def __init__(self, arcadia_enricher: Optional[ARCADIAContextEnricher] = None):
        self.logger = logging.getLogger(__name__)
        self.arcadia_enricher = arcadia_enricher or ARCADIAContextEnricher()
        
        # Validation configuration
        self.validation_config = {
            "min_description_words": 15,
            "max_description_words": 200,
            "required_fields": ["id", "description", "priority", "verification_method"],
            "priority_values": ["MUST", "SHOULD", "COULD", "WON'T"],
            "phase_specific_checks": True,
            "traceability_threshold": 0.6,
            "quality_threshold": 0.7
        }
        
        # Validation patterns
        self.validation_patterns = {
            "requirement_statement": re.compile(r".*shall\s+([^.]+)", re.IGNORECASE),
            "measurable_criteria": re.compile(r"(\d+(?:\.\d+)?)\s*(seconds?|minutes?|hours?|%|percent|MB|GB|TB)", re.IGNORECASE),
            "actor_reference": re.compile(r"(user|operator|system|administrator|manager)", re.IGNORECASE),
            "capability_reference": re.compile(r"(capability|function|feature|service)", re.IGNORECASE)
        }

    def validate_requirements(self, 
                            requirements_data: Dict[str, Any], 
                            phase: str,
                            context: Optional[List[Dict[str, Any]]] = None) -> ValidationReport:
        """
        Run comprehensive validation pipeline on generated requirements
        """
        self.logger.info(f"Starting validation pipeline for {phase} phase requirements")
        
        # Initialize validation report
        report = ValidationReport(
            overall_score=0.0,
            total_requirements=0
        )
        
        # Extract all requirements
        all_requirements = self._extract_all_requirements(requirements_data)
        report.total_requirements = len(all_requirements)
        
        if not all_requirements:
            report.issues.append(ValidationIssue(
                id="VAL-001",
                category=ValidationCategory.SYNTACTIC,
                level=ValidationLevel.CRITICAL,
                title="No Requirements Found",
                description="No requirements were found in the provided data"
            ))
            return report
        
        # Step 1: Syntactic Parsing Validation
        syntactic_score = self._validate_syntactic_parsing(all_requirements, report)
        
        # Step 2: Semantic Validation (ARCADIA Compliance)
        semantic_score = self._validate_semantic_compliance(all_requirements, phase, report)
        
        # Step 3: Coverage Analysis
        coverage_score = self._analyze_coverage(all_requirements, phase, context, report)
        
        # Step 4: Quality Scoring
        quality_score = self._calculate_quality_scores(all_requirements, report)
        
        # Step 5: Traceability Validation
        traceability_score = self._validate_traceability(all_requirements, phase, report)
        
        # Calculate overall score
        report.overall_score = np.mean([
            syntactic_score, semantic_score, coverage_score, 
            quality_score, traceability_score
        ])
        
        # Store category scores
        report.scores_by_category = {
            "syntactic": syntactic_score,
            "semantic": semantic_score,
            "coverage": coverage_score,
            "quality": quality_score,
            "traceability": traceability_score
        }
        
        # Generate recommendations
        self._generate_recommendations(report)
        
        self.logger.info(f"Validation completed. Overall score: {report.overall_score:.2f}")
        
        return report

    def _extract_all_requirements(self, requirements_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all requirements from the data structure"""
        all_requirements = []
        
        for req_type, requirements in requirements_data.items():
            if req_type == "stakeholders":
                continue
                
            if isinstance(requirements, list):
                for req in requirements:
                    if isinstance(req, dict):
                        req["requirement_type"] = req_type
                        all_requirements.append(req)
            elif isinstance(requirements, dict):
                # Handle nested structure
                for phase, phase_reqs in requirements.items():
                    if isinstance(phase_reqs, list):
                        for req in phase_reqs:
                            if isinstance(req, dict):
                                req["requirement_type"] = req_type
                                req["phase"] = phase
                                all_requirements.append(req)
        
        return all_requirements

    def _validate_syntactic_parsing(self, requirements: List[Dict[str, Any]], report: ValidationReport) -> float:
        """Validate syntactic structure and completeness"""
        self.logger.info("Running syntactic parsing validation")
        
        syntactic_issues = []
        valid_count = 0
        
        for req in requirements:
            req_id = req.get("id", "UNKNOWN")
            
            # Check required fields
            missing_fields = []
            for field in self.validation_config["required_fields"]:
                if field not in req or not req[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                syntactic_issues.append(ValidationIssue(
                    id=f"SYN-{len(syntactic_issues)+1:03d}",
                    category=ValidationCategory.SYNTACTIC,
                    level=ValidationLevel.MAJOR,
                    title="Missing Required Fields",
                    description=f"Missing required fields: {', '.join(missing_fields)}",
                    requirement_id=req_id,
                    suggestion=f"Add missing fields: {', '.join(missing_fields)}",
                    auto_fixable=True
                ))
            
            # Validate priority value
            priority = req.get("priority", "")
            if priority not in self.validation_config["priority_values"]:
                syntactic_issues.append(ValidationIssue(
                    id=f"SYN-{len(syntactic_issues)+1:03d}",
                    category=ValidationCategory.SYNTACTIC,
                    level=ValidationLevel.MINOR,
                    title="Invalid Priority Value",
                    description=f"Priority '{priority}' is not valid. Expected: {', '.join(self.validation_config['priority_values'])}",
                    requirement_id=req_id,
                    suggestion="Use valid priority values: MUST, SHOULD, COULD, WON'T",
                    auto_fixable=True
                ))
            
            # Validate description length
            description = req.get("description", "")
            word_count = len(description.split())
            
            if word_count < self.validation_config["min_description_words"]:
                syntactic_issues.append(ValidationIssue(
                    id=f"SYN-{len(syntactic_issues)+1:03d}",
                    category=ValidationCategory.SYNTACTIC,
                    level=ValidationLevel.MAJOR,
                    title="Description Too Short",
                    description=f"Description has only {word_count} words (minimum: {self.validation_config['min_description_words']})",
                    requirement_id=req_id,
                    suggestion="Expand description with more specific details and context"
                ))
            elif word_count > self.validation_config["max_description_words"]:
                syntactic_issues.append(ValidationIssue(
                    id=f"SYN-{len(syntactic_issues)+1:03d}",
                    category=ValidationCategory.SYNTACTIC,
                    level=ValidationLevel.MINOR,
                    title="Description Too Long",
                    description=f"Description has {word_count} words (maximum: {self.validation_config['max_description_words']})",
                    requirement_id=req_id,
                    suggestion="Consider breaking down into multiple requirements"
                ))
            
            # Check for proper requirement statement
            if not self.validation_patterns["requirement_statement"].search(description):
                syntactic_issues.append(ValidationIssue(
                    id=f"SYN-{len(syntactic_issues)+1:03d}",
                    category=ValidationCategory.SYNTACTIC,
                    level=ValidationLevel.MAJOR,
                    title="Invalid Requirement Statement",
                    description="Requirement does not follow 'shall' statement pattern",
                    requirement_id=req_id,
                    suggestion="Rewrite using 'The system/actor shall...' format"
                ))
            else:
                valid_count += 1
        
        # Add issues to report
        report.issues.extend(syntactic_issues)
        
        # Calculate syntactic score
        syntactic_score = valid_count / len(requirements) if requirements else 0.0
        
        self.logger.info(f"Syntactic validation completed. Score: {syntactic_score:.2f}, Issues: {len(syntactic_issues)}")
        
        return syntactic_score

    def _validate_semantic_compliance(self, requirements: List[Dict[str, Any]], phase: str, report: ValidationReport) -> float:
        """Validate ARCADIA methodology compliance"""
        self.logger.info("Running semantic validation for ARCADIA compliance")
        
        semantic_issues = []
        compliant_count = 0
        
        # Get phase-specific validation criteria
        phase_templates = self.arcadia_enricher.phase_templates.get(phase, {})
        
        for req in requirements:
            req_id = req.get("id", "UNKNOWN")
            description = req.get("description", "").lower()
            req_type = req.get("requirement_type", "")
            
            # Check for phase-appropriate content
            if phase_templates:
                key_aspects = phase_templates.get("key_aspects", [])
                aspect_mentions = sum(1 for aspect in key_aspects if aspect.lower() in description)
                
                if aspect_mentions == 0:
                    semantic_issues.append(ValidationIssue(
                        id=f"SEM-{len(semantic_issues)+1:03d}",
                        category=ValidationCategory.SEMANTIC,
                        level=ValidationLevel.MAJOR,
                        title="Missing Phase-Specific Content",
                        description=f"Requirement lacks {phase} phase-specific aspects",
                        requirement_id=req_id,
                        suggestion=f"Include references to: {', '.join(key_aspects[:3])}"
                    ))
            
            # Check for measurable criteria (for NFRs)
            if req_type == "non_functional":
                if not self.validation_patterns["measurable_criteria"].search(description):
                    semantic_issues.append(ValidationIssue(
                        id=f"SEM-{len(semantic_issues)+1:03d}",
                        category=ValidationCategory.SEMANTIC,
                        level=ValidationLevel.MAJOR,
                        title="Non-Measurable NFR",
                        description="Non-functional requirement lacks measurable criteria",
                        requirement_id=req_id,
                        suggestion="Add specific metrics, thresholds, or quantifiable criteria"
                    ))
            
            # Check for actor references
            if not self.validation_patterns["actor_reference"].search(description):
                semantic_issues.append(ValidationIssue(
                    id=f"SEM-{len(semantic_issues)+1:03d}",
                    category=ValidationCategory.SEMANTIC,
                    level=ValidationLevel.MINOR,
                    title="Missing Actor Reference",
                    description="Requirement does not specify responsible actor",
                    requirement_id=req_id,
                    suggestion="Specify which actor (user, system, operator) is responsible"
                ))
            
            # Check verification method appropriateness
            verification = req.get("verification_method", "").lower()
            if verification in ["review and testing", "testing", "validation"]:
                semantic_issues.append(ValidationIssue(
                    id=f"SEM-{len(semantic_issues)+1:03d}",
                    category=ValidationCategory.SEMANTIC,
                    level=ValidationLevel.MINOR,
                    title="Generic Verification Method",
                    description="Verification method is too generic",
                    requirement_id=req_id,
                    suggestion="Use more specific verification methods appropriate to requirement type"
                ))
            else:
                compliant_count += 1
        
        # Add issues to report
        report.issues.extend(semantic_issues)
        
        # Calculate semantic score
        semantic_score = compliant_count / len(requirements) if requirements else 0.0
        
        self.logger.info(f"Semantic validation completed. Score: {semantic_score:.2f}, Issues: {len(semantic_issues)}")
        
        return semantic_score

    def _analyze_coverage(self, requirements: List[Dict[str, Any]], phase: str, context: Optional[List[Dict[str, Any]]], report: ValidationReport) -> float:
        """Analyze requirement coverage and identify gaps"""
        self.logger.info("Running coverage analysis")
        
        coverage_issues = []
        gaps_identified = []
        
        # Analyze operational capability coverage
        capabilities = self.arcadia_enricher.operational_capabilities
        relevant_capabilities = [cap for cap in capabilities.values() if cap.phase == phase]
        
        covered_capabilities = set()
        for req in requirements:
            description = req.get("description", "").lower()
            for cap in relevant_capabilities:
                if any(keyword.lower() in description for keyword in cap.functions):
                    covered_capabilities.add(cap.name)
        
        uncovered_capabilities = set(cap.name for cap in relevant_capabilities) - covered_capabilities
        
        if uncovered_capabilities:
            gaps_identified.extend([f"Uncovered capability: {cap}" for cap in uncovered_capabilities])
            coverage_issues.append(ValidationIssue(
                id=f"COV-{len(coverage_issues)+1:03d}",
                category=ValidationCategory.COVERAGE,
                level=ValidationLevel.MAJOR,
                title="Incomplete Capability Coverage",
                description=f"Missing requirements for capabilities: {', '.join(list(uncovered_capabilities)[:3])}{'...' if len(uncovered_capabilities) > 3 else ''}",
                suggestion="Add requirements to cover missing operational capabilities"
            ))
        
        # Analyze actor coverage
        actors = self.arcadia_enricher.actors
        relevant_actors = [actor for actor in actors.values() if phase in actor.phase_involvement]
        
        covered_actors = set()
        for req in requirements:
            description = req.get("description", "").lower()
            for actor in relevant_actors:
                if actor.name.lower() in description:
                    covered_actors.add(actor.name)
        
        uncovered_actors = set(actor.name for actor in relevant_actors) - covered_actors
        
        if uncovered_actors:
            gaps_identified.extend([f"Uncovered actor: {actor}" for actor in uncovered_actors])
            coverage_issues.append(ValidationIssue(
                id=f"COV-{len(coverage_issues)+1:03d}",
                category=ValidationCategory.COVERAGE,
                level=ValidationLevel.MINOR,
                title="Incomplete Actor Coverage",
                description=f"Missing actor references: {', '.join(list(uncovered_actors)[:3])}",
                suggestion="Consider adding requirements that involve missing actors"
            ))
        
        # Analyze requirement type balance
        req_types = {}
        for req in requirements:
            req_type = req.get("requirement_type", "unknown")
            req_types[req_type] = req_types.get(req_type, 0) + 1
        
        total_reqs = len(requirements)
        if total_reqs > 0:
            functional_ratio = req_types.get("functional", 0) / total_reqs
            nfr_ratio = req_types.get("non_functional", 0) / total_reqs
            
            if functional_ratio < 0.3:
                coverage_issues.append(ValidationIssue(
                    id=f"COV-{len(coverage_issues)+1:03d}",
                    category=ValidationCategory.COVERAGE,
                    level=ValidationLevel.MINOR,
                    title="Low Functional Requirements Ratio",
                    description=f"Only {functional_ratio:.1%} functional requirements (recommended: >30%)",
                    suggestion="Consider adding more functional requirements"
                ))
            
            if nfr_ratio > 0.6:
                coverage_issues.append(ValidationIssue(
                    id=f"COV-{len(coverage_issues)+1:03d}",
                    category=ValidationCategory.COVERAGE,
                    level=ValidationLevel.MINOR,
                    title="High NFR Ratio",
                    description=f"NFR ratio is {nfr_ratio:.1%} (recommended: <60%)",
                    suggestion="Balance with more functional requirements"
                ))
        
        # Store coverage analysis
        report.coverage_analysis = {
            "capability_coverage": len(covered_capabilities) / len(relevant_capabilities) if relevant_capabilities else 1.0,
            "actor_coverage": len(covered_actors) / len(relevant_actors) if relevant_actors else 1.0,
            "requirement_type_distribution": req_types,
            "covered_capabilities": list(covered_capabilities),
            "uncovered_capabilities": list(uncovered_capabilities),
            "covered_actors": list(covered_actors),
            "uncovered_actors": list(uncovered_actors)
        }
        
        report.gaps_identified = gaps_identified
        report.issues.extend(coverage_issues)
        
        # Calculate coverage score
        coverage_score = np.mean([
            report.coverage_analysis["capability_coverage"],
            report.coverage_analysis["actor_coverage"]
        ])
        
        self.logger.info(f"Coverage analysis completed. Score: {coverage_score:.2f}, Gaps: {len(gaps_identified)}")
        
        return coverage_score

    def _calculate_quality_scores(self, requirements: List[Dict[str, Any]], report: ValidationReport) -> float:
        """Calculate detailed quality scores for requirements"""
        self.logger.info("Calculating quality scores")
        
        quality_issues = []
        quality_scores = []
        
        for req in requirements:
            req_id = req.get("id", "UNKNOWN")
            description = req.get("description", "")
            
            # Calculate individual quality metrics
            clarity_score = self._calculate_clarity_score(description)
            completeness_score = self._calculate_completeness_score(req)
            consistency_score = self._calculate_consistency_score(req)
            
            req_quality_score = np.mean([clarity_score, completeness_score, consistency_score])
            quality_scores.append(req_quality_score)
            
            # Generate quality issues for low-scoring requirements
            if req_quality_score < self.validation_config["quality_threshold"]:
                quality_issues.append(ValidationIssue(
                    id=f"QUA-{len(quality_issues)+1:03d}",
                    category=ValidationCategory.QUALITY,
                    level=ValidationLevel.MAJOR if req_quality_score < 0.5 else ValidationLevel.MINOR,
                    title="Low Quality Score",
                    description=f"Requirement quality score: {req_quality_score:.2f} (threshold: {self.validation_config['quality_threshold']})",
                    requirement_id=req_id,
                    suggestion="Improve clarity, completeness, and consistency"
                ))
        
        # Store quality metrics
        report.quality_metrics = {
            "average_quality": np.mean(quality_scores) if quality_scores else 0.0,
            "clarity_average": np.mean([self._calculate_clarity_score(req.get("description", "")) for req in requirements]),
            "completeness_average": np.mean([self._calculate_completeness_score(req) for req in requirements]),
            "consistency_average": np.mean([self._calculate_consistency_score(req) for req in requirements]),
            "quality_distribution": {
                "high": len([s for s in quality_scores if s >= 0.8]),
                "medium": len([s for s in quality_scores if 0.6 <= s < 0.8]),
                "low": len([s for s in quality_scores if s < 0.6])
            }
        }
        
        report.issues.extend(quality_issues)
        
        overall_quality_score = report.quality_metrics["average_quality"]
        
        self.logger.info(f"Quality scoring completed. Average score: {overall_quality_score:.2f}")
        
        return overall_quality_score

    def _validate_traceability(self, requirements: List[Dict[str, Any]], phase: str, report: ValidationReport) -> float:
        """Validate requirement traceability"""
        self.logger.info("Validating traceability")
        
        traceability_issues = []
        traceability_scores = []
        
        for req in requirements:
            req_id = req.get("id", "UNKNOWN")
            
            # Use ARCADIA enricher to validate traceability
            traceability_result = self.arcadia_enricher.validate_requirement_traceability(req, phase)
            traceability_scores.append(traceability_result["traceability_score"])
            
            if not traceability_result["is_valid"]:
                for issue in traceability_result["issues"]:
                    traceability_issues.append(ValidationIssue(
                        id=f"TRA-{len(traceability_issues)+1:03d}",
                        category=ValidationCategory.TRACEABILITY,
                        level=ValidationLevel.MAJOR,
                        title="Traceability Issue",
                        description=issue,
                        requirement_id=req_id,
                        suggestion="; ".join(traceability_result["suggestions"])
                    ))
        
        report.issues.extend(traceability_issues)
        
        traceability_score = np.mean(traceability_scores) if traceability_scores else 0.0
        
        self.logger.info(f"Traceability validation completed. Score: {traceability_score:.2f}")
        
        return traceability_score

    def _calculate_clarity_score(self, description: str) -> float:
        """Calculate clarity score for requirement description"""
        if not description:
            return 0.0
        
        score = 0.0
        
        # Check for clear action verbs
        action_verbs = ["shall", "must", "will", "should", "provide", "support", "enable"]
        if any(verb in description.lower() for verb in action_verbs):
            score += 0.3
        
        # Check for specific terms (not vague)
        vague_terms = ["appropriate", "suitable", "adequate", "reasonable", "good", "bad"]
        if not any(term in description.lower() for term in vague_terms):
            score += 0.2
        
        # Check sentence structure
        if len(description.split('.')) <= 3:  # Not overly complex
            score += 0.2
        
        # Check for specific details
        if any(pattern.search(description) for pattern in self.validation_patterns.values()):
            score += 0.3
        
        return min(1.0, score)

    def _calculate_completeness_score(self, requirement: Dict[str, Any]) -> float:
        """Calculate completeness score for requirement"""
        score = 0.0
        
        # Check required fields presence
        required_fields = self.validation_config["required_fields"]
        present_fields = sum(1 for field in required_fields if requirement.get(field))
        score += (present_fields / len(required_fields)) * 0.4
        
        # Check description quality
        description = requirement.get("description", "")
        word_count = len(description.split())
        if word_count >= self.validation_config["min_description_words"]:
            score += 0.3
        
        # Check for verification method specificity
        verification = requirement.get("verification_method", "")
        if verification and len(verification) > 20:  # Not generic
            score += 0.3
        
        return min(1.0, score)

    def _calculate_consistency_score(self, requirement: Dict[str, Any]) -> float:
        """Calculate consistency score for requirement"""
        score = 0.8  # Base score
        
        # Check ID format consistency
        req_id = requirement.get("id", "")
        if not re.match(r"^[A-Z]{2,3}-\d{3}$", req_id):
            score -= 0.2
        
        # Check priority consistency
        priority = requirement.get("priority", "")
        if priority not in self.validation_config["priority_values"]:
            score -= 0.3
        
        # Check description format consistency
        description = requirement.get("description", "")
        if not description.startswith("The ") and not description.startswith("System "):
            score -= 0.1
        
        return max(0.0, score)

    def _generate_recommendations(self, report: ValidationReport):
        """Generate prioritized recommendations based on validation results"""
        recommendations = []
        
        # Critical issues first
        critical_issues = [issue for issue in report.issues if issue.level == ValidationLevel.CRITICAL]
        if critical_issues:
            recommendations.append(f"🚨 Address {len(critical_issues)} critical issues immediately")
        
        # Major issues
        major_issues = [issue for issue in report.issues if issue.level == ValidationLevel.MAJOR]
        if major_issues:
            recommendations.append(f"⚠️ Resolve {len(major_issues)} major issues to improve quality")
        
        # Coverage gaps
        if report.gaps_identified:
            recommendations.append(f"📊 Fill {len(report.gaps_identified)} coverage gaps identified")
        
        # Quality improvements
        if report.quality_metrics.get("average_quality", 0) < 0.7:
            recommendations.append("📈 Improve overall requirement quality (clarity, completeness, consistency)")
        
        # Auto-fixable issues
        auto_fixable = [issue for issue in report.issues if issue.auto_fixable]
        if auto_fixable:
            recommendations.append(f"🔧 {len(auto_fixable)} issues can be automatically fixed")
        
        # Category-specific recommendations
        for category, score in report.scores_by_category.items():
            if score < 0.6:
                recommendations.append(f"🎯 Focus on improving {category} validation (score: {score:.2f})")
        
        report.recommendations = recommendations

    def get_validation_summary(self, report: ValidationReport) -> Dict[str, Any]:
        """Get a summary of validation results"""
        return {
            "overall_score": report.overall_score,
            "grade": self._get_grade(report.overall_score),
            "total_requirements": report.total_requirements,
            "total_issues": len(report.issues),
            "issues_by_level": {
                level.value: len([issue for issue in report.issues if issue.level == level])
                for level in ValidationLevel
            },
            "issues_by_category": {
                category.value: len([issue for issue in report.issues if issue.category == category])
                for category in ValidationCategory
            },
            "category_scores": report.scores_by_category,
            "quality_metrics": report.quality_metrics,
            "coverage_analysis": report.coverage_analysis,
            "top_recommendations": report.recommendations[:5],
            "gaps_count": len(report.gaps_identified),
            "auto_fixable_count": len([issue for issue in report.issues if issue.auto_fixable])
        }

    def _get_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
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

    def export_validation_report(self, report: ValidationReport, format: str = "json") -> str:
        """Export validation report in specified format"""
        if format.lower() == "json":
            return json.dumps({
                "validation_report": {
                    "overall_score": report.overall_score,
                    "total_requirements": report.total_requirements,
                    "scores_by_category": report.scores_by_category,
                    "quality_metrics": report.quality_metrics,
                    "coverage_analysis": report.coverage_analysis,
                    "issues": [
                        {
                            "id": issue.id,
                            "category": issue.category.value,
                            "level": issue.level.value,
                            "title": issue.title,
                            "description": issue.description,
                            "requirement_id": issue.requirement_id,
                            "suggestion": issue.suggestion,
                            "auto_fixable": issue.auto_fixable
                        }
                        for issue in report.issues
                    ],
                    "recommendations": report.recommendations,
                    "gaps_identified": report.gaps_identified
                }
            }, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}") 