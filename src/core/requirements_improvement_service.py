from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from .enhanced_requirements_generator import EnhancedRequirementsGenerator
from .requirements_generator import RequirementsGenerator
import numpy as np

@dataclass
class ImprovementMetrics:
    """Metrics to track improvements in requirements generation"""
    priority_distribution: Dict[str, float]
    nfr_category_balance: Dict[str, int]
    description_completeness: float
    verification_specificity: float
    traceability_coverage: float
    overall_quality_score: float

@dataclass
class RequirementsQualityReport:
    """Comprehensive quality report for requirements"""
    total_requirements: int
    functional_count: int
    non_functional_count: int
    priority_balance_score: float
    description_quality_score: float
    verification_quality_score: float
    traceability_score: float
    improvement_recommendations: List[str]

class RequirementsImprovementService:
    """
    Service to manage and evaluate requirements generation improvements.
    Addresses the identified issues:
    1. Priority imbalance (target: 30% MUST, 50% SHOULD, 20% COULD)
    2. NFR overrepresentation (balanced based on context)
    3. Incomplete descriptions (minimum quality standards)
    4. Generic verification methods (context-specific methods)
    5. Enhanced traceability to operational capabilities
    """
    
    def __init__(self, ollama_client):
        self.logger = logging.getLogger(__name__)
        self.enhanced_generator = EnhancedRequirementsGenerator(ollama_client)
        self.standard_generator = RequirementsGenerator(ollama_client)
        
        # Quality thresholds for evaluation
        self.quality_thresholds = {
            "priority_balance": 0.85,  # How close to target distribution
            "description_completeness": 0.80,  # Minimum description quality
            "verification_specificity": 0.75,  # Non-generic verification methods
            "traceability_coverage": 0.70,  # Links to operational context
            "nfr_balance": 0.80  # Balanced NFR categories
        }
        
        # Target priority distribution
        self.target_priority_distribution = {
            "MUST": 0.30,
            "SHOULD": 0.50,
            "COULD": 0.20
        }

    def generate_improved_requirements(self, 
                                     context: List[Dict[str, Any]], 
                                     phase: str, 
                                     proposal_text: str,
                                     requirement_types: List[str]) -> Dict[str, Any]:
        """
        Generate requirements using the enhanced generator with all improvements
        """
        self.logger.info(f"Generating improved requirements for {phase} phase")
        
        # Generate enhanced requirements
        enhanced_results = self.enhanced_generator.generate_balanced_requirements(
            context, phase, proposal_text, requirement_types
        )
        
        # Add quality metrics
        quality_report = self._evaluate_requirements_quality(enhanced_results)
        
        # Package results
        results = {
            "requirements": {phase: enhanced_results},
            "quality_report": quality_report,
            "improvements_applied": [
                "Balanced priority distribution (30/50/20 target)",
                "Context-aware NFR category selection",
                "Enhanced requirement descriptions with operational context",
                "Specific verification methods by type and phase",
                "Operational capability and scenario traceability"
            ],
            "metadata": {
                "generator_type": "enhanced",
                "phase": phase,
                "requirement_types": requirement_types,
                "quality_score": quality_report.verification_quality_score
            }
        }
        
        return results

    def compare_generation_approaches(self, 
                                    context: List[Dict[str, Any]], 
                                    phase: str, 
                                    proposal_text: str,
                                    requirement_types: List[str]) -> Dict[str, Any]:
        """
        Compare standard vs enhanced requirements generation
        """
        self.logger.info("Comparing standard vs enhanced requirements generation")
        
        # Generate with both approaches
        standard_results = self._generate_standard_requirements(
            context, phase, proposal_text, requirement_types
        )
        
        enhanced_results = self.enhanced_generator.generate_balanced_requirements(
            context, phase, proposal_text, requirement_types
        )
        
        # Evaluate both approaches
        standard_metrics = self._calculate_improvement_metrics(standard_results)
        enhanced_metrics = self._calculate_improvement_metrics(enhanced_results)
        
        # Calculate improvements
        improvements = self._calculate_improvements(standard_metrics, enhanced_metrics)
        
        return {
            "standard_approach": {
                "results": standard_results,
                "metrics": standard_metrics
            },
            "enhanced_approach": {
                "results": enhanced_results,
                "metrics": enhanced_metrics
            },
            "improvements": improvements,
            "summary": self._generate_improvement_summary(improvements)
        }

    def _generate_standard_requirements(self, 
                                      context: List[Dict[str, Any]], 
                                      phase: str, 
                                      proposal_text: str,
                                      requirement_types: List[str]) -> Dict[str, Any]:
        """Generate requirements using standard approach for comparison"""
        
        results = {}
        
        if "stakeholder" in requirement_types:
            results["stakeholders"] = self.standard_generator.generate_stakeholders(context, proposal_text)
        
        if "functional" in requirement_types:
            results["functional"] = self.standard_generator.generate_functional_requirements(
                context, phase, proposal_text
            )
        
        if "non_functional" in requirement_types:
            results["non_functional"] = self.standard_generator.generate_non_functional_requirements(
                context, phase, proposal_text
            )
        
        return results

    def _evaluate_requirements_quality(self, requirements_data: Dict[str, Any]) -> RequirementsQualityReport:
        """Evaluate the quality of generated requirements"""
        
        # Extract all requirements
        all_requirements = []
        functional_count = 0
        non_functional_count = 0
        
        for req_type, reqs in requirements_data.items():
            if req_type != "stakeholders" and isinstance(reqs, list):
                all_requirements.extend(reqs)
                if req_type == "functional":
                    functional_count = len(reqs)
                elif req_type == "non_functional":
                    non_functional_count = len(reqs)
        
        if not all_requirements:
            return RequirementsQualityReport(
                total_requirements=0,
                functional_count=0,
                non_functional_count=0,
                priority_balance_score=0.0,
                description_quality_score=0.0,
                verification_quality_score=0.0,
                traceability_score=0.0,
                improvement_recommendations=["No requirements generated"]
            )
        
        # Calculate quality scores
        priority_balance_score = self._calculate_priority_balance_score(all_requirements)
        description_quality_score = self._calculate_description_quality_score(all_requirements)
        verification_quality_score = self._calculate_verification_quality_score(all_requirements)
        traceability_score = self._calculate_traceability_score(all_requirements)
        
        # Generate improvement recommendations
        recommendations = self._generate_quality_recommendations(
            priority_balance_score, description_quality_score, 
            verification_quality_score, traceability_score
        )
        
        return RequirementsQualityReport(
            total_requirements=len(all_requirements),
            functional_count=functional_count,
            non_functional_count=non_functional_count,
            priority_balance_score=priority_balance_score,
            description_quality_score=description_quality_score,
            verification_quality_score=verification_quality_score,
            traceability_score=traceability_score,
            improvement_recommendations=recommendations
        )

    def _calculate_improvement_metrics(self, requirements_data: Dict[str, Any]) -> ImprovementMetrics:
        """Calculate detailed improvement metrics"""
        
        # Extract all requirements
        all_requirements = []
        for req_type, reqs in requirements_data.items():
            if req_type != "stakeholders" and isinstance(reqs, list):
                all_requirements.extend(reqs)
        
        if not all_requirements:
            return ImprovementMetrics(
                priority_distribution={},
                nfr_category_balance={},
                description_completeness=0.0,
                verification_specificity=0.0,
                traceability_coverage=0.0,
                overall_quality_score=0.0
            )
        
        # Calculate priority distribution
        priority_dist = self._calculate_priority_distribution(all_requirements)
        
        # Calculate NFR category balance
        nfr_balance = self._calculate_nfr_category_balance(requirements_data.get("non_functional", []))
        
        # Calculate description completeness
        description_completeness = self._calculate_description_completeness(all_requirements)
        
        # Calculate verification specificity
        verification_specificity = self._calculate_verification_specificity(all_requirements)
        
        # Calculate traceability coverage
        traceability_coverage = self._calculate_traceability_coverage(all_requirements)
        
        # Overall quality score
        overall_quality = np.mean([
            self._score_priority_balance(priority_dist),
            description_completeness,
            verification_specificity,
            traceability_coverage
        ])
        
        return ImprovementMetrics(
            priority_distribution=priority_dist,
            nfr_category_balance=nfr_balance,
            description_completeness=description_completeness,
            verification_specificity=verification_specificity,
            traceability_coverage=traceability_coverage,
            overall_quality_score=overall_quality
        )

    def _calculate_priority_distribution(self, requirements: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate actual priority distribution"""
        total = len(requirements)
        if total == 0:
            return {"MUST": 0.0, "SHOULD": 0.0, "COULD": 0.0}
        
        counts = {"MUST": 0, "SHOULD": 0, "COULD": 0}
        for req in requirements:
            priority = req.get("priority", "SHOULD")
            counts[priority] = counts.get(priority, 0) + 1
        
        return {k: v / total for k, v in counts.items()}

    def _calculate_priority_balance_score(self, requirements: List[Dict[str, Any]]) -> float:
        """Calculate how well priority distribution matches target"""
        actual_dist = self._calculate_priority_distribution(requirements)
        
        # Calculate deviation from target
        total_deviation = 0.0
        for priority, target in self.target_priority_distribution.items():
            actual = actual_dist.get(priority, 0.0)
            total_deviation += abs(actual - target)
        
        # Convert to score (lower deviation = higher score)
        balance_score = max(0.0, 1.0 - (total_deviation / 2.0))
        return balance_score

    def _calculate_nfr_category_balance(self, nfr_requirements: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of NFR categories"""
        category_counts = {}
        for req in nfr_requirements:
            category = req.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts

    def _calculate_description_completeness(self, requirements: List[Dict[str, Any]]) -> float:
        """Calculate description quality score"""
        if not requirements:
            return 0.0
        
        scores = []
        for req in requirements:
            description = req.get("description", "")
            
            # Check length
            word_count = len(description.split())
            length_score = min(1.0, word_count / 20.0)  # Target: 20+ words
            
            # Check for operational context
            context_indicators = ["operational", "capability", "scenario", "stakeholder"]
            context_score = sum(1 for indicator in context_indicators if indicator in description.lower()) / len(context_indicators)
            
            # Check for specificity
            specific_indicators = ["shall", "must", "specific", "measurable"]
            specific_score = min(1.0, sum(1 for indicator in specific_indicators if indicator in description.lower()) / 2.0)
            
            req_score = np.mean([length_score, context_score, specific_score])
            scores.append(req_score)
        
        return np.mean(scores)

    def _calculate_description_quality_score(self, requirements: List[Dict[str, Any]]) -> float:
        """Calculate description quality score (alias for completeness)"""
        return self._calculate_description_completeness(requirements)

    def _calculate_verification_specificity(self, requirements: List[Dict[str, Any]]) -> float:
        """Calculate verification method specificity score"""
        if not requirements:
            return 0.0
        
        generic_methods = ["review and testing", "testing", "review", "validation"]
        
        specific_count = 0
        for req in requirements:
            verification = req.get("verification_method", "").lower()
            if verification and not any(generic in verification for generic in generic_methods):
                specific_count += 1
        
        return specific_count / len(requirements)

    def _calculate_verification_quality_score(self, requirements: List[Dict[str, Any]]) -> float:
        """Calculate verification quality score (alias for specificity)"""
        return self._calculate_verification_specificity(requirements)

    def _calculate_traceability_coverage(self, requirements: List[Dict[str, Any]]) -> float:
        """Calculate traceability coverage score"""
        if not requirements:
            return 0.0
        
        traceability_fields = [
            "operational_capability_links",
            "operational_scenario_links", 
            "stakeholder_traceability",
            "operational_capability_link"
        ]
        
        traced_count = 0
        for req in requirements:
            has_traceability = any(
                req.get(field) and len(req.get(field, [])) > 0 if isinstance(req.get(field), list)
                else req.get(field) and len(str(req.get(field))) > 10
                for field in traceability_fields
            )
            if has_traceability:
                traced_count += 1
        
        return traced_count / len(requirements)

    def _calculate_traceability_score(self, requirements: List[Dict[str, Any]]) -> float:
        """Calculate traceability score (alias for coverage)"""
        return self._calculate_traceability_coverage(requirements)

    def _score_priority_balance(self, priority_dist: Dict[str, float]) -> float:
        """Score priority balance against target"""
        total_deviation = 0.0
        for priority, target in self.target_priority_distribution.items():
            actual = priority_dist.get(priority, 0.0)
            total_deviation += abs(actual - target)
        
        return max(0.0, 1.0 - (total_deviation / 2.0))

    def _calculate_improvements(self, 
                              standard_metrics: ImprovementMetrics,
                              enhanced_metrics: ImprovementMetrics) -> Dict[str, Any]:
        """Calculate improvements between standard and enhanced approaches"""
        
        return {
            "priority_balance_improvement": enhanced_metrics.overall_quality_score - standard_metrics.overall_quality_score,
            "description_completeness_improvement": enhanced_metrics.description_completeness - standard_metrics.description_completeness,
            "verification_specificity_improvement": enhanced_metrics.verification_specificity - standard_metrics.verification_specificity,
            "traceability_coverage_improvement": enhanced_metrics.traceability_coverage - standard_metrics.traceability_coverage,
            "overall_quality_improvement": enhanced_metrics.overall_quality_score - standard_metrics.overall_quality_score,
            "nfr_balance_improvement": self._compare_nfr_balance(
                standard_metrics.nfr_category_balance,
                enhanced_metrics.nfr_category_balance
            )
        }

    def _compare_nfr_balance(self, 
                           standard_balance: Dict[str, int],
                           enhanced_balance: Dict[str, int]) -> Dict[str, Any]:
        """Compare NFR category balance between approaches"""
        
        standard_total = sum(standard_balance.values()) or 1
        enhanced_total = sum(enhanced_balance.values()) or 1
        
        # Calculate distribution evenness (lower is better)
        def calculate_evenness(balance_dict, total):
            if not balance_dict:
                return 1.0
            proportions = [count / total for count in balance_dict.values()]
            return np.std(proportions)
        
        standard_evenness = calculate_evenness(standard_balance, standard_total)
        enhanced_evenness = calculate_evenness(enhanced_balance, enhanced_total)
        
        return {
            "standard_categories": len(standard_balance),
            "enhanced_categories": len(enhanced_balance),
            "standard_evenness": standard_evenness,
            "enhanced_evenness": enhanced_evenness,
            "balance_improvement": standard_evenness - enhanced_evenness,
            "category_selection_improvement": len(enhanced_balance) <= 4  # Target: max 4 categories
        }

    def _generate_improvement_summary(self, improvements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable improvement summary"""
        
        summary = {
            "overall_assessment": "Significant improvements achieved" if improvements.get("overall_quality_improvement", 0) > 0.2 else "Moderate improvements achieved",
            "key_improvements": [],
            "areas_addressed": [],
            "quantitative_gains": {}
        }
        
        # Identify key improvements
        if improvements.get("priority_balance_improvement", 0) > 0.1:
            summary["key_improvements"].append("Better priority distribution balance")
            summary["areas_addressed"].append("Priority imbalance issue resolved")
        
        if improvements.get("description_completeness_improvement", 0) > 0.1:
            summary["key_improvements"].append("More complete requirement descriptions")
            summary["areas_addressed"].append("Truncated descriptions issue resolved")
        
        if improvements.get("verification_specificity_improvement", 0) > 0.1:
            summary["key_improvements"].append("More specific verification methods")
            summary["areas_addressed"].append("Generic verification methods issue resolved")
        
        if improvements.get("traceability_coverage_improvement", 0) > 0.1:
            summary["key_improvements"].append("Enhanced traceability to operational context")
            summary["areas_addressed"].append("Missing operational links issue resolved")
        
        nfr_improvement = improvements.get("nfr_balance_improvement", {})
        if nfr_improvement.get("balance_improvement", 0) > 0:
            summary["key_improvements"].append("Better NFR category balance")
            summary["areas_addressed"].append("NFR overrepresentation issue resolved")
        
        # Quantitative gains
        summary["quantitative_gains"] = {
            "overall_quality": f"+{improvements.get('overall_quality_improvement', 0):.1%}",
            "description_quality": f"+{improvements.get('description_completeness_improvement', 0):.1%}",
            "verification_specificity": f"+{improvements.get('verification_specificity_improvement', 0):.1%}",
            "traceability_coverage": f"+{improvements.get('traceability_coverage_improvement', 0):.1%}"
        }
        
        return summary

    def _generate_quality_recommendations(self, 
                                        priority_balance: float,
                                        description_quality: float,
                                        verification_quality: float,
                                        traceability: float) -> List[str]:
        """Generate recommendations based on quality scores"""
        
        recommendations = []
        
        if priority_balance < self.quality_thresholds["priority_balance"]:
            recommendations.append("Improve priority distribution to match ARCADIA guidelines (30% MUST, 50% SHOULD, 20% COULD)")
        
        if description_quality < self.quality_thresholds["description_completeness"]:
            recommendations.append("Enhance requirement descriptions with more operational context and specific details")
        
        if verification_quality < self.quality_thresholds["verification_specificity"]:
            recommendations.append("Use more specific verification methods appropriate to requirement type and phase")
        
        if traceability < self.quality_thresholds["traceability_coverage"]:
            recommendations.append("Improve traceability links to operational capabilities and stakeholder needs")
        
        if not recommendations:
            recommendations.append("Requirements quality meets all target thresholds")
        
        return recommendations

    def generate_quality_dashboard_data(self, requirements_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for quality dashboard visualization"""
        
        quality_report = self._evaluate_requirements_quality(requirements_data)
        metrics = self._calculate_improvement_metrics(requirements_data)
        
        return {
            "summary_metrics": {
                "total_requirements": quality_report.total_requirements,
                "functional_count": quality_report.functional_count,
                "non_functional_count": quality_report.non_functional_count,
                "overall_quality_score": metrics.overall_quality_score
            },
            "quality_scores": {
                "priority_balance": quality_report.priority_balance_score,
                "description_quality": quality_report.description_quality_score,
                "verification_quality": quality_report.verification_quality_score,
                "traceability": quality_report.traceability_score
            },
            "priority_distribution": metrics.priority_distribution,
            "nfr_category_balance": metrics.nfr_category_balance,
            "improvement_recommendations": quality_report.improvement_recommendations,
            "quality_thresholds": self.quality_thresholds
        } 