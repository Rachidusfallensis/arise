from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .rag_system import SAFEMBSERAGSystem
from .structured_arcadia_service import StructuredARCADIAService
from ..models.arcadia_outputs import ARCADIAStructuredOutput
from config import config
import json

class EnhancedStructuredRAGSystem(SAFEMBSERAGSystem):
    """
    Enhanced RAG system that produces both traditional requirements 
    and structured ARCADIA outputs.
    
    Combines:
    - Traditional requirements generation (inherited from SAFEMBSERAGSystem)
    - Structured ARCADIA analysis (operational, system, logical, physical phases)
    - Cross-phase analysis (traceability, gaps, consistency, quality metrics)
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize structured ARCADIA service
        self.structured_service = StructuredARCADIAService(self.ollama_client)
        
        self.logger.info("Enhanced Structured RAG System initialized")
    
    def generate_enhanced_requirements_from_proposal(self, 
                                                   proposal_text: str, 
                                                   target_phase: str = "all",
                                                   requirement_types: Optional[List[str]] = None,
                                                   enable_structured_analysis: bool = True,
                                                   enable_cross_phase_analysis: bool = True) -> Dict:
        """
        Generate both traditional requirements and structured ARCADIA analysis
        
        Args:
            proposal_text: The project proposal text
            target_phase: ARCADIA phase to focus on ("operational", "system", "logical", "physical", "all")
            requirement_types: Types of requirements to generate ["functional", "non_functional", "stakeholder"]
            enable_structured_analysis: Whether to perform structured ARCADIA analysis
            enable_cross_phase_analysis: Whether to perform cross-phase analysis
            
        Returns:
            Enhanced results containing both traditional requirements and structured outputs
        """
        self.logger.info("Starting enhanced requirements generation with structured analysis")
        
        start_time = datetime.now()
        
        # Step 1: Generate traditional requirements (existing functionality)
        self.logger.info("Step 1: Generating traditional requirements")
        traditional_results = super().generate_requirements_from_proposal(
            proposal_text, target_phase, requirement_types
        )
        
        # Step 2: Generate structured ARCADIA analysis (new functionality)
        structured_results = None
        if enable_structured_analysis:
            self.logger.info("Step 2: Generating structured ARCADIA analysis")
            try:
                # Extract context chunks for structured analysis
                context_chunks = self._extract_proposal_context(proposal_text)
                
                # Determine phases for structured analysis
                target_phases = self._determine_structured_phases(target_phase)
                
                # Generate structured analysis
                structured_results = self.structured_service.extract_complete_arcadia_analysis(
                    context_chunks=context_chunks,
                    proposal_text=proposal_text,
                    target_phases=target_phases,
                    source_documents=["proposal_text"],
                    enable_cross_phase_analysis=enable_cross_phase_analysis
                )
                
                self.logger.info(f"Structured analysis completed for phases: {target_phases}")
                
            except Exception as e:
                self.logger.error(f"Error in structured analysis: {str(e)}")
                self.logger.error(f"   Error details: {type(e).__name__}")
                self.logger.info("Continuing with traditional requirements only")
                structured_results = None
        else:
            self.logger.info("Step 2: Skipping structured analysis (disabled)")
        
        # Step 3: Combine and enhance results
        enhanced_results = self._combine_traditional_and_structured_results(
            traditional_results, structured_results, start_time
        )
        
        total_time = (datetime.now() - start_time).total_seconds()
        # Format time duration for better readability
        if total_time < 60:
            time_str = f"{total_time:.1f} seconds"
        elif total_time < 3600:
            time_str = f"{total_time/60:.1f} minutes ({total_time:.1f} seconds)"
        else:
            time_str = f"{total_time/3600:.1f} hours ({total_time/60:.0f} minutes)"
        
        self.logger.info(f"Enhanced requirements generation completed in {time_str}")
        
        return enhanced_results
    
    def export_structured_requirements(self, enhanced_results: Dict, format_type: str) -> str:
        """
        Export structured requirements in various formats
        
        Args:
            enhanced_results: Results from generate_enhanced_requirements_from_proposal
            format_type: Export format ("JSON", "Markdown", "Excel", "DOORS", "ReqIF", "ARCADIA_JSON")
            
        Returns:
            Exported content as string
        """
        if format_type == "ARCADIA_JSON":
            return self._export_arcadia_json(enhanced_results)
        elif format_type == "Structured_Markdown":
            return self._export_structured_markdown(enhanced_results)
        else:
            # Fall back to traditional export for other formats
            return super().export_requirements(enhanced_results.get('traditional_requirements', {}), format_type)
    
    def get_structured_analysis_summary(self, enhanced_results: Dict) -> Dict[str, Any]:
        """
        Get a summary of the structured analysis results
        
        Args:
            enhanced_results: Results from enhanced generation
            
        Returns:
            Summary statistics and insights
        """
        structured_analysis = enhanced_results.get('structured_analysis')
        if not structured_analysis:
            return {"error": "No structured analysis available"}
        
        summary = {
            "phases_analyzed": [],
            "extraction_statistics": {},
            "cross_phase_insights": {},
            "quality_scores": {},
            "recommendations": []
        }
        
        # Analyze each phase (all ARCADIA phases)
        if structured_analysis.operational_analysis:
            summary["phases_analyzed"].append("operational")
            summary["extraction_statistics"]["operational"] = {
                "actors": len(structured_analysis.operational_analysis.actors),
                "capabilities": len(structured_analysis.operational_analysis.capabilities),
                "scenarios": len(structured_analysis.operational_analysis.scenarios),
                "processes": len(structured_analysis.operational_analysis.processes)
            }
        
        if structured_analysis.system_analysis:
            summary["phases_analyzed"].append("system")
            summary["extraction_statistics"]["system"] = {
                "actors": len(structured_analysis.system_analysis.actors),
                "functions": len(structured_analysis.system_analysis.functions),
                "capabilities": len(structured_analysis.system_analysis.capabilities),
                "functional_chains": len(structured_analysis.system_analysis.functional_chains)
            }
        
        if structured_analysis.logical_architecture:
            summary["phases_analyzed"].append("logical")
            summary["extraction_statistics"]["logical"] = {
                "components": len(structured_analysis.logical_architecture.components),
                "functions": len(structured_analysis.logical_architecture.functions),
                "interfaces": len(structured_analysis.logical_architecture.interfaces),
                "scenarios": len(structured_analysis.logical_architecture.scenarios)
            }
        
        if structured_analysis.physical_architecture:
            summary["phases_analyzed"].append("physical")
            summary["extraction_statistics"]["physical"] = {
                "components": len(structured_analysis.physical_architecture.components),
                "functions": len(structured_analysis.physical_architecture.functions),
                "implementation_constraints": len(structured_analysis.physical_architecture.constraints),
                "scenarios": len(structured_analysis.physical_architecture.scenarios)
            }
        
        # Cross-phase insights
        if structured_analysis.cross_phase_analysis:
            cross_phase = structured_analysis.cross_phase_analysis
            summary["cross_phase_insights"] = {
                "traceability_links": len(cross_phase.traceability_links),
                "gaps_identified": len(cross_phase.gap_analysis),
                "consistency_checks": len(cross_phase.consistency_checks),
                "coverage_matrix": cross_phase.coverage_matrix
            }
            
            # Extract quality scores
            for metric in cross_phase.quality_metrics:
                summary["quality_scores"][metric.metric_name] = {
                    "score": metric.score,
                    "max_score": metric.max_score,
                    "percentage": (metric.score / metric.max_score) * 100
                }
            
            # Generate recommendations based on gaps and quality
            summary["recommendations"] = self._generate_analysis_recommendations(cross_phase)
        
        return summary
    
    def _determine_structured_phases(self, target_phase: str) -> List[str]:
        """Determine which phases to analyze for structured analysis"""
        if target_phase == "all":
            return ["operational", "system", "logical", "physical"]  # All phases now implemented
        elif target_phase in ["operational", "system", "logical", "physical"]:
            return [target_phase]
        else:
            # Default to operational for unsupported phases
            return ["operational"]
    
    def _combine_traditional_and_structured_results(self, 
                                                   traditional_results: Dict,
                                                   structured_results: Optional[ARCADIAStructuredOutput],
                                                   start_time: datetime) -> Dict:
        """Combine traditional requirements with structured analysis"""
        
        # Start with traditional results as the base to ensure compatibility
        enhanced_results = traditional_results.copy() if traditional_results else {}
        
        # Add enhanced metadata
        enhanced_results["generation_metadata"] = {
            "generation_type": "enhanced_structured",
            "timestamp": start_time.isoformat(),
            "processing_time": (datetime.now() - start_time).total_seconds(),
            "includes_structured_analysis": structured_results is not None,
            "traditional_compatible": True
        }
        
        # Store traditional and structured results separately for advanced access
        enhanced_results["traditional_requirements"] = traditional_results
        enhanced_results["structured_analysis"] = structured_results
        
        # Generate enhancement summary
        if structured_results:
            phases_analyzed = []
            if structured_results.operational_analysis:
                phases_analyzed.append("operational")
            if structured_results.system_analysis:
                phases_analyzed.append("system")
            if structured_results.logical_architecture:
                phases_analyzed.append("logical")
            if structured_results.physical_architecture:
                phases_analyzed.append("physical")
            
            enhanced_results["enhancement_summary"] = {
                "phases_analyzed": phases_analyzed,
                "total_actors_identified": self._count_total_actors(structured_results),
                "total_capabilities_identified": self._count_total_capabilities(structured_results),
                "total_components_identified": self._count_total_components(structured_results),
                "total_functions_identified": self._count_total_functions(structured_results),
                "cross_phase_links": len(structured_results.cross_phase_analysis.traceability_links) if structured_results.cross_phase_analysis else 0,
                "quality_assessment_available": bool(structured_results.cross_phase_analysis and structured_results.cross_phase_analysis.quality_metrics)
            }
        else:
            enhanced_results["enhancement_summary"] = {
                "phases_analyzed": [],
                "total_actors_identified": 0,
                "total_capabilities_identified": 0,
                "cross_phase_links": 0,
                "quality_assessment_available": False,
                "note": "Structured analysis failed, traditional requirements only"
            }
        
        # Ensure we always return valid results even if traditional generation failed
        if not enhanced_results.get('requirements'):
            enhanced_results["requirements"] = {}
        if not enhanced_results.get('statistics'):
            enhanced_results["statistics"] = {
                "total_requirements": 0,
                "by_priority": {"MUST": 0, "SHOULD": 0, "COULD": 0},
                "by_phase": {},
                "average_quality": 0.0
            }
        if not enhanced_results.get('stakeholders'):
            enhanced_results["stakeholders"] = {}
        
        return enhanced_results
    
    def _extract_proposal_context(self, proposal_text: str) -> List[Dict[str, Any]]:
        """Extract context chunks from proposal text for structured analysis"""
        try:
            # Use the document processor to create context chunks
            context_chunks = []
            
            # Split proposal into manageable chunks (similar to RAG chunking)
            chunk_size = 1000
            overlap = 200
            
            for i in range(0, len(proposal_text), chunk_size - overlap):
                chunk_text = proposal_text[i:i + chunk_size]
                if chunk_text.strip():
                    context_chunks.append({
                        "content": chunk_text,
                        "page_content": chunk_text,  # For compatibility
                        "metadata": {
                            "source": "proposal_text",
                            "chunk_id": f"chunk_{len(context_chunks)}",
                            "start_index": i,
                            "end_index": min(i + chunk_size, len(proposal_text))
                        }
                    })
            
            self.logger.info(f"Created {len(context_chunks)} context chunks from proposal")
            return context_chunks
            
        except Exception as e:
            self.logger.error(f"Error extracting proposal context: {str(e)}")
            # Return minimal context chunk
            return [{
                "content": proposal_text[:1000] + "..." if len(proposal_text) > 1000 else proposal_text,
                "page_content": proposal_text[:1000] + "..." if len(proposal_text) > 1000 else proposal_text,
                "metadata": {"source": "proposal_text", "chunk_id": "chunk_0"}
            }]
    
    def _export_arcadia_json(self, enhanced_results: Dict) -> str:
        """Export structured ARCADIA analysis as JSON"""
        structured_analysis = enhanced_results.get('structured_analysis')
        if not structured_analysis:
            return json.dumps({"error": "No structured analysis available"}, indent=2)
        
        return structured_analysis.to_json()
    
    def _export_structured_markdown(self, enhanced_results: Dict) -> str:
        """Export structured analysis as comprehensive Markdown report"""
        structured_analysis = enhanced_results.get('structured_analysis')
        if not structured_analysis:
            return "# Error: No structured analysis available"
        
        md_content = []
        md_content.append("# ARCADIA Structured Analysis Report")
        md_content.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_content.append(f"\nAnalysis ID: {structured_analysis.generation_metadata.get('analysis_id', 'N/A')}")
        
        # Operational Analysis Section
        if structured_analysis.operational_analysis:
            md_content.append("\n## 1. Operational Analysis Phase")
            
            md_content.append("\n### Operational Actors")
            for actor in structured_analysis.operational_analysis.actors:
                md_content.append(f"\n#### {actor.name} ({actor.id})")
                md_content.append(f"**Role:** {actor.role_definition}")
                md_content.append(f"**Description:** {actor.description}")
                if actor.responsibilities:
                    md_content.append("**Responsibilities:**")
                    for resp in actor.responsibilities:
                        md_content.append(f"- {resp}")
            
            md_content.append("\n### Operational Capabilities")
            for capability in structured_analysis.operational_analysis.capabilities:
                md_content.append(f"\n#### {capability.name} ({capability.id})")
                md_content.append(f"**Mission:** {capability.mission_statement}")
                md_content.append(f"**Description:** {capability.description}")
                if capability.performance_constraints:
                    md_content.append("**Performance Constraints:**")
                    for constraint in capability.performance_constraints:
                        md_content.append(f"- {constraint}")
        
        # System Analysis Section
        if structured_analysis.system_analysis:
            md_content.append("\n## 2. System Analysis Phase")
            
            md_content.append("\n### System Boundary")
            boundary = structured_analysis.system_analysis.system_boundary
            md_content.append(f"**Scope:** {boundary.scope_definition}")
            if boundary.included_elements:
                md_content.append("**Included Elements:**")
                for element in boundary.included_elements:
                    md_content.append(f"- {element}")
            
            md_content.append("\n### System Functions")
            for function in structured_analysis.system_analysis.functions:
                md_content.append(f"\n#### {function.name} ({function.id})")
                md_content.append(f"**Type:** {function.function_type}")
                md_content.append(f"**Description:** {function.description}")
        
        # Logical Architecture Section
        if structured_analysis.logical_architecture:
            md_content.append("\n## 3. Logical Architecture Phase")
            
            md_content.append("\n### Logical Components")
            for component in structured_analysis.logical_architecture.components:
                md_content.append(f"\n#### {component.name} ({component.id})")
                md_content.append(f"**Type:** {component.component_type}")
                md_content.append(f"**Description:** {component.description}")
                if component.responsibilities:
                    md_content.append("**Responsibilities:**")
                    for resp in component.responsibilities:
                        md_content.append(f"- {resp}")
            
            md_content.append("\n### Logical Functions")
            for function in structured_analysis.logical_architecture.functions:
                md_content.append(f"\n#### {function.name} ({function.id})")
                # Format behavioral models as readable text
                behavioral_text = ""
                if function.behavioral_models:
                    behavioral_specs = [model.get('spec', str(model)) for model in function.behavioral_models]
                    behavioral_text = "; ".join(behavioral_specs)
                md_content.append(f"**Behavioral Specification:** {behavioral_text}")
                md_content.append(f"**Description:** {function.description}")
        
        # Physical Architecture Section
        if structured_analysis.physical_architecture:
            md_content.append("\n## 4. Physical Architecture Phase")
            
            md_content.append("\n### Physical Components")
            for component in structured_analysis.physical_architecture.components:
                md_content.append(f"\n#### {component.name} ({component.id})")
                md_content.append(f"**Type:** {component.component_type}")
                md_content.append(f"**Technology Platform:** {component.technology_platform}")
                md_content.append(f"**Description:** {component.description}")
                if component.resource_requirements:
                    md_content.append("**Resource Requirements:**")
                    for req in component.resource_requirements:
                        md_content.append(f"- {req}")
            
            md_content.append("\n### Implementation Constraints")
            for constraint in structured_analysis.physical_architecture.constraints:
                md_content.append(f"\n#### {constraint.constraint_type.title()} Constraint")
                md_content.append(f"**Description:** {constraint.description}")
                if hasattr(constraint, 'rationale') and constraint.rationale:
                    md_content.append(f"**Rationale:** {constraint.rationale}")
        
        # Cross-Phase Analysis Section
        if structured_analysis.cross_phase_analysis:
            md_content.append("\n## 5. Cross-Phase Analysis")
            
            cross_phase = structured_analysis.cross_phase_analysis
            
            md_content.append(f"\n### Traceability Analysis")
            md_content.append(f"**Total Links:** {len(cross_phase.traceability_links)}")
            for link in cross_phase.traceability_links[:5]:  # Show first 5 links
                md_content.append(f"- {link.source_element} → {link.target_element} ({link.relationship_type}, confidence: {link.confidence_score:.2f})")
            
            md_content.append(f"\n### Gap Analysis")
            md_content.append(f"**Total Gaps Identified:** {len(cross_phase.gap_analysis)}")
            for gap in cross_phase.gap_analysis:
                md_content.append(f"- **{gap.gap_type.upper()}**: {gap.description} (Severity: {gap.severity})")
            
            md_content.append(f"\n### Quality Metrics")
            for metric in cross_phase.quality_metrics:
                percentage = (metric.score / metric.max_score) * 100
                md_content.append(f"- **{metric.metric_name}**: {percentage:.1f}% ({metric.score:.2f}/{metric.max_score})")
        
        return "\n".join(md_content)
    
    def _count_total_actors(self, structured_results: ARCADIAStructuredOutput) -> int:
        """Count total actors across all phases"""
        total = 0
        if structured_results.operational_analysis:
            total += len(structured_results.operational_analysis.actors)
        if structured_results.system_analysis:
            total += len(structured_results.system_analysis.actors)
        # Note: Logical and Physical phases have components rather than actors
        return total
    
    def _count_total_capabilities(self, structured_results: ARCADIAStructuredOutput) -> int:
        """Count total capabilities across all phases"""
        total = 0
        if structured_results.operational_analysis:
            total += len(structured_results.operational_analysis.capabilities)
        if structured_results.system_analysis:
            total += len(structured_results.system_analysis.capabilities)
        # Note: Logical and Physical phases don't have explicit capabilities but have components/functions
        return total
    
    def _count_total_components(self, structured_results: ARCADIAStructuredOutput) -> int:
        """Count total components across logical and physical phases"""
        total = 0
        if structured_results.logical_architecture:
            total += len(structured_results.logical_architecture.components)
        if structured_results.physical_architecture:
            total += len(structured_results.physical_architecture.components)
        return total
    
    def _count_total_functions(self, structured_results: ARCADIAStructuredOutput) -> int:
        """Count total functions across all phases"""
        total = 0
        if structured_results.system_analysis:
            total += len(structured_results.system_analysis.functions)
        if structured_results.logical_architecture:
            total += len(structured_results.logical_architecture.functions)
        if structured_results.physical_architecture:
            total += len(structured_results.physical_architecture.functions)
        return total
    
    def _generate_analysis_recommendations(self, cross_phase_analysis) -> List[str]:
        """Generate recommendations based on cross-phase analysis"""
        recommendations = []
        
        # Recommendations based on gaps
        critical_gaps = [gap for gap in cross_phase_analysis.gap_analysis if gap.severity in ["critical", "major"]]
        if critical_gaps:
            recommendations.append(f"Address {len(critical_gaps)} critical/major gaps identified in the analysis")
        
        # Recommendations based on quality metrics
        low_quality_metrics = [metric for metric in cross_phase_analysis.quality_metrics if metric.score < 0.7]
        if low_quality_metrics:
            recommendations.append(f"Improve {len(low_quality_metrics)} quality metrics scoring below 70%")
        
        # Recommendations based on traceability
        if len(cross_phase_analysis.traceability_links) < 3:
            recommendations.append("Enhance traceability between operational and system phases")
        
        # Default recommendation if none identified
        if not recommendations:
            recommendations.append("Analysis completed successfully with good quality scores")
        
        return recommendations 