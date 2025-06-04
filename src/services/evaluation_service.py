"""
Evaluation Service for SAFE MBSE RAG System

This service provides comprehensive evaluation capabilities for generated requirements,
including quality assessment, ARCADIA compliance, and CYDERCO compatibility analysis.
"""

from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum
import re


class QualityMetric(Enum):
    """Quality metrics for requirements evaluation."""
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    TRACEABILITY = "traceability"
    TESTABILITY = "testability"
    CLARITY = "clarity"


@dataclass
class QualityAssessment:
    """Structure for quality assessment results."""
    completeness: float
    consistency: float
    traceability: float
    testability: float
    clarity: float
    overall_score: float
    recommendations: List[str]


@dataclass
class RequirementQuality:
    """Quality metrics for individual requirement."""
    requirement_id: str
    clarity_score: float
    completeness_score: float
    testability_score: float
    consistency_score: float
    issues: List[str]


class EvaluationService:
    """Service for evaluating generated requirements quality and compliance."""
    
    def __init__(self):
        """Initialize the evaluation service."""
        self.quality_thresholds = {
            QualityMetric.COMPLETENESS: 0.8,
            QualityMetric.CONSISTENCY: 0.85,
            QualityMetric.TRACEABILITY: 0.75,
            QualityMetric.TESTABILITY: 0.7,
            QualityMetric.CLARITY: 0.8
        }
        
        # Patterns for quality assessment
        self.clarity_patterns = {
            'vague_terms': [r'\b(maybe|possibly|might|could|should probably)\b', 
                           r'\b(appropriate|adequate|reasonable|suitable)\b'],
            'ambiguous': [r'\b(etc|and so on|among others)\b', 
                         r'\b(as needed|when necessary|if required)\b'],
            'subjective': [r'\b(user-friendly|easy|fast|slow|good|bad)\b']
        }
        
        self.testability_keywords = [
            'shall', 'must', 'will', 'verify', 'test', 'measure', 
            'validate', 'demonstrate', 'confirm', 'ensure'
        ]
    
    def assess_requirement_quality(self, requirements_data: Dict[str, Any]) -> QualityAssessment:
        """
        Assess the overall quality of generated requirements.
        
        Args:
            requirements_data: Dictionary containing generated requirements
            
        Returns:
            QualityAssessment with comprehensive quality metrics
        """
        all_requirements = self._extract_all_requirements(requirements_data)
        
        if not all_requirements:
            return QualityAssessment(
                completeness=0.0, consistency=0.0, traceability=0.0,
                testability=0.0, clarity=0.0, overall_score=0.0,
                recommendations=["No requirements found for assessment"]
            )
        
        # Assess individual metrics
        completeness = self._assess_completeness(requirements_data)
        consistency = self._assess_consistency(all_requirements)
        traceability = self._assess_traceability(requirements_data)
        testability = self._assess_testability(all_requirements)
        clarity = self._assess_clarity(all_requirements)
        
        # Calculate overall score
        overall_score = np.mean([completeness, consistency, traceability, testability, clarity])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            completeness, consistency, traceability, testability, clarity
        )
        
        return QualityAssessment(
            completeness=completeness,
            consistency=consistency,
            traceability=traceability,
            testability=testability,
            clarity=clarity,
            overall_score=overall_score,
            recommendations=recommendations
        )
    
    def evaluate_requirement_quality(self, requirement: Dict[str, Any]) -> RequirementQuality:
        """
        Evaluate quality of a single requirement.
        
        Args:
            requirement: Single requirement dictionary
            
        Returns:
            RequirementQuality with detailed metrics
        """
        req_id = requirement.get('id', 'Unknown')
        description = requirement.get('description', '')
        
        clarity_score = self._assess_requirement_clarity(description)
        completeness_score = self._assess_requirement_completeness(requirement)
        testability_score = self._assess_requirement_testability(description)
        consistency_score = self._assess_requirement_consistency(requirement)
        
        issues = self._identify_requirement_issues(requirement)
        
        return RequirementQuality(
            requirement_id=req_id,
            clarity_score=clarity_score,
            completeness_score=completeness_score,
            testability_score=testability_score,
            consistency_score=consistency_score,
            issues=issues
        )
    
    def _extract_all_requirements(self, requirements_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all requirements from the data structure."""
        all_reqs = []
        
        requirements = requirements_data.get('requirements', {})
        for phase, phase_reqs in requirements.items():
            for req_type, reqs_list in phase_reqs.items():
                if isinstance(reqs_list, list):
                    all_reqs.extend(reqs_list)
        
        return all_reqs
    
    def _assess_completeness(self, requirements_data: Dict[str, Any]) -> float:
        """Assess completeness of requirements coverage."""
        required_fields = ['id', 'title', 'description', 'priority', 'verification_method']
        all_reqs = self._extract_all_requirements(requirements_data)
        
        if not all_reqs:
            return 0.0
        
        completeness_scores = []
        for req in all_reqs:
            present_fields = sum(1 for field in required_fields if req.get(field))
            completeness_scores.append(present_fields / len(required_fields))
        
        return np.mean(completeness_scores)
    
    def _assess_consistency(self, requirements: List[Dict[str, Any]]) -> float:
        """Assess consistency across requirements."""
        if not requirements:
            return 0.0
        
        # Check ID format consistency
        id_formats = [req.get('id', '').split('-')[0] for req in requirements if req.get('id')]
        id_consistency = len(set(id_formats)) <= 2 if id_formats else 0.5
        
        # Check priority format consistency
        priorities = [req.get('priority') for req in requirements if req.get('priority')]
        valid_priorities = {'MUST', 'SHOULD', 'COULD', 'WONT'}
        priority_consistency = all(p in valid_priorities for p in priorities) if priorities else 0.5
        
        # Check description format consistency
        desc_lengths = [len(req.get('description', '')) for req in requirements]
        desc_consistency = (np.std(desc_lengths) / np.mean(desc_lengths)) < 0.5 if desc_lengths else 0.5
        
        return np.mean([id_consistency, priority_consistency, desc_consistency])
    
    def _assess_traceability(self, requirements_data: Dict[str, Any]) -> float:
        """Assess traceability of requirements to ARCADIA phases."""
        requirements = requirements_data.get('requirements', {})
        
        # Check if requirements are properly mapped to ARCADIA phases
        arcadia_phases = ['operational_analysis', 'system_analysis', 'logical_architecture', 
                         'physical_architecture', 'epbs_architecture']
        
        covered_phases = [phase for phase in arcadia_phases if phase in requirements]
        phase_coverage = len(covered_phases) / len(arcadia_phases)
        
        # Check stakeholder traceability
        stakeholders = requirements_data.get('stakeholders', {})
        stakeholder_coverage = min(len(stakeholders) / 5, 1.0)  # Expect at least 5 stakeholders
        
        return np.mean([phase_coverage, stakeholder_coverage])
    
    def _assess_testability(self, requirements: List[Dict[str, Any]]) -> float:
        """Assess testability of requirements."""
        if not requirements:
            return 0.0
        
        testability_scores = []
        for req in requirements:
            description = req.get('description', '').lower()
            verification = req.get('verification_method', '').lower()
            
            # Check for testable language
            testable_keywords = sum(1 for keyword in self.testability_keywords 
                                  if keyword in description or keyword in verification)
            
            # Check for verification method
            has_verification = bool(verification and verification != 'n/a')
            
            # Check for measurable criteria
            has_metrics = bool(re.search(r'\d+|\b(percent|%|seconds?|minutes?|hours?)\b', description))
            
            score = (min(testable_keywords / 3, 1.0) + has_verification + has_metrics) / 3
            testability_scores.append(score)
        
        return np.mean(testability_scores)
    
    def _assess_clarity(self, requirements: List[Dict[str, Any]]) -> float:
        """Assess clarity of requirements descriptions."""
        if not requirements:
            return 0.0
        
        clarity_scores = []
        for req in requirements:
            clarity_scores.append(self._assess_requirement_clarity(req.get('description', '')))
        
        return np.mean(clarity_scores)
    
    def _assess_requirement_clarity(self, description: str) -> float:
        """Assess clarity of a single requirement description."""
        if not description:
            return 0.0
        
        description_lower = description.lower()
        issues = 0
        
        # Check for vague terms
        for pattern_list in self.clarity_patterns.values():
            for pattern in pattern_list:
                if re.search(pattern, description_lower):
                    issues += 1
        
        # Check length (too short or too long)
        if len(description) < 20 or len(description) > 500:
            issues += 1
        
        # Check for proper sentence structure
        if not description.strip().endswith('.'):
            issues += 0.5
        
        # Calculate clarity score (fewer issues = higher clarity)
        max_issues = 5
        clarity_score = max(0, 1 - (issues / max_issues))
        
        return clarity_score
    
    def _assess_requirement_completeness(self, requirement: Dict[str, Any]) -> float:
        """Assess completeness of a single requirement."""
        required_fields = ['id', 'title', 'description', 'priority']
        present_fields = sum(1 for field in required_fields if requirement.get(field))
        return present_fields / len(required_fields)
    
    def _assess_requirement_testability(self, description: str) -> float:
        """Assess testability of a single requirement description."""
        if not description:
            return 0.0
        
        description_lower = description.lower()
        testable_keywords = sum(1 for keyword in self.testability_keywords 
                              if keyword in description_lower)
        
        has_metrics = bool(re.search(r'\d+|\b(percent|%|seconds?|minutes?|hours?)\b', description_lower))
        
        return min((testable_keywords / 3 + has_metrics) / 2, 1.0)
    
    def _assess_requirement_consistency(self, requirement: Dict[str, Any]) -> float:
        """Assess consistency of a single requirement."""
        # Simple consistency checks
        has_valid_priority = requirement.get('priority') in {'MUST', 'SHOULD', 'COULD', 'WONT'}
        has_proper_id = bool(requirement.get('id') and '-' in requirement.get('id', ''))
        
        return (has_valid_priority + has_proper_id) / 2
    
    def _identify_requirement_issues(self, requirement: Dict[str, Any]) -> List[str]:
        """Identify specific issues with a requirement."""
        issues = []
        
        if not requirement.get('description'):
            issues.append("Missing description")
        
        if not requirement.get('id'):
            issues.append("Missing requirement ID")
        
        if requirement.get('priority') not in {'MUST', 'SHOULD', 'COULD', 'WONT'}:
            issues.append("Invalid priority level")
        
        description = requirement.get('description', '')
        if len(description) < 20:
            issues.append("Description too short")
        elif len(description) > 500:
            issues.append("Description too long")
        
        # Check for vague language
        description_lower = description.lower()
        for pattern_list in self.clarity_patterns.values():
            for pattern in pattern_list:
                if re.search(pattern, description_lower):
                    issues.append("Contains vague or ambiguous language")
                    break
        
        return issues
    
    def _generate_recommendations(self, completeness: float, consistency: float, 
                                traceability: float, testability: float, clarity: float) -> List[str]:
        """Generate improvement recommendations based on quality metrics."""
        recommendations = []
        
        if completeness < self.quality_thresholds[QualityMetric.COMPLETENESS]:
            recommendations.append("Improve requirement completeness by ensuring all required fields are present")
        
        if consistency < self.quality_thresholds[QualityMetric.CONSISTENCY]:
            recommendations.append("Enhance consistency by standardizing ID formats and priority levels")
        
        if traceability < self.quality_thresholds[QualityMetric.TRACEABILITY]:
            recommendations.append("Improve traceability by ensuring requirements map to ARCADIA phases")
        
        if testability < self.quality_thresholds[QualityMetric.TESTABILITY]:
            recommendations.append("Enhance testability by adding measurable criteria and verification methods")
        
        if clarity < self.quality_thresholds[QualityMetric.CLARITY]:
            recommendations.append("Improve clarity by avoiding vague language and ensuring proper structure")
        
        if not recommendations:
            recommendations.append("Requirements meet quality standards - continue maintaining best practices")
        
        return recommendations
