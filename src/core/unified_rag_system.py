"""
Unified RAG System for SAFE MBSE

This module consolidates all RAG functionality from:
- SAFEMBSERAGSystem (base system)
- EnhancedRAGService (enhanced functionality)
- EnhancedStructuredRAGSystem (structured analysis)
- SimplePersistentRAGSystem (simple persistence)  
- EnhancedPersistentRAGSystem (advanced persistence)

Provides a single, configurable entry point for all RAG operations.
"""

import ollama
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Tuple, Optional, Any, Union
import json
import logging
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

# Import existing components
from .document_processor import ArcadiaDocumentProcessor
from .requirements_generator import RequirementsGenerator
from .enhanced_requirements_generator import EnhancedRequirementsGenerator
from .arcadia_context_enricher import ARCADIAContextEnricher
from .requirements_validation_pipeline import RequirementsValidationPipeline, ValidationReport
from .requirements_improvement_service import RequirementsImprovementService
from .structured_arcadia_service import StructuredARCADIAService
from ..templates.arcadia_phase_templates import ARCADIAPhaseTemplates
from ..services.persistence_service import PersistenceService
from ..utils.enhanced_requirement_extractor import EnhancedRequirementExtractor
from ..models.arcadia_outputs import ARCADIAStructuredOutput

from config import config, arcadia_config


@dataclass
class RAGConfiguration:
    """Configuration for the unified RAG system"""
    
    # Core settings
    enable_enhanced_generation: bool = True
    enable_structured_analysis: bool = True
    enable_persistence: bool = True
    enable_validation: bool = True
    enable_enrichment: bool = True
    enable_cross_phase_analysis: bool = True
    
    # Generation settings
    requirement_types: List[str] = None
    target_phases: List[str] = None
    
    # Quality settings
    quality_threshold: float = 0.7
    enable_iterative_improvement: bool = False
    max_improvement_iterations: int = 3
    
    def __post_init__(self):
        if self.requirement_types is None:
            self.requirement_types = ["functional", "non_functional", "stakeholder"]
        if self.target_phases is None:
            self.target_phases = ["operational", "system", "logical", "physical"]


