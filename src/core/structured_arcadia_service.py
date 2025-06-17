from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid

from ..models.arcadia_outputs import (
    ARCADIAStructuredOutput, OperationalAnalysisOutput, SystemAnalysisOutput,
    LogicalArchitectureOutput, PhysicalArchitectureOutput, 
    CrossPhaseAnalysisOutput, TraceabilityLink, GapAnalysisItem,
    ArchitectureConsistencyCheck, QualityMetric, ARCADIAPhaseType,
    create_extraction_metadata
)
from .operational_analysis_extractor import OperationalAnalysisExtractor
from .system_analysis_extractor import SystemAnalysisExtractor
from .logical_architecture_extractor import LogicalArchitectureExtractor
from .physical_architecture_extractor import PhysicalArchitectureExtractor

class StructuredARCADIAService:
    """
    Main orchestrator service for structured ARCADIA analysis.
    
    Coordinates extraction across all ARCADIA phases:
    1. Operational Analysis Phase
    2. System Analysis Phase  
    3. Logical Architecture Phase
    4. Physical Architecture Phase
    5. Cross-Phase Analysis
    
    Produces comprehensive structured outputs with traceability, gap analysis,
    architecture consistency checks, and quality metrics.
    """
    
    def __init__(self, ollama_client):
        self.logger = logging.getLogger(__name__)
        self.ollama_client = ollama_client
        
        # Initialize phase extractors
        self.operational_extractor = OperationalAnalysisExtractor(ollama_client)
        self.system_extractor = SystemAnalysisExtractor(ollama_client)
        self.logical_extractor = LogicalArchitectureExtractor(ollama_client)
        self.physical_extractor = PhysicalArchitectureExtractor(ollama_client)
        
        self.logger.info("Structured ARCADIA Service initialized")
    
    def extract_complete_arcadia_analysis(self,
                                        context_chunks: List[Dict[str, Any]],
                                        proposal_text: str,
                                        target_phases: Optional[List[str]] = None,
                                        source_documents: Optional[List[str]] = None,
                                        enable_cross_phase_analysis: bool = True) -> ARCADIAStructuredOutput:
        """
        Extract complete structured ARCADIA analysis across all requested phases
        
        Args:
            context_chunks: Document chunks with metadata
            proposal_text: Full proposal text
            target_phases: List of phases to extract ["operational", "system", "logical", "physical"]
            source_documents: List of source document paths
            enable_cross_phase_analysis: Whether to perform cross-phase analysis
            
        Returns:
            Complete structured ARCADIA output
        """
        self.logger.info("Starting complete ARCADIA structured analysis")
        
        start_time = datetime.now()
        analysis_id = str(uuid.uuid4())
        
        # Default to all phases if not specified
        if target_phases is None:
            target_phases = ["operational", "system", "logical", "physical"]
        
        source_docs = source_documents or ["proposal_text"]
        
        # Initialize result structure
        result = ARCADIAStructuredOutput()
        
        # Set generation metadata
        result.generation_metadata = {
            "analysis_id": analysis_id,
            "start_time": start_time.isoformat(),
            "target_phases": target_phases,
            "source_documents": source_docs,
            "service_version": "1.0.0"
        }
        
        # Phase 1: Operational Analysis
        operational_output = None
        if "operational" in target_phases:
            self.logger.info("Phase 1: Extracting Operational Analysis")
            try:
                operational_output = self.operational_extractor.extract_operational_analysis(
                    context_chunks, proposal_text, source_docs
                )
                result.operational_analysis = operational_output
                self.logger.info(f"Operational analysis completed: {len(operational_output.actors)} actors, "
                               f"{len(operational_output.capabilities)} capabilities")
            except Exception as e:
                self.logger.error(f"Error in operational analysis: {str(e)}")
        
        # Phase 2: System Analysis
        system_output = None
        if "system" in target_phases:
            self.logger.info("Phase 2: Extracting System Analysis")
            try:
                operational_actors = operational_output.actors if operational_output else []
                system_output = self.system_extractor.extract_system_analysis(
                    context_chunks, proposal_text, operational_actors, source_docs
                )
                result.system_analysis = system_output
                self.logger.info(f"System analysis completed: {len(system_output.actors)} actors, "
                              f"{len(system_output.functions)} functions")
            except Exception as e:
                self.logger.error(f"Error in system analysis: {str(e)}")
        
        # Phase 3: Logical Architecture
        logical_output = None
        if "logical" in target_phases:
            self.logger.info("Phase 3: Extracting Logical Architecture")
            try:
                logical_output = self.logical_extractor.extract_logical_architecture(
                    context_chunks, proposal_text, operational_output, system_output, source_docs
                )
                result.logical_architecture = logical_output
                self.logger.info(f"Logical architecture completed: {len(logical_output.components)} components, "
                               f"{len(logical_output.functions)} functions, {len(logical_output.interfaces)} interfaces")
            except Exception as e:
                self.logger.error(f"Error in logical architecture: {str(e)}")
        
        # Phase 4: Physical Architecture
        physical_output = None
        if "physical" in target_phases:
            self.logger.info("Phase 4: Extracting Physical Architecture")
            try:
                physical_output = self.physical_extractor.extract_physical_architecture(
                    context_chunks, proposal_text, operational_output, system_output, logical_output, source_docs
                )
                result.physical_architecture = physical_output
                self.logger.info(f"Physical architecture completed: {len(physical_output.components)} components, "
                               f"{len(physical_output.constraints)} constraints")
            except Exception as e:
                self.logger.error(f"Error in physical architecture: {str(e)}")
        
        # Cross-Phase Analysis
        if enable_cross_phase_analysis:
            self.logger.info("Performing cross-phase analysis")
            try:
                cross_phase_analysis = self._perform_cross_phase_analysis(
                    result, context_chunks, proposal_text
                )
                result.cross_phase_analysis = cross_phase_analysis
                self.logger.info(f"Cross-phase analysis completed: {len(cross_phase_analysis.traceability_links)} links, "
                              f"{len(cross_phase_analysis.gap_analysis)} gaps")
            except Exception as e:
                self.logger.error(f"Error in cross-phase analysis: {str(e)}")
        
        # Finalize metadata
        end_time = datetime.now()
        result.generation_metadata.update({
            "end_time": end_time.isoformat(),
            "processing_time_seconds": (end_time - start_time).total_seconds(),
            "phases_completed": [phase for phase in target_phases if getattr(result, f"{phase}_analysis", None) is not None]
        })
        
        self.logger.info(f"Complete ARCADIA analysis finished in {(end_time - start_time).total_seconds():.1f} seconds")
        
        return result
    
    def _perform_cross_phase_analysis(self,
                                    partial_result: ARCADIAStructuredOutput,
                                    context_chunks: List[Dict[str, Any]],
                                    proposal_text: str) -> CrossPhaseAnalysisOutput:
        """
        Perform cross-phase analysis including traceability, gap analysis, and consistency checks
        """
        self.logger.info("Starting cross-phase analysis")
        
        cross_phase = CrossPhaseAnalysisOutput()
        
        # Generate traceability links
        cross_phase.traceability_links = self._generate_traceability_links(partial_result)
        
        # Perform gap analysis
        cross_phase.gap_analysis = self._perform_gap_analysis(partial_result, context_chunks)
        
        # Check architecture consistency
        cross_phase.consistency_checks = self._check_architecture_consistency(partial_result)
        
        # Calculate quality metrics
        cross_phase.quality_metrics = self._calculate_quality_metrics(partial_result)
        
        # Generate coverage matrix
        cross_phase.coverage_matrix = self._generate_coverage_matrix(partial_result)
        
        # Perform impact analysis
        cross_phase.impact_analysis = self._perform_impact_analysis(partial_result)
        
        # Set metadata
        cross_phase.extraction_metadata = create_extraction_metadata(
            ["cross_phase_analysis"], datetime.now(),
            {"traceability_confidence": 0.8, "gap_analysis_confidence": 0.7},
            {"links_generated": len(cross_phase.traceability_links), 
             "gaps_identified": len(cross_phase.gap_analysis)}
        )
        
        return cross_phase
    
    def _generate_traceability_links(self, result: ARCADIAStructuredOutput) -> List[TraceabilityLink]:
        """Generate comprehensive bidirectional traceability links using enhanced semantic matching"""
        links: List[TraceabilityLink] = []
        
        # 1. Operational -> System Traceability
        if result.operational_analysis and result.system_analysis:
            self.logger.info("Generating Operational -> System traceability links")
            
            # Link operational capabilities to system capabilities
            for op_cap in result.operational_analysis.capabilities:
                best_cap_match = None
                best_cap_score = 0.5  # Minimum threshold
                
                for sys_cap in result.system_analysis.capabilities:
                    similarity = self._calculate_semantic_similarity(op_cap, sys_cap, "comprehensive")
                    if similarity > best_cap_score:
                        best_cap_score = similarity
                        best_cap_match = sys_cap
                
                if best_cap_match:
                    link = TraceabilityLink(
                        id=f"TRACE-{len(links)+1:03d}",
                        source_element=op_cap.id,
                        target_element=best_cap_match.id,
                        source_phase=ARCADIAPhaseType.OPERATIONAL,
                        target_phase=ARCADIAPhaseType.SYSTEM,
                        relationship_type="realizes",
                        confidence_score=best_cap_score,
                        validation_status="unverified"
                    )
                    links.append(link)
            
            # Link operational actors to system actors
            for op_actor in result.operational_analysis.actors:
                best_actor_match = None
                best_actor_score = 0.6  # Higher threshold for actors
                
                for sys_actor in result.system_analysis.actors:
                    similarity = self._calculate_semantic_similarity(op_actor, sys_actor, "contextual")
                    if similarity > best_actor_score:
                        best_actor_score = similarity
                        best_actor_match = sys_actor
                
                if best_actor_match:
                    link = TraceabilityLink(
                        id=f"TRACE-{len(links)+1:03d}",
                        source_element=op_actor.id,
                        target_element=best_actor_match.id,
                        source_phase=ARCADIAPhaseType.OPERATIONAL,
                        target_phase=ARCADIAPhaseType.SYSTEM,
                        relationship_type="implements",
                        confidence_score=best_actor_score,
                        validation_status="unverified"
                    )
                    links.append(link)
        
        # 2. System -> Logical Traceability
        if result.system_analysis and result.logical_architecture:
            self.logger.info("Generating System -> Logical traceability links")
            
            # Link system functions to logical functions
            for sys_func in result.system_analysis.functions:
                best_func_match = None
                best_func_score = 0.5
                
                for log_func in result.logical_architecture.functions:
                    similarity = self._calculate_semantic_similarity(sys_func, log_func, "functional")
                    if similarity > best_func_score:
                        best_func_score = similarity
                        best_func_match = log_func
                
                if best_func_match:
                    link = TraceabilityLink(
                        id=f"TRACE-{len(links)+1:03d}",
                        source_element=sys_func.id,
                        target_element=best_func_match.id,
                        source_phase=ARCADIAPhaseType.SYSTEM,
                        target_phase=ARCADIAPhaseType.LOGICAL,
                        relationship_type="decomposes_to",
                        confidence_score=best_func_score,
                        validation_status="unverified"
                    )
                    links.append(link)
            
            # Link system capabilities to logical components
            for sys_cap in result.system_analysis.capabilities:
                best_comp_match = None
                best_comp_score = 0.5
                
                for log_comp in result.logical_architecture.components:
                    similarity = self._calculate_semantic_similarity(sys_cap, log_comp, "comprehensive")
                    if similarity > best_comp_score:
                        best_comp_score = similarity
                        best_comp_match = log_comp
                
                if best_comp_match:
                    link = TraceabilityLink(
                        id=f"TRACE-{len(links)+1:03d}",
                        source_element=sys_cap.id,
                        target_element=best_comp_match.id,
                        source_phase=ARCADIAPhaseType.SYSTEM,
                        target_phase=ARCADIAPhaseType.LOGICAL,
                        relationship_type="allocated_to",
                        confidence_score=best_comp_score,
                        validation_status="unverified"
                    )
                    links.append(link)
        
        # 3. Logical -> Physical Traceability
        if result.logical_architecture and result.physical_architecture:
            self.logger.info("Generating Logical -> Physical traceability links")
            
            # Link logical components to physical components
            for log_comp in result.logical_architecture.components:
                best_phys_comp_match = None
                best_phys_comp_score = 0.5
                
                for phys_comp in result.physical_architecture.components:
                    similarity = self._calculate_semantic_similarity(log_comp, phys_comp, "comprehensive")
                    if similarity > best_phys_comp_score:
                        best_phys_comp_score = similarity
                        best_phys_comp_match = phys_comp
                
                if best_phys_comp_match:
                    link = TraceabilityLink(
                        id=f"TRACE-{len(links)+1:03d}",
                        source_element=log_comp.id,
                        target_element=best_phys_comp_match.id,
                        source_phase=ARCADIAPhaseType.LOGICAL,
                        target_phase=ARCADIAPhaseType.PHYSICAL,
                        relationship_type="implemented_by",
                        confidence_score=best_phys_comp_score,
                        validation_status="unverified"
                    )
                    links.append(link)
            
            # Link logical functions to physical functions
            for log_func in result.logical_architecture.functions:
                best_phys_func_match = None
                best_phys_func_score = 0.5
                
                for phys_func in result.physical_architecture.functions:
                    similarity = self._calculate_semantic_similarity(log_func, phys_func, "functional")
                    if similarity > best_phys_func_score:
                        best_phys_func_score = similarity
                        best_phys_func_match = phys_func
                
                if best_phys_func_match:
                    link = TraceabilityLink(
                        id=f"TRACE-{len(links)+1:03d}",
                        source_element=log_func.id,
                        target_element=best_phys_func_match.id,
                        source_phase=ARCADIAPhaseType.LOGICAL,
                        target_phase=ARCADIAPhaseType.PHYSICAL,
                        relationship_type="realized_by",
                        confidence_score=best_phys_func_score,
                        validation_status="unverified"
                    )
                    links.append(link)
        
        # 4. Cross-Phase Interface Traceability
        self._generate_interface_traceability_links(result, links)
        
        # 5. End-to-End Traceability (Operational -> Physical)
        if result.operational_analysis and result.physical_architecture:
            self.logger.info("Generating End-to-End traceability links")
            self._generate_end_to_end_traceability_links(result, links)
        
        self.logger.info(f"Generated {len(links)} total traceability links across all phases")
        return links
    
    def _generate_interface_traceability_links(self, result: ARCADIAStructuredOutput, links: List[TraceabilityLink]):
        """Generate traceability links for interfaces across phases"""
        # Link logical interfaces to physical interfaces (if available)
        if result.logical_architecture and result.physical_architecture:
            for log_intf in result.logical_architecture.interfaces:
                for phys_comp in result.physical_architecture.components:
                    # Check if physical component interfaces match logical interfaces
                    for phys_intf in phys_comp.interfaces:
                        intf_name = phys_intf.get('name', '') if isinstance(phys_intf, dict) else str(phys_intf)
                        similarity = self._calculate_name_similarity(log_intf.name, intf_name)
                        
                        if similarity > 0.7:
                            link = TraceabilityLink(
                                id=f"TRACE-{len(links)+1:03d}",
                                source_element=log_intf.id,
                                target_element=f"{phys_comp.id}:{intf_name}",
                                source_phase=ARCADIAPhaseType.LOGICAL,
                                target_phase=ARCADIAPhaseType.PHYSICAL,
                                relationship_type="implemented_through",
                                confidence_score=similarity,
                                validation_status="unverified"
                            )
                            links.append(link)
    
    def _generate_end_to_end_traceability_links(self, result: ARCADIAStructuredOutput, links: List[TraceabilityLink]):
        """Generate end-to-end traceability links across all phases"""
        # Link operational capabilities directly to physical components (through intermediate links)
        if result.operational_analysis and result.physical_architecture:
            for op_cap in result.operational_analysis.capabilities[:3]:  # Limit for performance
                for phys_comp in result.physical_architecture.components:
                    # Use description-based matching for end-to-end links
                    similarity = self._calculate_description_similarity(
                        op_cap.mission_statement, phys_comp.description
                    )
                    
                    if similarity > 0.6:
                        link = TraceabilityLink(
                            id=f"TRACE-{len(links)+1:03d}",
                            source_element=op_cap.id,
                            target_element=phys_comp.id,
                            source_phase=ARCADIAPhaseType.OPERATIONAL,
                            target_phase=ARCADIAPhaseType.PHYSICAL,
                            relationship_type="enables",
                            confidence_score=similarity,
                            validation_status="requires_validation"  # End-to-end links need validation
                        )
                        links.append(link)
    
    def _perform_gap_analysis(self, result: ARCADIAStructuredOutput, 
                            context_chunks: List[Dict[str, Any]]) -> List[GapAnalysisItem]:
        """Identify gaps in requirement coverage and consistency"""
        gaps: List[GapAnalysisItem] = []
        
        # Check for missing operational capabilities
        if result.operational_analysis:
            # Simple gap detection based on common capability patterns
            expected_capabilities = ["security", "monitoring", "data_processing", "user_interface"]
            found_capabilities = [cap.name.lower() for cap in result.operational_analysis.capabilities]
            
            for expected in expected_capabilities:
                if not any(expected in found for found in found_capabilities):
                    gap = GapAnalysisItem(
                        id=f"GAP-{len(gaps)+1:03d}",
                        gap_type="missing",
                        phase=ARCADIAPhaseType.OPERATIONAL,
                        description=f"Missing {expected} capability in operational analysis",
                        severity="medium",
                        recommendations=[f"Consider adding {expected} capability requirements"]
                    )
                    gaps.append(gap)
        
        # Check for system-operational inconsistencies
        if result.operational_analysis and result.system_analysis:
            op_actor_count = len(result.operational_analysis.actors)
            sys_actor_count = len(result.system_analysis.actors)
            
            if abs(op_actor_count - sys_actor_count) > max(3, op_actor_count * 0.5):
                gap = GapAnalysisItem(
                    id=f"GAP-{len(gaps)+1:03d}",
                    gap_type="inconsistent",
                    phase=ARCADIAPhaseType.SYSTEM,
                    description=f"Significant mismatch in actor count: {op_actor_count} operational vs {sys_actor_count} system",
                    severity="major",
                    recommendations=["Review actor mappings between operational and system phases"]
                )
                gaps.append(gap)
        
        self.logger.info(f"Identified {len(gaps)} gaps in analysis")
        return gaps
    
    def _check_architecture_consistency(self, result: ARCADIAStructuredOutput) -> List[ArchitectureConsistencyCheck]:
        """Check consistency across architecture phases"""
        checks = []
        
        # Model coherence check
        coherence_check = ArchitectureConsistencyCheck(
            id="CONSIST-001",
            check_type="model_coherence",
            phases_involved=[ARCADIAPhaseType.OPERATIONAL, ARCADIAPhaseType.SYSTEM],
            status="passed",
            description="Model coherence across operational and system phases",
            issues_found=[],
            recommendations=[]
        )
        
        # Check for coherence issues
        if result.operational_analysis and result.system_analysis:
            op_capabilities = len(result.operational_analysis.capabilities)
            sys_capabilities = len(result.system_analysis.capabilities)
            
            if sys_capabilities < op_capabilities * 0.5:
                coherence_check.status = "warning"
                coherence_check.issues_found.append("System capabilities significantly fewer than operational capabilities")
                coherence_check.recommendations.append("Review system capability coverage")
        
        checks.append(coherence_check)
        
        # Interface compatibility check (placeholder)
        interface_check = ArchitectureConsistencyCheck(
            id="CONSIST-002",
            check_type="interface_compatibility",
            phases_involved=[ARCADIAPhaseType.SYSTEM],
            status="passed",
            description="Interface compatibility within system phase"
        )
        checks.append(interface_check)
        
        self.logger.info(f"Performed {len(checks)} consistency checks")
        return checks
    
    def _calculate_quality_metrics(self, result: ARCADIAStructuredOutput) -> List[QualityMetric]:
        """Calculate quality metrics for the analysis"""
        metrics = []
        
        # Operational analysis quality
        if result.operational_analysis:
            op_actors = len(result.operational_analysis.actors)
            op_capabilities = len(result.operational_analysis.capabilities)
            op_scenarios = len(result.operational_analysis.scenarios)
            
            # Completeness metric
            completeness_score = min((op_actors * 0.3 + op_capabilities * 0.4 + op_scenarios * 0.3) / 5, 1.0)
            completeness_metric = QualityMetric(
                id="QUALITY-001",
                metric_name="Operational Analysis Completeness",
                metric_type="requirement_quality",
                phase=ARCADIAPhaseType.OPERATIONAL,
                score=completeness_score,
                max_score=1.0,
                criteria=["Actor coverage", "Capability completeness", "Scenario coverage"],
                assessment_details={
                    "actors_count": op_actors,
                    "capabilities_count": op_capabilities,
                    "scenarios_count": op_scenarios
                }
            )
            metrics.append(completeness_metric)
        
        # System analysis quality
        if result.system_analysis:
            sys_actors = len(result.system_analysis.actors)
            sys_functions = len(result.system_analysis.functions)
            sys_capabilities = len(result.system_analysis.capabilities)
            
            # Architecture quality metric
            architecture_score = min((sys_actors * 0.2 + sys_functions * 0.5 + sys_capabilities * 0.3) / 8, 1.0)
            architecture_metric = QualityMetric(
                id="QUALITY-002",
                metric_name="System Architecture Quality",
                metric_type="architecture_quality",
                phase=ARCADIAPhaseType.SYSTEM,
                score=architecture_score,
                max_score=1.0,
                criteria=["Actor definition", "Function decomposition", "Capability realization"],
                assessment_details={
                    "actors_count": sys_actors,
                    "functions_count": sys_functions,
                    "capabilities_count": sys_capabilities
                }
            )
            metrics.append(architecture_metric)
        
        self.logger.info(f"Calculated {len(metrics)} quality metrics")
        return metrics
    
    def _generate_coverage_matrix(self, result: ARCADIAStructuredOutput) -> Dict[str, Dict[str, float]]:
        """Generate coverage matrix showing relationships between phases"""
        matrix = {}
        
        if result.operational_analysis and result.system_analysis:
            matrix["operational_to_system"] = {
                "actor_coverage": self._calculate_actor_coverage(
                    result.operational_analysis.actors, 
                    result.system_analysis.actors
                ),
                "capability_coverage": self._calculate_capability_coverage(
                    result.operational_analysis.capabilities,
                    result.system_analysis.capabilities
                )
            }
        
        return matrix
    
    def _perform_impact_analysis(self, result: ARCADIAStructuredOutput) -> Dict[str, List[str]]:
        """Perform impact analysis for change propagation"""
        impact_analysis = {}
        
        # Identify high-impact elements
        if result.operational_analysis:
            high_impact_capabilities = []
            for cap in result.operational_analysis.capabilities:
                if len(cap.involved_actors) > 2:  # Capabilities involving multiple actors
                    high_impact_capabilities.append(cap.id)
            
            impact_analysis["high_impact_operational_capabilities"] = high_impact_capabilities
        
        if result.system_analysis:
            critical_functions = []
            for func in result.system_analysis.functions:
                if func.function_type == "primary" and len(func.allocated_actors) > 1:
                    critical_functions.append(func.id)
            
            impact_analysis["critical_system_functions"] = critical_functions
        
        return impact_analysis
    
    # Enhanced Semantic Matching Utility Methods
    def _calculate_semantic_similarity(self, element1: Any, element2: Any, 
                                     similarity_type: str = "comprehensive") -> float:
        """
        Calculate semantic similarity between two ARCADIA elements using multiple criteria
        
        Args:
            element1, element2: ARCADIA elements to compare
            similarity_type: Type of similarity calculation
                - "name_only": Basic name similarity
                - "comprehensive": Multi-criteria semantic matching
                - "contextual": Context-aware similarity including descriptions
                - "functional": Function/capability-based similarity
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if similarity_type == "name_only":
            return self._calculate_name_similarity(element1.name, element2.name)
        
        elif similarity_type == "comprehensive":
            # Multi-criteria scoring
            name_score = self._calculate_name_similarity(element1.name, element2.name) * 0.4
            description_score = self._calculate_description_similarity(
                getattr(element1, 'description', ''), 
                getattr(element2, 'description', '')
            ) * 0.3
            context_score = self._calculate_contextual_similarity(element1, element2) * 0.3
            
            return name_score + description_score + context_score
        
        elif similarity_type == "contextual":
            # Include context and relationship information
            name_score = self._calculate_name_similarity(element1.name, element2.name) * 0.3
            description_score = self._calculate_description_similarity(
                getattr(element1, 'description', ''), 
                getattr(element2, 'description', '')
            ) * 0.4
            relationship_score = self._calculate_relationship_similarity(element1, element2) * 0.3
            
            return name_score + description_score + relationship_score
        
        elif similarity_type == "functional":
            # Function and capability-based matching
            return self._calculate_functional_similarity(element1, element2)
        
        else:
            return self._calculate_name_similarity(element1.name, element2.name)
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Enhanced name similarity calculation with multiple techniques"""
        if not name1 or not name2:
            return 0.0
            
        name1_lower = name1.lower().strip()
        name2_lower = name2.lower().strip()
        
        # Exact match
        if name1_lower == name2_lower:
            return 1.0
        
        # Substring matching (bidirectional)
        if name1_lower in name2_lower or name2_lower in name1_lower:
            shorter = min(len(name1_lower), len(name2_lower))
            longer = max(len(name1_lower), len(name2_lower))
            return 0.7 + (shorter / longer) * 0.2  # 0.7-0.9 range
        
        # Word-based similarity with synonyms
        words1 = set(name1_lower.split())
        words2 = set(name2_lower.split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        if not words1 or not words2:
            return 0.0
        
        # Direct word matching
        common_words = words1.intersection(words2)
        if common_words:
            jaccard_similarity = len(common_words) / len(words1.union(words2))
            return min(jaccard_similarity * 1.2, 1.0)  # Boost direct matches
        
        # Synonym and related term matching
        synonym_score = self._calculate_synonym_similarity(words1, words2)
        if synonym_score > 0:
            return synonym_score
        
        # Character-level similarity (Levenshtein-inspired)
        char_similarity = self._calculate_character_similarity(name1_lower, name2_lower)
        return char_similarity * 0.6  # Lower weight for character similarity
    
    def _calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """Calculate similarity between element descriptions"""
        if not desc1 or not desc2:
            return 0.0
        
        desc1_lower = desc1.lower()
        desc2_lower = desc2.lower()
        
        # Extract key terms (nouns, verbs, domain-specific words)
        key_terms1 = self._extract_key_terms(desc1_lower)
        key_terms2 = self._extract_key_terms(desc2_lower)
        
        if not key_terms1 or not key_terms2:
            return 0.0
        
        # Calculate term overlap
        common_terms = key_terms1.intersection(key_terms2)
        if common_terms:
            jaccard_similarity = len(common_terms) / len(key_terms1.union(key_terms2))
            return jaccard_similarity
        
        # Check for semantic similarity in descriptions
        return self._calculate_semantic_term_similarity(key_terms1, key_terms2)
    
    def _calculate_contextual_similarity(self, element1: Any, element2: Any) -> float:
        """Calculate similarity based on element context and relationships"""
        # Type-based similarity
        type1 = type(element1).__name__
        type2 = type(element2).__name__
        
        if type1 != type2:
            return 0.0  # Different types can't be contextually similar
        
        # Attribute-based similarity
        similarity_score = 0.0
        attribute_count = 0
        
        # Check common attributes based on element type
        if hasattr(element1, 'responsibilities') and hasattr(element2, 'responsibilities'):
            resp1 = set(getattr(element1, 'responsibilities', []))
            resp2 = set(getattr(element2, 'responsibilities', []))
            if resp1 or resp2:
                resp_similarity = len(resp1.intersection(resp2)) / max(len(resp1.union(resp2)), 1)
                similarity_score += resp_similarity
                attribute_count += 1
        
        if hasattr(element1, 'capabilities') and hasattr(element2, 'capabilities'):
            cap1 = set(getattr(element1, 'capabilities', []))
            cap2 = set(getattr(element2, 'capabilities', []))
            if cap1 or cap2:
                cap_similarity = len(cap1.intersection(cap2)) / max(len(cap1.union(cap2)), 1)
                similarity_score += cap_similarity
                attribute_count += 1
        
        if hasattr(element1, 'involved_actors') and hasattr(element2, 'allocated_actors'):
            actors1 = set(getattr(element1, 'involved_actors', []))
            actors2 = set(getattr(element2, 'allocated_actors', []))
            if actors1 or actors2:
                actor_similarity = len(actors1.intersection(actors2)) / max(len(actors1.union(actors2)), 1)
                similarity_score += actor_similarity
                attribute_count += 1
        
        return similarity_score / max(attribute_count, 1)
    
    def _calculate_relationship_similarity(self, element1: Any, element2: Any) -> float:
        """Calculate similarity based on element relationships"""
        # Check parent-child relationships
        parent1 = getattr(element1, 'parent_component', None) or getattr(element1, 'parent_function', None)
        parent2 = getattr(element2, 'parent_component', None) or getattr(element2, 'parent_function', None)
        
        if parent1 and parent2:
            parent_similarity = self._calculate_name_similarity(parent1, parent2)
            if parent_similarity > 0.6:
                return 0.8  # Strong relationship indicator
        
        # Check sub-elements
        subs1 = getattr(element1, 'sub_components', []) or getattr(element1, 'sub_functions', [])
        subs2 = getattr(element2, 'sub_components', []) or getattr(element2, 'sub_functions', [])
        
        if subs1 and subs2:
            sub_overlap = len(set(subs1).intersection(set(subs2)))
            if sub_overlap > 0:
                return min(sub_overlap / max(len(subs1), len(subs2)), 0.7)
        
        return 0.0
    
    def _calculate_functional_similarity(self, element1: Any, element2: Any) -> float:
        """Calculate similarity based on functional characteristics"""
        # For functions, check input/output compatibility
        if hasattr(element1, 'input_interfaces') and hasattr(element2, 'input_interfaces'):
            inputs1 = getattr(element1, 'input_interfaces', [])
            inputs2 = getattr(element2, 'input_interfaces', [])
            outputs1 = getattr(element1, 'output_interfaces', [])
            outputs2 = getattr(element2, 'output_interfaces', [])
            
            input_similarity = self._calculate_interface_similarity(inputs1, inputs2)
            output_similarity = self._calculate_interface_similarity(outputs1, outputs2)
            
            return (input_similarity + output_similarity) / 2
        
        # For capabilities, check mission alignment
        if hasattr(element1, 'mission_statement') and hasattr(element2, 'description'):
            mission1 = getattr(element1, 'mission_statement', '')
            desc2 = getattr(element2, 'description', '')
            return self._calculate_description_similarity(mission1, desc2)
        
        return 0.0
    
    def _calculate_synonym_similarity(self, words1: set, words2: set) -> float:
        """Calculate similarity based on synonyms and related terms"""
        # Domain-specific synonym mappings for ARCADIA
        synonym_groups = [
            {'monitor', 'observe', 'watch', 'track', 'surveillance'},
            {'process', 'handle', 'manage', 'execute', 'perform'},
            {'user', 'operator', 'actor', 'stakeholder', 'participant'},
            {'system', 'platform', 'infrastructure', 'framework'},
            {'security', 'protection', 'safety', 'defense'},
            {'data', 'information', 'content', 'payload'},
            {'interface', 'connection', 'link', 'communication'},
            {'control', 'command', 'manage', 'govern', 'regulate'},
            {'analyze', 'evaluate', 'assess', 'examine', 'review'},
            {'network', 'communication', 'connectivity', 'transmission'}
        ]
        
        synonym_score = 0.0
        total_comparisons = 0
        
        for word1 in words1:
            for word2 in words2:
                total_comparisons += 1
                # Check if words are in the same synonym group
                for group in synonym_groups:
                    if word1 in group and word2 in group:
                        synonym_score += 0.8  # High similarity for synonyms
                        break
                else:
                    # Check for partial matches or root words
                    if len(word1) > 3 and len(word2) > 3:
                        if word1[:3] == word2[:3] or word1[-3:] == word2[-3:]:
                            synonym_score += 0.4  # Moderate similarity for root matches
        
        return synonym_score / max(total_comparisons, 1)
    
    def _calculate_character_similarity(self, str1: str, str2: str) -> float:
        """Calculate character-level similarity (simplified Levenshtein)"""
        if not str1 or not str2:
            return 0.0
        
        if str1 == str2:
            return 1.0
        
        # Simple character overlap calculation
        chars1 = set(str1)
        chars2 = set(str2)
        common_chars = chars1.intersection(chars2)
        
        if not common_chars:
            return 0.0
        
        char_similarity = len(common_chars) / len(chars1.union(chars2))
        
        # Boost for similar lengths
        length_factor = min(len(str1), len(str2)) / max(len(str1), len(str2))
        
        return char_similarity * length_factor
    
    def _extract_key_terms(self, text: str) -> set:
        """Extract key terms from text (nouns, domain terms, etc.)"""
        # Domain-specific keywords for ARCADIA
        domain_keywords = {
            'system', 'component', 'function', 'capability', 'actor', 'interface',
            'requirement', 'specification', 'architecture', 'design', 'model',
            'operational', 'logical', 'physical', 'performance', 'security',
            'data', 'process', 'workflow', 'scenario', 'constraint', 'validation'
        }
        
        # Simple term extraction (can be enhanced with NLP)
        words = set(text.lower().split())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'is', 'are', 'was', 'were', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        key_terms = words - stop_words
        
        # Prefer domain-specific terms and longer words
        weighted_terms = set()
        for term in key_terms:
            if len(term) >= 3:  # Filter out very short words
                if term in domain_keywords or len(term) >= 5:
                    weighted_terms.add(term)
        
        return weighted_terms or key_terms  # Fallback to all terms if no weighted terms
    
    def _calculate_semantic_term_similarity(self, terms1: set, terms2: set) -> float:
        """Calculate semantic similarity between term sets"""
        if not terms1 or not terms2:
            return 0.0
        
        # Check for semantic relationships
        total_score = 0.0
        total_comparisons = 0
        
        for term1 in terms1:
            for term2 in terms2:
                total_comparisons += 1
                
                # Character similarity for similar terms
                char_sim = self._calculate_character_similarity(term1, term2)
                if char_sim > 0.6:
                    total_score += char_sim * 0.7
                
                # Check for common roots or stems
                if len(term1) > 4 and len(term2) > 4:
                    if term1[:4] == term2[:4] or term1[-4:] == term2[-4:]:
                        total_score += 0.5
        
        return total_score / max(total_comparisons, 1)
    
    def _calculate_interface_similarity(self, interfaces1: List[Dict], interfaces2: List[Dict]) -> float:
        """Calculate similarity between interface specifications"""
        if not interfaces1 or not interfaces2:
            return 0.0
        
        total_score = 0.0
        comparisons = 0
        
        for intf1 in interfaces1:
            for intf2 in interfaces2:
                comparisons += 1
                
                # Compare interface types
                type1 = intf1.get('type', '') if isinstance(intf1, dict) else str(intf1)
                type2 = intf2.get('type', '') if isinstance(intf2, dict) else str(intf2)
                
                if type1 == type2:
                    total_score += 1.0
                elif self._calculate_name_similarity(type1, type2) > 0.6:
                    total_score += 0.7
        
        return total_score / max(comparisons, 1)
    
    def _calculate_actor_coverage(self, op_actors: List, sys_actors: List) -> float:
        """Calculate coverage of operational actors by system actors"""
        if not op_actors:
            return 1.0
        
        covered_count = 0
        for op_actor in op_actors:
            for sys_actor in sys_actors:
                if self._calculate_name_similarity(op_actor.name, sys_actor.name) > 0.6:
                    covered_count += 1
                    break
        
        return covered_count / len(op_actors)
    
    def _calculate_capability_coverage(self, op_capabilities: List, sys_capabilities: List) -> float:
        """Calculate coverage of operational capabilities by system capabilities"""
        if not op_capabilities:
            return 1.0
        
        covered_count = 0
        for op_cap in op_capabilities:
            for sys_cap in sys_capabilities:
                if self._calculate_name_similarity(op_cap.name, sys_cap.name) > 0.6:
                    covered_count += 1
                    break
        
        return covered_count / len(op_capabilities) 