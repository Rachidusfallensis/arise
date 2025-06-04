import os
import json
import xml.etree.ElementTree as ET
from typing import List, Dict
import PyPDF2
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup
from config import config, arcadia_config
import re

class ArcadiaDocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process_project_proposal(self, proposal_text: str) -> Dict:
        """Process project proposal and extract MBSE-relevant information"""
        proposal_analysis = {
            "objectives": self._extract_objectives(proposal_text),
            "stakeholders": self._extract_stakeholders(proposal_text),
            "work_packages": self._extract_work_packages(proposal_text),
            "technical_components": self._extract_technical_components(proposal_text),
            "requirements_indicators": self._extract_requirement_indicators(proposal_text),
            "arcadia_mapping": self._map_to_arcadia_phases(proposal_text)
        }
        
        return proposal_analysis
    
    def _extract_objectives(self, text: str) -> List[Dict]:
        """Extract project objectives from proposal text"""
        objectives = []
        
        # Look for numbered objectives or bullet points
        objective_patterns = [
            r"(?:Objective|Goal|Aim)\s*(\d+)[:\.]?\s*([^.\n]+)",
            r"(\d+)\.\s*([A-Z][^.\n]+)",
            r"[•\-]\s*([A-Z][^.\n]+)"
        ]
        
        for pattern in objective_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:
                    obj_id, description = match.groups()
                    objectives.append({
                        "id": f"OBJ-{len(objectives)+1:02d}",
                        "number": obj_id if obj_id.isdigit() else str(len(objectives)+1),
                        "description": description.strip(),
                        "arcadia_phase": self._classify_objective_phase(description)
                    })
                else:
                    description = match.group(1)
                    objectives.append({
                        "id": f"OBJ-{len(objectives)+1:02d}",
                        "number": str(len(objectives)+1),
                        "description": description.strip(),
                        "arcadia_phase": self._classify_objective_phase(description)
                    })
        
        return objectives
    
    def _extract_stakeholders(self, text: str) -> List[Dict]:
        """Extract stakeholders from proposal text"""
        stakeholders = []
        
        # Common stakeholder patterns
        stakeholder_patterns = [
            r"(?:stakeholder|actor|user|team|organization)[s]?[:\s]*([^.\n]+)",
            r"SOC[s]?\s+([^.\n]+)",
            r"(?:analyst|engineer|manager|operator)[s]?\s+([^.\n]*)",
            r"(?:consortium|partner)[s]?\s*[:\s]*([^.\n]+)"
        ]
        
        for pattern in stakeholder_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                description = match.group(1).strip()
                if len(description) > 5:  # Filter out very short matches
                    stakeholders.append({
                        "id": f"STK-{len(stakeholders)+1:02d}",
                        "description": description,
                        "type": self._classify_stakeholder_type(description),
                        "phase": "operational"  # Most stakeholders are relevant to operational phase
                    })
        
        return stakeholders
    
    def _extract_work_packages(self, text: str) -> List[Dict]:
        """Extract work packages and map them to ARCADIA phases"""
        work_packages = []
        
        # Look for WP patterns
        wp_pattern = r"(?:WP|Work Package)\s*(\d+)[:\.]?\s*([^.\n]+)"
        matches = re.finditer(wp_pattern, text, re.IGNORECASE)
        
        for match in matches:
            wp_number, wp_description = match.groups()
            work_packages.append({
                "id": f"WP{wp_number}",
                "number": wp_number,
                "description": wp_description.strip(),
                "arcadia_phase": self._map_wp_to_arcadia_phase(wp_description),
                "requirements_potential": self._assess_requirements_potential(wp_description)
            })
        
        return work_packages
    
    def _extract_technical_components(self, text: str) -> List[Dict]:
        """Extract technical components and systems"""
        components = []
        
        # Technical component patterns
        component_patterns = [
            r"(?:component|module|system|platform|service)\s*[:\-]?\s*([^.\n]+)",
            r"(?:AI|ML|algorithm|model)\s+([^.\n]+)",
            r"(?:interface|API|protocol)\s+([^.\n]+)"
        ]
        
        for pattern in component_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                description = match.group(1).strip()
                if len(description) > 10:
                    components.append({
                        "id": f"COMP-{len(components)+1:02d}",
                        "description": description,
                        "type": self._classify_component_type(description),
                        "arcadia_phase": self._classify_component_phase(description)
                    })
        
        return components
    
    def _extract_requirement_indicators(self, text: str) -> List[Dict]:
        """Extract potential requirement indicators from text"""
        indicators = []
        
        # Requirement indicator patterns
        requirement_patterns = [
            r"(?:shall|must|will|should|need[s]? to)\s+([^.\n]+)",
            r"(?:requirement|constraint|specification)[s]?\s*[:\-]?\s*([^.\n]+)",
            r"(?:performance|security|usability|reliability)\s+([^.\n]+)"
        ]
        
        for pattern in requirement_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                description = match.group(1).strip()
                if len(description) > 5:
                    indicators.append({
                        "id": f"REQ-IND-{len(indicators)+1:02d}",
                        "text": f"{match.group(0)}",
                        "description": description,
                        "type": self._classify_requirement_type(match.group(0)),
                        "priority": self._estimate_priority(match.group(0))
                    })
        
        return indicators
    
    def _map_to_arcadia_phases(self, text: str) -> Dict:
        """Map content to ARCADIA phases based on keyword analysis"""
        phase_mapping = {}
        
        for phase, phase_info in arcadia_config.ARCADIA_PHASES.items():
            keywords = phase_info.get("keywords", [])
            relevance_score = 0
            found_keywords = []
            
            for keyword in keywords:
                pattern = rf"\b{re.escape(keyword)}\b"
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                if matches > 0:
                    relevance_score += matches
                    found_keywords.append(keyword)
            
            phase_mapping[phase] = {
                "relevance_score": relevance_score,
                "found_keywords": found_keywords,
                "percentage": (relevance_score / len(keywords)) * 100 if keywords else 0
            }
        
        return phase_mapping
    
    def _classify_objective_phase(self, description: str) -> str:
        """Classify objective into ARCADIA phase"""
        description_lower = description.lower()
        
        # Phase classification based on keywords
        if any(word in description_lower for word in ["stakeholder", "user", "actor", "mission", "goal"]):
            return "operational"
        elif any(word in description_lower for word in ["function", "requirement", "interface", "system"]):
            return "system"
        elif any(word in description_lower for word in ["component", "logical", "behavior", "interaction"]):
            return "logical"
        elif any(word in description_lower for word in ["implementation", "deployment", "physical", "hardware"]):
            return "physical"
        else:
            return "system"  # Default
    
    def _classify_stakeholder_type(self, description: str) -> str:
        """Classify stakeholder type"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["soc", "analyst", "security"]):
            return "technical_user"
        elif any(word in description_lower for word in ["manager", "director", "admin"]):
            return "management"
        elif any(word in description_lower for word in ["developer", "engineer", "team"]):
            return "technical_team"
        else:
            return "general_user"
    
    def _map_wp_to_arcadia_phase(self, description: str) -> str:
        """Map work package to ARCADIA phase"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["stakeholder", "analysis", "requirement", "elicitation"]):
            return "operational"
        elif any(word in description_lower for word in ["architecture", "design", "component"]):
            return "logical"
        elif any(word in description_lower for word in ["implementation", "deployment", "pilot"]):
            return "physical"
        else:
            return "system"
    
    def _assess_requirements_potential(self, description: str) -> str:
        """Assess how much requirements can be derived from WP"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["requirement", "specification", "analysis"]):
            return "high"
        elif any(word in description_lower for word in ["design", "architecture", "component"]):
            return "medium"
        else:
            return "low"
    
    def _classify_component_type(self, description: str) -> str:
        """Classify technical component type"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["ai", "ml", "algorithm", "model"]):
            return "ai_component"
        elif any(word in description_lower for word in ["interface", "api", "protocol"]):
            return "interface"
        elif any(word in description_lower for word in ["data", "database", "storage"]):
            return "data_component"
        else:
            return "system_component"
    
    def _classify_component_phase(self, description: str) -> str:
        """Classify component into ARCADIA phase"""
        return self._classify_objective_phase(description)  # Same logic
    
    def _classify_requirement_type(self, text: str) -> str:
        """Classify requirement type from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["shall", "must", "will"]):
            return "functional"
        elif any(word in text_lower for word in ["performance", "security", "usability", "reliability"]):
            return "non_functional"
        else:
            return "general"
    
    def _estimate_priority(self, text: str) -> str:
        """Estimate requirement priority from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["must", "critical", "essential"]):
            return "MUST"
        elif any(word in text_lower for word in ["should", "important"]):
            return "SHOULD"
        else:
            return "COULD"
    
    def _chunk_text_with_metadata(self, text: str, metadata: Dict) -> List[Dict]:
        """Chunk text and add metadata"""
        chunks = []
        text_chunks = self.text_splitter.split_text(text)
        
        for i, chunk in enumerate(text_chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": i,
                "total_chunks": len(text_chunks),
                "arcadia_phase": self._detect_arcadia_phase(chunk)
            })
            
            chunks.append({
                "content": chunk,
                "metadata": chunk_metadata
            })
        
        return chunks
    
    def _detect_arcadia_phase(self, content: str) -> str:
        """Detect ARCADIA phase from content"""
        content_lower = content.lower()
        phase_scores = {}
        
        for phase, phase_info in arcadia_config.ARCADIA_PHASES.items():
            keywords = phase_info.get("keywords", [])
            score = sum(1 for keyword in keywords if keyword in content_lower)
            phase_scores[phase] = score
        
        # Return phase with highest score
        if phase_scores:
            return max(phase_scores, key=phase_scores.get)
        return "system"  # Default