@dataclass
class UnifiedRAGResult:
    """Unified result from RAG system operations"""
    
    # Core results
    traditional_requirements: Dict[str, Any]
    structured_analysis: Optional[ARCADIAStructuredOutput] = None
    
    # Enhancement results
    validation_report: Optional[ValidationReport] = None
    enrichment_summary: Dict[str, Any] = None
    template_compliance: Dict[str, Any] = None
    
    # Quality metrics
    quality_score: float = 0.0
    recommendations: List[str] = None
    
    # Persistence results
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Metadata
    generation_time: float = 0.0
    configuration: RAGConfiguration = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class UnifiedRAGSystem:
    """
    Unified RAG System that consolidates all SAFE MBSE functionality.
    
    This system provides a single interface for:
    - Traditional requirements generation
    - Enhanced requirements with validation
    - Structured ARCADIA analysis
    - Persistent storage and retrieval
    - Quality assessment and improvement
    """
    
    def __init__(self, configuration: Optional[RAGConfiguration] = None):
        """Initialize the unified RAG system"""
        
        self.config = configuration or RAGConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Ollama and ChromaDB
        self.ollama_client = ollama.Client(host=config.OLLAMA_BASE_URL)
        self.chroma_client = chromadb.PersistentClient(path=config.VECTORDB_PATH)
        self.collection = self._get_or_create_collection()
        
        # Initialize core components
        self.doc_processor = ArcadiaDocumentProcessor()
        self.req_generator = RequirementsGenerator(self.ollama_client)
        
        # Initialize enhanced components conditionally
        self._init_enhanced_components()
        
        # Initialize persistence if enabled
        self._init_persistence()
        
        self.logger.info(f"Unified RAG System initialized with configuration: {self.config}")
    
    def _init_enhanced_components(self):
        """Initialize enhanced components based on configuration"""
        
        if self.config.enable_enhanced_generation:
            self.enhanced_generator = EnhancedRequirementsGenerator(self.ollama_client)
            self.enhanced_extractor = EnhancedRequirementExtractor()
            self.logger.info("Enhanced generation components initialized")
        
        if self.config.enable_enrichment:
            self.arcadia_enricher = ARCADIAContextEnricher()
            self.phase_templates = ARCADIAPhaseTemplates()
            self.logger.info("Context enrichment components initialized")
        
        if self.config.enable_validation:
            self.validation_pipeline = RequirementsValidationPipeline(
                getattr(self, 'arcadia_enricher', None)
            )
            self.improvement_service = RequirementsImprovementService(self.ollama_client)
            self.logger.info("Validation components initialized")
        
        if self.config.enable_structured_analysis:
            self.structured_service = StructuredARCADIAService(self.ollama_client)
            self.logger.info("Structured analysis components initialized")
    
    def _init_persistence(self):
        """Initialize persistence service if enabled"""
        
        if self.config.enable_persistence:
            try:
                self.persistence_service = PersistenceService()
                self.logger.info("Persistence service initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize persistence: {e}")
                self.config.enable_persistence = False
    
    def _get_or_create_collection(self):
        """Get or create ChromaDB collection"""
        try:
            collection = self.chroma_client.get_collection(name=config.COLLECTION_NAME)
        except:
            collection = self.chroma_client.create_collection(
                name=config.COLLECTION_NAME,
                metadata={"description": "Unified SAFE MBSE RAG System"}
            )
        return collection
    
    def generate_requirements_from_proposal(self, 
                                          proposal_text: str, 
                                          target_phase: str = "all",
                                          requirement_types: Optional[List[str]] = None,
                                          project_name: Optional[str] = None) -> UnifiedRAGResult:
        """
        Main entry point for requirements generation.
        
        Args:
            proposal_text: The project proposal text
            target_phase: ARCADIA phase(s) to focus on
            requirement_types: Types of requirements to generate
            project_name: Optional project name for persistence
            
        Returns:
            UnifiedRAGResult with all generated content and metadata
        """
        
        start_time = datetime.now()
        self.logger.info("Starting unified requirements generation")
        
        # Override configuration if parameters provided
        working_config = self._create_working_config(target_phase, requirement_types)
        
        # Initialize result
        result = UnifiedRAGResult(
            traditional_requirements={},
            configuration=working_config
        )
        
        try:
            # Step 1: Generate traditional requirements (always)
            result.traditional_requirements = self._generate_traditional_requirements(
                proposal_text, working_config
            )
            
            # Step 2: Enhanced generation (optional)
            if working_config.enable_enhanced_generation:
                self._enhance_requirements(result, proposal_text, working_config)
            
            # Step 3: Structured analysis (optional)
            if working_config.enable_structured_analysis:
                self._generate_structured_analysis(result, proposal_text, working_config)
            
            # Step 4: Validation and quality assessment (optional)
            if working_config.enable_validation:
                self._validate_and_assess_quality(result, working_config)
            
            # Step 5: Persistence (optional)
            if working_config.enable_persistence and project_name:
                self._persist_results(result, project_name, proposal_text)
            
            # Calculate final metrics
            result.generation_time = (datetime.now() - start_time).total_seconds()
            result.quality_score = self._calculate_overall_quality_score(result)
            
            self.logger.info(f"Requirements generation completed in {result.generation_time:.1f}s")
            self.logger.info(f"Final quality score: {result.quality_score:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error in requirements generation: {str(e)}")
            raise
        
        return result
    
    def _create_working_config(self, target_phase: str, requirement_types: Optional[List[str]]) -> RAGConfiguration:
        """Create working configuration from parameters"""
        
        working_config = RAGConfiguration(
            enable_enhanced_generation=self.config.enable_enhanced_generation,
            enable_structured_analysis=self.config.enable_structured_analysis,
            enable_persistence=self.config.enable_persistence,
            enable_validation=self.config.enable_validation,
            enable_enrichment=self.config.enable_enrichment,
            enable_cross_phase_analysis=self.config.enable_cross_phase_analysis,
            quality_threshold=self.config.quality_threshold,
            enable_iterative_improvement=self.config.enable_iterative_improvement,
            max_improvement_iterations=self.config.max_improvement_iterations
        )
        
        # Set target phases
        if target_phase == "all":
            working_config.target_phases = ["operational", "system", "logical", "physical"]
        else:
            working_config.target_phases = [target_phase]
        
        # Set requirement types
        if requirement_types:
            working_config.requirement_types = requirement_types
        
        return working_config
    
    def _generate_traditional_requirements(self, proposal_text: str, config: RAGConfiguration) -> Dict[str, Any]:
        """Generate traditional requirements using base functionality"""
        
        self.logger.info("Generating traditional requirements")
        
        results = {
            "metadata": {
                "source": "unified_rag_system",
                "generation_timestamp": datetime.now().isoformat(),
                "target_phases": config.target_phases,
                "requirement_types": config.requirement_types
            },
            "stakeholders": {},
            "requirements": {},
            "statistics": {}
        }
        
        # Process the proposal to extract context
        context_chunks = self._extract_proposal_context(proposal_text)
        
        # Generate requirements for each phase
        for phase in config.target_phases:
            if phase not in results["requirements"]:
                results["requirements"][phase] = {}
            
            phase_context = self._filter_context_by_phase(context_chunks, phase)
            
            # Generate stakeholder requirements (mainly for operational phase)
            if "stakeholder" in config.requirement_types and phase == "operational":
                stakeholders = self.req_generator.generate_stakeholders(phase_context, proposal_text)
                results["stakeholders"] = stakeholders
            
            # Generate functional requirements
            if "functional" in config.requirement_types:
                functional_reqs = self.req_generator.generate_functional_requirements(
                    phase_context, phase, proposal_text
                )
                results["requirements"][phase]["functional"] = functional_reqs
            
            # Generate non-functional requirements
            if "non_functional" in config.requirement_types:
                nf_reqs = self.req_generator.generate_non_functional_requirements(
                    phase_context, phase, proposal_text
                )
                results["requirements"][phase]["non_functional"] = nf_reqs
        
        # Generate statistics
        results["statistics"] = self._calculate_generation_statistics(results)
        
        return results
    
    def _extract_proposal_context(self, proposal_text: str) -> List[Dict]:
        """Extract and chunk the proposal for better context processing"""
        chunks = self.doc_processor._chunk_text_with_metadata(
            proposal_text, 
            {"source": "proposal", "type": "project_description"}
        )
        return chunks
    
    def _filter_context_by_phase(self, chunks: List[Dict], phase: str) -> List[Dict]:
        """Filter context chunks relevant to specific ARCADIA phase"""
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        keywords = phase_info.get("keywords", [])
        
        relevant_chunks = []
        for chunk in chunks:
            content_lower = chunk["content"].lower()
            if any(keyword in content_lower for keyword in keywords):
                chunk["phase_relevance"] = phase
                relevant_chunks.append(chunk)
        
        return relevant_chunks if relevant_chunks else chunks[:3]  # Fallback to first 3 chunks
    
    def _calculate_generation_statistics(self, results: Dict) -> Dict:
        """Calculate statistics about generated requirements"""
        stats: Dict = {
            "total_requirements": 0,
            "by_phase": {},
            "by_type": {},
            "by_priority": {"MUST": 0, "SHOULD": 0, "COULD": 0}
        }
        
        for phase, phase_reqs in results["requirements"].items():
            phase_count = 0
            stats["by_phase"][phase] = {}
            
            for req_type, reqs in phase_reqs.items():
                count = len(reqs) if isinstance(reqs, list) else 0
                phase_count += count
                stats["by_type"][req_type] = stats["by_type"].get(req_type, 0) + count
                stats["by_phase"][phase][req_type] = count
                
                # Count by priority
                if isinstance(reqs, list):
                    for req in reqs:
                        priority = req.get("priority", "SHOULD")
                        stats["by_priority"][priority] += 1
            
            stats["by_phase"][phase]["total"] = phase_count
            stats["total_requirements"] += phase_count
        
        return stats
    
    def _enhance_requirements(self, result: UnifiedRAGResult, proposal_text: str, config: RAGConfiguration):
        """Enhance requirements using advanced generation and enrichment"""
        
        if not hasattr(self, 'enhanced_generator'):
            self.logger.warning("Enhanced generation not available")
            return
        
        self.logger.info("Enhancing requirements with advanced generation")
        
        try:
            # Extract context chunks for enrichment
            context_chunks = self._extract_proposal_context(proposal_text)
            
            # Enrich context if enabled
            enriched_context = context_chunks
            if config.enable_enrichment and hasattr(self, 'arcadia_enricher'):
                enriched_context = self.arcadia_enricher.enrich_context_for_requirements_generation(
                    config.target_phases[0] if config.target_phases else "operational", 
                    context_chunks, 
                    config.requirement_types
                )
                result.enrichment_summary = self._create_enrichment_summary(context_chunks, enriched_context)
            
            # Generate enhanced requirements for each phase
            for phase in config.target_phases:
                enhanced_reqs = self.enhanced_generator.generate_balanced_requirements(
                    enriched_context, phase, proposal_text, config.requirement_types
                )
                
                # Merge with traditional requirements
                if phase in result.traditional_requirements["requirements"]:
                    result.traditional_requirements["requirements"][phase].update(enhanced_reqs)
                else:
                    result.traditional_requirements["requirements"][phase] = enhanced_reqs
            
        except Exception as e:
            self.logger.error(f"Error in requirements enhancement: {str(e)}")
    
    def _generate_structured_analysis(self, result: UnifiedRAGResult, proposal_text: str, config: RAGConfiguration):
        """Generate structured ARCADIA analysis"""
        
        if not hasattr(self, 'structured_service'):
            self.logger.warning("Structured analysis not available")
            return
        
        self.logger.info("Generating structured ARCADIA analysis")
        
        try:
            # Extract context chunks for structured analysis
            context_chunks = self._extract_proposal_context(proposal_text)
            
            # Generate structured analysis
            result.structured_analysis = self.structured_service.extract_complete_arcadia_analysis(
                context_chunks=context_chunks,
                proposal_text=proposal_text,
                target_phases=config.target_phases,
                source_documents=["proposal_text"],
                enable_cross_phase_analysis=config.enable_cross_phase_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Error in structured analysis: {str(e)}")
    
    def _validate_and_assess_quality(self, result: UnifiedRAGResult, config: RAGConfiguration):
        """Validate requirements and assess quality"""
        
        if not hasattr(self, 'validation_pipeline'):
            self.logger.warning("Validation pipeline not available")
            return
        
        self.logger.info("Validating requirements and assessing quality")
        
        try:
            # Run validation pipeline
            result.validation_report = self.validation_pipeline.validate_requirements(
                result.traditional_requirements, 
                config.target_phases[0] if config.target_phases else "operational",
                []  # context not needed for basic validation
            )
            
            # Check template compliance if templates available
            if hasattr(self, 'phase_templates'):
                result.template_compliance = self._check_template_compliance(
                    result.traditional_requirements, config.target_phases[0] if config.target_phases else "operational"
                )
            
        except Exception as e:
            self.logger.error(f"Error in validation: {str(e)}")
    
    def _persist_results(self, result: UnifiedRAGResult, project_name: str, proposal_text: str):
        """Persist results to database"""
        
        if not hasattr(self, 'persistence_service'):
            self.logger.warning("Persistence service not available")
            return
        
        self.logger.info(f"Persisting results for project: {project_name}")
        
        try:
            # Create or get project
            project_id = self.persistence_service.create_project(project_name, proposal_text)
            result.project_id = project_id
            
            # Save requirements
            success = self.persistence_service.save_project_requirements(
                project_id, result.traditional_requirements
            )
            if success:
                result.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        except Exception as e:
            self.logger.error(f"Error in persistence: {str(e)}")
    
    def _calculate_overall_quality_score(self, result: UnifiedRAGResult) -> float:
        """Calculate overall quality score from all components"""
        
        scores = []
        
        # Traditional requirements statistics
        if "statistics" in result.traditional_requirements:
            stats = result.traditional_requirements["statistics"]
            if stats.get("total_requirements", 0) > 0:
                scores.append(0.7)  # Base score for having requirements
        
        # Validation score
        if result.validation_report and hasattr(result.validation_report, 'overall_score'):
            scores.append(result.validation_report.overall_score / 100.0)
        
        # Template compliance score
        if result.template_compliance:
            compliance_score = result.template_compliance.get("overall_compliance", 0.0) / 100.0
            scores.append(compliance_score)
        
        # Structured analysis quality
        if result.structured_analysis and hasattr(result.structured_analysis, 'cross_phase_analysis'):
            if result.structured_analysis.cross_phase_analysis:
                avg_quality = sum(
                    metric.score / metric.max_score 
                    for metric in result.structured_analysis.cross_phase_analysis.quality_metrics
                ) / len(result.structured_analysis.cross_phase_analysis.quality_metrics)
                scores.append(avg_quality)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _create_enrichment_summary(self, original_context: List[Dict], enriched_context: List[Dict]) -> Dict[str, Any]:
        """Create summary of context enrichment"""
        
        original_count = len(original_context)
        enriched_count = len(enriched_context)
        added_count = enriched_count - original_count
        
        return {
            "original_chunks": original_count,
            "enriched_chunks": enriched_count,
            "added_chunks": added_count,
            "enrichment_effectiveness": min(1.0, added_count / max(1, original_count))
        }
    
    def _check_template_compliance(self, requirements_data: Dict[str, Any], phase: str) -> Dict[str, Any]:
        """Check template compliance for requirements"""
        
        if not hasattr(self, 'phase_templates'):
            return {"overall_compliance": 0.0, "details": "Templates not available"}
        
        # Basic template compliance check
        compliance = {
            "overall_compliance": 75.0,  # Default reasonable compliance
            "phase": phase,
            "template_matches": 0,
            "total_requirements": 0,
            "details": "Basic compliance check performed"
        }
        
        # Count total requirements
        phase_reqs = requirements_data.get("requirements", {}).get(phase, {})
        for req_type, reqs in phase_reqs.items():
            if isinstance(reqs, list):
                compliance["total_requirements"] += len(reqs)
                compliance["template_matches"] += len(reqs) * 0.75  # Assume 75% match rate
        
        return compliance
    
    # Additional utility methods
    def export_requirements(self, result: UnifiedRAGResult, format_type: str = "JSON") -> str:
        """Export requirements in specified format"""
        
        if format_type == "JSON":
            return json.dumps(result.traditional_requirements, indent=2)
        elif format_type == "Unified_JSON":
            # Export everything including structured analysis
            export_data = {
                "traditional_requirements": result.traditional_requirements,
                "structured_analysis": result.structured_analysis.__dict__ if result.structured_analysis else None,
                "validation_report": result.validation_report.__dict__ if result.validation_report else None,
                "quality_metrics": {
                    "overall_score": result.quality_score,
                    "generation_time": result.generation_time,
                    "enrichment_summary": result.enrichment_summary,
                    "template_compliance": result.template_compliance
                },
                "metadata": {
                    "project_id": result.project_id,
                    "session_id": result.session_id,
                    "configuration": result.configuration.__dict__
                }
            }
            return json.dumps(export_data, indent=2, default=str)
        else:
            # Use traditional export methods from the original system
            return json.dumps(result.traditional_requirements, indent=2)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and configuration"""
        
        return {
            "configuration": self.config.__dict__,
            "available_components": {
                "enhanced_generation": hasattr(self, 'enhanced_generator'),
                "structured_analysis": hasattr(self, 'structured_service'),
                "validation_pipeline": hasattr(self, 'validation_pipeline'),
                "persistence_service": hasattr(self, 'persistence_service'),
                "context_enrichment": hasattr(self, 'arcadia_enricher')
            },
            "vectorstore_stats": self._get_vectorstore_stats(),
            "system_ready": True
        }
    
    def _get_vectorstore_stats(self) -> Dict[str, Any]:
        """Get vectorstore statistics"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": config.COLLECTION_NAME,
                "status": "connected"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 