from typing import List, Dict, Any, Optional
import re
from config import arcadia_config, requirements_templates
import logging

class RequirementsGenerator:
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client
        self.logger = logging.getLogger(__name__)
        self.requirement_counters = {
            "functional": 1,
            "non_functional": 1,
            "stakeholder": 1
        }
    
    def generate_stakeholders(self, context: List[Dict], proposal_text: str) -> Dict:
        """Generate stakeholder analysis from proposal"""
        template = requirements_templates.REQUIREMENT_TEMPLATES["stakeholder_template"]
        
        prompt = template["prompts"]["identification"].format(
            context=self._prepare_context_text(context)
        )
        
        response = self._call_ai_model(prompt, "requirements_generation")
        stakeholders = self._parse_stakeholder_response(response)
        
        return stakeholders
    
    def generate_functional_requirements(self, 
                                       context: List[Dict], 
                                       phase: str, 
                                       proposal_text: str) -> List[Dict]:
        """Generate functional requirements for specific ARCADIA phase"""
        template = requirements_templates.REQUIREMENT_TEMPLATES["functional_template"]
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        
        prompt = template["prompts"]["generation"].format(
            phase=phase,
            context=self._prepare_context_text(context),
            stakeholders=self._extract_stakeholders_from_context(context),
            phase_description=phase_info.get("description", ""),
            prefix="FR",
            phase_keywords=", ".join(phase_info.get("keywords", []))
        )
        
        response = self._call_ai_model(prompt, "requirements_generation")
        requirements = self._parse_requirements_response(response, "functional", phase)
        
        return requirements
    
    def generate_non_functional_requirements(self, 
                                           context: List[Dict], 
                                           phase: str, 
                                           proposal_text: str) -> List[Dict]:
        """Generate non-functional requirements for specific ARCADIA phase"""
        template = requirements_templates.REQUIREMENT_TEMPLATES["non_functional_template"]
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        
        # Generate for each NFR category
        all_nf_requirements = []
        nfr_categories = arcadia_config.REQUIREMENT_CATEGORIES["non_functional"]["subcategories"]
        
        for category, prefix in nfr_categories.items():
            prompt = template["prompts"]["generation"].format(
                phase=phase,
                context=self._prepare_context_text(context),
                category=category,
                phase_keywords=", ".join(phase_info.get("keywords", []))
            )
            
            response = self._call_ai_model(prompt, "requirements_generation")
            reqs = self._parse_requirements_response(response, "non_functional", phase, category)
            all_nf_requirements.extend(reqs)
        
        return all_nf_requirements
    
    def _call_ai_model(self, prompt: str, model_type: str) -> str:
        """Call appropriate AI model based on task type"""
        from config import config
        
        model_config = config.AI_MODELS.get(model_type, config.AI_MODELS["requirements_generation"])
        
        try:
            response = self.ollama_client.generate(
                model=model_config["model"],
                prompt=prompt,
                stream=False,
                options={
                    "temperature": model_config["temperature"],
                    "num_predict": model_config["max_tokens"]
                }
            )
            return response['response']
        except Exception as e:
            self.logger.error(f"Error calling AI model: {e}")
            return ""
    
    def _prepare_context_text(self, context: List[Dict]) -> str:
        """Prepare context chunks for AI prompt"""
        return "\n\n".join([chunk["content"] for chunk in context[:5]])  # Limit to 5 chunks
    
    def _extract_stakeholders_from_context(self, context: List[Dict]) -> str:
        """Extract stakeholder mentions from context"""
        stakeholder_patterns = [
            r"stakeholder[s]?",
            r"user[s]?",
            r"actor[s]?",
            r"team[s]?",
            r"organization[s]?",
            r"SOC[s]?",
            r"analyst[s]?"
        ]
        
        stakeholders = set()
        for chunk in context:
            content = chunk["content"].lower()
            for pattern in stakeholder_patterns:
                matches = re.findall(rf"\b\w*{pattern}\w*\b", content)
                stakeholders.update(matches)
        
        return ", ".join(list(stakeholders)[:10])  # Limit to 10 stakeholders
    
    def _parse_stakeholder_response(self, response: str) -> Dict:
        """Parse AI response to extract structured stakeholder data"""
        stakeholders = {}
        
        # Simple parsing logic - in production, use more sophisticated NLP
        lines = response.split('\n')
        current_stakeholder = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') and ':' in line:
                # New stakeholder: "- Name: Description"
                parts = line[1:].split(':', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    description = parts[1].strip()
                    
                    stakeholder_id = f"STK-{self.requirement_counters['stakeholder']:03d}"
                    self.requirement_counters['stakeholder'] += 1
                    
                    stakeholders[stakeholder_id] = {
                        "id": stakeholder_id,
                        "name": name,
                        "role": description,
                        "interests": [],
                        "influence": "Medium",
                        "phase": "operational"
                    }
                    current_stakeholder = stakeholder_id
        
        return stakeholders
    
    def _parse_requirements_response(self, 
                                   response: str, 
                                   req_type: str, 
                                   phase: str, 
                                   category: str = None) -> List[Dict]:
        """Parse AI response to extract structured requirements"""
        requirements = []
        
        # Extract requirements using patterns
        req_patterns = [
            r"(?:FR|NFR|FUNC|NFUNC)-[\w-]+-\d+",  # Existing ID format
            r"The system shall ([^.]+)",           # Requirement text
            r"Priority:\s*(MUST|SHOULD|COULD)",    # Priority
            r"Verification:\s*([^.\n]+)"           # Verification method
        ]
        
        lines = response.split('\n')
        current_req = None
        
        for line in lines:
            line = line.strip()
            
            # Check for "The system shall" requirements
            shall_match = re.search(r"[Tt]he system shall ([^.]+)", line)
            if shall_match:
                requirement_text = shall_match.group(1).strip()
                
                # Generate requirement ID
                if req_type == "functional":
                    req_id = f"FR-{phase.upper()[:3]}-{self.requirement_counters['functional']:03d}"
                    self.requirement_counters['functional'] += 1
                else:
                    cat_prefix = category.upper()[:4] if category else "NFR"
                    req_id = f"NFR-{cat_prefix}-{self.requirement_counters['non_functional']:03d}"
                    self.requirement_counters['non_functional'] += 1
                
                # Extract priority from same line or context
                priority = "SHOULD"  # Default
                priority_match = re.search(r"Priority:\s*(MUST|SHOULD|COULD)", line)
                if priority_match:
                    priority = priority_match.group(1)
                
                # Extract verification method
                verification = "Review and testing"  # Default
                verification_match = re.search(r"Verification:\s*([^.\n]+)", line)
                if verification_match:
                    verification = verification_match.group(1).strip()
                
                requirement = {
                    "id": req_id,
                    "type": req_type.title(),
                    "title": f"{requirement_text[:50]}..." if len(requirement_text) > 50 else requirement_text,
                    "description": f"The system shall {requirement_text}",
                    "priority": priority,
                    "phase": phase,
                    "verification_method": verification,
                    "dependencies": [],
                    "rationale": f"Generated from {phase} phase analysis"
                }
                
                if req_type == "non_functional" and category:
                    requirement["category"] = category
                    requirement["metric"] = "TBD"
                    requirement["target_value"] = "TBD"
                
                requirements.append(requirement)
        
        return requirements

    def validate_requirements(self, requirements: List[Dict]) -> Dict:
        """Validate generated requirements for quality and completeness"""
        validation_results = {
            "valid_requirements": [],
            "invalid_requirements": [],
            "warnings": [],
            "quality_score": 0.0
        }
        
        for req in requirements:
            issues = []
            
            # Check mandatory fields
            if not req.get("id"):
                issues.append("Missing requirement ID")
            if not req.get("description"):
                issues.append("Missing requirement description")
            if not req.get("priority") or req["priority"] not in ["MUST", "SHOULD", "COULD"]:
                issues.append("Invalid or missing priority")
            
            # Check requirement quality
            description = req.get("description", "")
            if not re.search(r"\bshall\b", description, re.IGNORECASE):
                issues.append("Requirement should use 'shall' for mandatory statements")
            
            if len(description.split()) < 5:
                issues.append("Requirement description too short")
            
            if issues:
                req["validation_issues"] = issues
                validation_results["invalid_requirements"].append(req)
            else:
                validation_results["valid_requirements"].append(req)
        
        # Calculate quality score
        total_reqs = len(requirements)
        valid_reqs = len(validation_results["valid_requirements"])
        validation_results["quality_score"] = (valid_reqs / total_reqs) * 100 if total_reqs > 0 else 0
        
        return validation_results