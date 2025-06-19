"""
Consolidated ARCADIA Extractors

This module consolidates all ARCADIA phase extractors into a single unified class:
- OperationalAnalysisExtractor → operational_analysis()
- SystemAnalysisExtractor → system_analysis()  
- LogicalArchitectureExtractor → logical_architecture()
- PhysicalArchitectureExtractor → physical_architecture()

Each phase extractor is now a method of the BaseARCADIAExtractor class.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from abc import ABC, abstractmethod
from datetime import datetime
import json

from ..models.arcadia_outputs import (
    ARCADIAStructuredOutput, OperationalAnalysisOutput, SystemAnalysisOutput, 
    LogicalArchitectureOutput, PhysicalArchitectureOutput,
    OperationalActor, SystemActor, LogicalComponent, PhysicalComponent,
    OperationalCapability, SystemCapability, OperationalScenario, LogicalScenario, PhysicalScenario,
    SystemFunction, LogicalFunction, PhysicalFunction, LogicalInterface,
    OperationalProcess, FunctionalChain, ImplementationConstraint,
    CrossPhaseAnalysisOutput, TraceabilityLink, GapAnalysisItem, 
    ArchitectureConsistencyCheck, QualityMetric, ARCADIAPhaseType
)
from config import config, arcadia_config


class BaseARCADIAExtractor:
    """
    Unified ARCADIA extractor that handles all four phases:
    - Operational Analysis
    - System Analysis
    - Logical Architecture
    - Physical Architecture
    
    Each phase has its specialized extraction method with common infrastructure.
    """
    
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client
        self.logger = logging.getLogger(__name__)
        
        # Common extraction settings
        self.extraction_settings = {
            "max_retries": 3,
            "temperature": 0.1,
            "max_tokens": 4000,
            "timeout": 60
        }
        
        # Phase-specific prompts loaded from config
        self.phase_prompts = self._load_phase_prompts()
        
        self.logger.info("Unified ARCADIA extractor initialized")
    
    def _load_phase_prompts(self) -> Dict[str, Dict[str, str]]:
        """Load phase-specific prompts for extraction"""
        
        return {
            "operational": {
                "actors": """
                Extract operational actors from the text. An operational actor is:
                - An external entity that interacts with the system
                - Has specific roles and responsibilities
                - Can be a person, organization, or external system
                
                For each actor, identify:
                - Name and type
                - Primary responsibilities
                - Interaction patterns
                - Goals and constraints
                """,
                
                "capabilities": """
                Extract operational capabilities from the text. A capability is:
                - A high-level ability the system must provide
                - Business-oriented and measurable
                - Independent of implementation
                
                For each capability, identify:
                - Name and description
                - Performance measures
                - Enabling conditions
                - Dependencies
                """,
                
                "scenarios": """
                Extract operational scenarios from the text. A scenario is:
                - A sequence of interactions between actors and the system
                - Represents a typical use case or mission
                - Has clear start and end conditions
                
                For each scenario, identify:
                - Scenario name and objective
                - Participating actors
                - Main steps/interactions
                - Success criteria
                """,
                
                "processes": """
                Extract operational processes from the text. A process is:
                - A structured sequence of activities
                - Transforms inputs into outputs
                - Has defined roles and responsibilities
                
                For each process, identify:
                - Process name and purpose
                - Input/output elements
                - Key activities and decisions
                - Performance criteria
                """
            },
            
            "system": {
                "actors": """
                Extract system actors from the text. A system actor is:
                - An entity that interacts directly with the system
                - More specific than operational actors
                - Can be users, external systems, or devices
                
                For each actor, identify:
                - Name and type (user, system, device)
                - System interfaces used
                - Interaction patterns
                - Authorization levels
                """,
                
                "functions": """
                Extract system functions from the text. A system function is:
                - A transformation performed by the system
                - Takes inputs and produces outputs
                - Supports operational capabilities
                
                For each function, identify:
                - Function name and purpose
                - Input/output data
                - Performance requirements
                - Error handling
                """,
                
                "capabilities": """
                Extract system capabilities from the text. A system capability is:
                - A cohesive set of system functions
                - Directly supports operational capabilities
                - Has measurable performance attributes
                
                For each capability, identify:
                - Name and functional scope
                - Supporting functions
                - Performance measures
                - Quality attributes
                """,
                
                "functional_chains": """
                Extract functional chains from the text. A functional chain is:
                - A sequence of connected functions
                - Realizes a complete capability
                - Shows data/control flow
                
                For each chain, identify:
                - Chain name and purpose
                - Sequence of functions
                - Data flows between functions
                - Control conditions
                """
            },
            
            "logical": {
                "components": """
                Extract logical components from the text. A logical component is:
                - A cohesive part of the system architecture
                - Encapsulates related functions
                - Has well-defined interfaces
                
                For each component, identify:
                - Component name and responsibilities
                - Encapsulated functions
                - Required/provided interfaces
                - Internal structure
                """,
                
                "functions": """
                Extract logical functions from the text. A logical function is:
                - An allocated system function
                - Assigned to a specific component
                - Has defined implementation approach
                
                For each function, identify:
                - Function name and behavior
                - Host component
                - Implementation constraints
                - Interface requirements
                """,
                
                "interfaces": """
                Extract logical interfaces from the text. A logical interface is:
                - A connection point between components
                - Defines data/service exchange
                - Has protocols and formats
                
                For each interface, identify:
                - Interface name and type
                - Connected components
                - Exchanged data/services
                - Protocols and constraints
                """,
                
                "scenarios": """
                Extract logical scenarios from the text. A logical scenario is:
                - A sequence of component interactions
                - Realizes a system function or capability
                - Shows message/data flows
                
                For each scenario, identify:
                - Scenario name and objective
                - Participating components
                - Interaction sequence
                - Data/control flows
                """
            },
            
            "physical": {
                "components": """
                Extract physical components from the text. A physical component is:
                - A concrete implementation element
                - Hardware, software, or hybrid
                - Has specific deployment characteristics
                
                For each component, identify:
                - Component name and type
                - Implemented logical components
                - Technical specifications
                - Deployment constraints
                """,
                
                "functions": """
                Extract physical functions from the text. A physical function is:
                - A function as implemented in physical components
                - Has specific technology choices
                - Subject to implementation constraints
                
                For each function, identify:
                - Function name and implementation
                - Host physical component
                - Technology choices
                - Performance characteristics
                """,
                
                "constraints": """
                Extract implementation constraints from the text. A constraint is:
                - A limitation on physical implementation
                - Can be technical, regulatory, or business
                - Affects design decisions
                
                For each constraint, identify:
                - Constraint description and type
                - Affected components/functions
                - Rationale and impact
                - Compliance requirements
                """,
                
                "scenarios": """
                Extract physical scenarios from the text. A physical scenario is:
                - A sequence of physical component interactions
                - Shows actual deployment and execution
                - Includes performance and resource usage
                
                For each scenario, identify:
                - Scenario name and context
                - Physical components involved
                - Resource usage patterns
                - Performance characteristics
                """
            }
        }
    
    def extract_complete_analysis(self, 
                                context_chunks: List[Dict[str, Any]], 
                                proposal_text: str,
                                target_phases: List[str],
                                source_documents: List[str],
                                enable_cross_phase_analysis: bool = True) -> ARCADIAStructuredOutput:
        """
        Extract complete ARCADIA analysis for specified phases
        
        Args:
            context_chunks: Processed document chunks
            proposal_text: Original proposal text
            target_phases: List of phases to analyze ["operational", "system", "logical", "physical"]
            source_documents: List of source document names
            enable_cross_phase_analysis: Whether to perform cross-phase analysis
            
        Returns:
            Complete ARCADIA analysis results
        """
        
        self.logger.info(f"Starting complete ARCADIA analysis for phases: {target_phases}")
        start_time = datetime.now()
        
        # Initialize results
        results = ARCADIAStructuredOutput(
            generation_metadata={
                "source_documents": source_documents,
                "extraction_timestamp": start_time.isoformat(),
                "target_phases": target_phases
            }
        )
        
        # Extract each requested phase
        if "operational" in target_phases:
            self.logger.info("Extracting operational analysis")
            results.operational_analysis = self.extract_operational_analysis(context_chunks, proposal_text)
        
        if "system" in target_phases:
            self.logger.info("Extracting system analysis")
            results.system_analysis = self.extract_system_analysis(context_chunks, proposal_text)
        
        if "logical" in target_phases:
            self.logger.info("Extracting logical architecture")
            results.logical_architecture = self.extract_logical_architecture(context_chunks, proposal_text)
        
        if "physical" in target_phases:
            self.logger.info("Extracting physical architecture")
            results.physical_architecture = self.extract_physical_architecture(context_chunks, proposal_text)
        
        # Cross-phase analysis
        if enable_cross_phase_analysis and len(target_phases) > 1:
            self.logger.info("Performing cross-phase analysis")
            results.cross_phase_analysis = self.extract_cross_phase_analysis(results)
        
        # Calculate extraction statistics (stored in metadata)
        results.generation_metadata.update(self._calculate_extraction_statistics(results))
        
        extraction_time = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"ARCADIA analysis completed in {extraction_time:.1f} seconds")
        
        return results
    
    def extract_operational_analysis(self, context_chunks: List[Dict[str, Any]], proposal_text: str) -> OperationalAnalysisOutput:
        """Extract operational analysis phase"""
        self.logger.info("Extracting operational analysis (placeholder)")
        return OperationalAnalysisOutput()
    
    def extract_system_analysis(self, context_chunks: List[Dict[str, Any]], proposal_text: str) -> SystemAnalysisOutput:
        """Extract system analysis phase"""
        self.logger.info("Extracting system analysis (placeholder)")
        return SystemAnalysisOutput()
    
    def extract_logical_architecture(self, context_chunks: List[Dict[str, Any]], proposal_text: str) -> LogicalArchitectureOutput:
        """Extract logical architecture phase"""
        self.logger.info("Extracting logical architecture (placeholder)")
        return LogicalArchitectureOutput()
    
    def extract_physical_architecture(self, context_chunks: List[Dict[str, Any]], proposal_text: str) -> PhysicalArchitectureOutput:
        """Extract physical architecture phase"""
        self.logger.info("Extracting physical architecture (placeholder)")
        return PhysicalArchitectureOutput()
    
    def extract_cross_phase_analysis(self, results: ARCADIAStructuredOutput) -> CrossPhaseAnalysisOutput:
        """Extract cross-phase analysis"""
        self.logger.info("Extracting cross-phase analysis (placeholder)")
        return CrossPhaseAnalysisOutput()
    
    def _calculate_extraction_statistics(self, results: ARCADIAStructuredOutput) -> Dict[str, Any]:
        """Calculate extraction statistics"""
        return {
            "total_elements": 0,
            "phases_processed": len(results.generation_metadata.get("target_phases", [])),
            "extraction_time": "completed"
        } 