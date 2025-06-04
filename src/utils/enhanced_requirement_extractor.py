"""
Module d'extraction avancée de requirements avec analyse linguistique

Ce module fournit des capacités d'analyse avancée pour identifier:
- Les verbes d'obligation (shall, must, should)
- Les entités système
- Les conditions et contraintes
- Les métriques quantifiables
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logger
logger = logging.getLogger(__name__)

class ObligationLevel(Enum):
    """Niveaux d'obligation selon IEEE 830"""
    MANDATORY = "SHALL"      # Exigence obligatoire
    STRONG = "MUST"          # Exigence forte
    RECOMMENDED = "SHOULD"   # Exigence recommandée
    OPTIONAL = "MAY"         # Exigence optionnelle
    FUTURE = "WILL"          # Exigence future

@dataclass
class RequirementElement:
    """Structure pour un élément de requirement extrait"""
    text: str
    obligation_verb: str
    obligation_level: ObligationLevel
    system_entity: Optional[str]
    action: str
    conditions: List[str]
    constraints: List[str]
    metrics: List[Dict[str, any]]
    confidence_score: float

@dataclass
class MetricElement:
    """Structure pour une métrique quantifiable"""
    value: str
    unit: str
    operator: str  # >, <, >=, <=, =, etc.
    context: str
    metric_type: str  # performance, security, usability, etc.

class EnhancedRequirementExtractor:
    """Extracteur avancé de requirements avec analyse linguistique"""
    
    def __init__(self):
        """Initialise l'extracteur avec les patterns linguistiques"""
        # Patterns pour les verbes d'obligation
        self.obligation_patterns = {
            ObligationLevel.MANDATORY: [
                r'\bshall\b',
                r'\brequired to\b',
                r'\bmandatory\b',
                r'\bmust be\b'
            ],
            ObligationLevel.STRONG: [
                r'\bmust\b',
                r'\bneed to\b',
                r'\bhas to\b',
                r'\brequires\b'
            ],
            ObligationLevel.RECOMMENDED: [
                r'\bshould\b',
                r'\brecommended\b',
                r'\bpreferred\b',
                r'\bdesirable\b'
            ],
            ObligationLevel.OPTIONAL: [
                r'\bmay\b',
                r'\boptional\b',
                r'\bcan\b',
                r'\bmight\b'
            ],
            ObligationLevel.FUTURE: [
                r'\bwill\b',
                r'\bshall be\b',
                r'\bis to be\b'
            ]
        }
        
        # Patterns pour les entités système
        self.system_entity_patterns = [
            r'\b(?:the\s+)?system\b',
            r'\b(?:the\s+)?application\b',
            r'\b(?:the\s+)?software\b',
            r'\b(?:the\s+)?platform\b',
            r'\b(?:the\s+)?interface\b',
            r'\b(?:the\s+)?module\b',
            r'\b(?:the\s+)?component\b',
            r'\b(?:the\s+)?service\b',
            r'\b(?:the\s+)?database\b',
            r'\b(?:the\s+)?server\b',
            r'\b(?:the\s+)?client\b',
            r'\b(?:the\s+)?user interface\b',
            r'\b(?:the\s+)?API\b',
            r'\b(?:the\s+)?network\b',
            r'\b(?:the\s+)?security system\b',
            r'\b(?:the\s+)?monitoring system\b'
        ]
        
        # Patterns pour les conditions
        self.condition_patterns = [
            r'\bif\b.*?(?=shall|must|should|will)',
            r'\bwhen\b.*?(?=shall|must|should|will)',
            r'\bunless\b.*?(?=shall|must|should|will)',
            r'\bin case of\b.*?(?=shall|must|should|will)',
            r'\bupon\b.*?(?=shall|must|should|will)',
            r'\bduring\b.*?(?=shall|must|should|will)',
            r'\bwhile\b.*?(?=shall|must|should|will)'
        ]
        
        # Patterns pour les contraintes
        self.constraint_patterns = [
            r'\bwithin\s+\d+.*?(?:seconds?|minutes?|hours?|days?)\b',
            r'\bunder\s+(?:normal|stress|peak)\s+conditions\b',
            r'\bwith(?:out)?\s+(?:exceeding|compromising)\b.*?',
            r'\bsubject to\b.*?',
            r'\bin compliance with\b.*?',
            r'\baccording to\b.*?',
            r'\bas defined in\b.*?'
        ]
        
        # Patterns pour les métriques quantifiables
        self.metric_patterns = [
            # Performance metrics
            r'(?:response time|latency)\s*(?:of\s*)?(?:less than|<|≤|<=|under)\s*(\d+(?:\.\d+)?)\s*(ms|seconds?|minutes?)',
            r'(?:throughput|rate)\s*(?:of\s*)?(?:at least|>=|≥|>|above)\s*(\d+(?:\.\d+)?)\s*(requests?|transactions?|operations?)\s*per\s*(second|minute|hour)',
            r'(?:availability|uptime)\s*(?:of\s*)?(?:at least|>=|≥|>)\s*(\d+(?:\.\d+)?)\s*(%|percent)',
            r'(?:capacity|storage)\s*(?:of\s*)?(?:at least|>=|≥|>)\s*(\d+(?:\.\d+)?)\s*(GB|TB|MB|KB|bytes?)',
            
            # Security metrics
            r'(?:encryption)\s*(?:of\s*)?(?:at least|>=|≥|>)\s*(\d+)\s*(?:bit|bits)',
            r'(?:password|key)\s*(?:length|size)\s*(?:of\s*)?(?:at least|>=|≥|>)\s*(\d+)\s*(?:characters?|bits?)',
            
            # Quality metrics
            r'(?:accuracy|precision|recall)\s*(?:of\s*)?(?:at least|>=|≥|>)\s*(\d+(?:\.\d+)?)\s*(%|percent)',
            r'(?:error rate|failure rate)\s*(?:of\s*)?(?:less than|<|≤|<=|under)\s*(\d+(?:\.\d+)?)\s*(%|percent)',
            
            # Usability metrics
            r'(?:user\s*)?(?:satisfaction|rating)\s*(?:of\s*)?(?:at least|>=|≥|>)\s*(\d+(?:\.\d+)?)\s*(?:out of\s*(\d+)|/(\d+)|\s*stars?)',
            r'(?:learning\s*time|training\s*time)\s*(?:of\s*)?(?:less than|<|≤|<=|under)\s*(\d+(?:\.\d+)?)\s*(hours?|days?|weeks?)',
            
            # Business metrics
            r'(?:cost|price|budget)\s*(?:of\s*)?(?:less than|<|≤|<=|under)\s*(\$?\d+(?:,\d{3})*(?:\.\d+)?)\s*(\$|euros?|dollars?)?',
            r'(?:ROI|return)\s*(?:of\s*)?(?:at least|>=|≥|>)\s*(\d+(?:\.\d+)?)\s*(%|percent)'
        ]
    
    def extract_enhanced_requirements(self, text: str) -> List[RequirementElement]:
        """
        Extrait les requirements avec analyse linguistique avancée
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste des éléments de requirements extraits
        """
        logger.info(f"Starting enhanced requirement extraction from {len(text)} characters")
        
        # Préprocessing du texte
        sentences = self._split_into_sentences(text)
        logger.info(f"Split text into {len(sentences)} sentences")
        
        requirements = []
        
        for i, sentence in enumerate(sentences):
            # Analyser chaque phrase pour les patterns de requirements
            req_elements = self._analyze_sentence(sentence)
            
            for req in req_elements:
                req.text = sentence
                requirements.append(req)
        
        logger.info(f"Extracted {len(requirements)} requirement elements")
        return requirements
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divise le texte en phrases"""
        # Fallback basique sans spaCy
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _analyze_sentence(self, sentence: str) -> List[RequirementElement]:
        """Analyse une phrase pour extraire les éléments de requirements"""
        requirements = []
        
        # 1. Détecter les verbes d'obligation
        obligation_info = self._detect_obligation_verbs(sentence)
        
        if not obligation_info:
            return requirements  # Pas de verbe d'obligation trouvé
        
        obligation_verb, obligation_level = obligation_info
        
        # 2. Identifier les entités système
        system_entity = self._extract_system_entity(sentence)
        
        # 3. Extraire l'action principal
        action = self._extract_action(sentence, obligation_verb)
        
        # 4. Identifier les conditions
        conditions = self._extract_conditions(sentence)
        
        # 5. Identifier les contraintes
        constraints = self._extract_constraints(sentence)
        
        # 6. Extraire les métriques quantifiables
        metrics = self._extract_metrics(sentence)
        
        # 7. Calculer un score de confiance
        confidence = self._calculate_confidence(sentence, obligation_verb, system_entity, action, metrics)
        
        requirement = RequirementElement(
            text=sentence,
            obligation_verb=obligation_verb,
            obligation_level=obligation_level,
            system_entity=system_entity,
            action=action,
            conditions=conditions,
            constraints=constraints,
            metrics=metrics,
            confidence_score=confidence
        )
        
        requirements.append(requirement)
        return requirements
    
    def _detect_obligation_verbs(self, sentence: str) -> Optional[Tuple[str, ObligationLevel]]:
        """Détecte les verbes d'obligation dans une phrase"""
        sentence_lower = sentence.lower()
        
        for level, patterns in self.obligation_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, sentence_lower)
                if match:
                    return match.group(0), level
        
        return None
    
    def _extract_system_entity(self, sentence: str) -> Optional[str]:
        """Extrait l'entité système de la phrase"""
        sentence_lower = sentence.lower()
        
        for pattern in self.system_entity_patterns:
            match = re.search(pattern, sentence_lower, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_action(self, sentence: str, obligation_verb: str) -> str:
        """Extrait l'action principale de la requirement"""
        # Trouver le texte après le verbe d'obligation
        pattern = rf'{re.escape(obligation_verb)}\s+(.*?)(?:\.|$|if|when|unless|within|under|subject to)'
        match = re.search(pattern, sentence, re.IGNORECASE)
        
        if match:
            action = match.group(1).strip()
            # Nettoyer l'action
            action = re.sub(r'\s+', ' ', action)
            return action
        
        return ""
    
    def _extract_conditions(self, sentence: str) -> List[str]:
        """Extrait les conditions de la phrase"""
        conditions = []
        
        for pattern in self.condition_patterns:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                condition = match.group(0).strip()
                conditions.append(condition)
        
        return conditions
    
    def _extract_constraints(self, sentence: str) -> List[str]:
        """Extrait les contraintes de la phrase"""
        constraints = []
        
        for pattern in self.constraint_patterns:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                constraint = match.group(0).strip()
                constraints.append(constraint)
        
        return constraints
    
    def _extract_metrics(self, sentence: str) -> List[Dict[str, any]]:
        """Extrait les métriques quantifiables de la phrase"""
        metrics = []
        
        for pattern in self.metric_patterns:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                metric_data = {
                    "full_match": match.group(0),
                    "value": match.group(1) if match.lastindex >= 1 else None,
                    "unit": match.group(2) if match.lastindex >= 2 else None,
                    "context": self._get_metric_context(match.group(0)),
                    "position": match.span()
                }
                metrics.append(metric_data)
        
        return metrics
    
    def _get_metric_context(self, metric_text: str) -> str:
        """Détermine le contexte d'une métrique (performance, sécurité, etc.)"""
        metric_lower = metric_text.lower()
        
        if any(word in metric_lower for word in ['response', 'latency', 'throughput', 'performance']):
            return "performance"
        elif any(word in metric_lower for word in ['availability', 'uptime', 'reliability']):
            return "reliability"
        elif any(word in metric_lower for word in ['encryption', 'password', 'security']):
            return "security"
        elif any(word in metric_lower for word in ['accuracy', 'precision', 'error']):
            return "quality"
        elif any(word in metric_lower for word in ['satisfaction', 'usability', 'learning']):
            return "usability"
        elif any(word in metric_lower for word in ['cost', 'price', 'budget', 'roi']):
            return "business"
        else:
            return "general"
    
    def _calculate_confidence(self, sentence: str, obligation_verb: str, 
                            system_entity: Optional[str], action: str, 
                            metrics: List[Dict]) -> float:
        """Calcule un score de confiance pour l'extraction"""
        score = 0.0
        
        # Base score pour avoir un verbe d'obligation
        score += 0.3
        
        # Bonus pour entité système identifiée
        if system_entity:
            score += 0.2
        
        # Bonus pour action claire
        if action and len(action.split()) >= 2:
            score += 0.2
        
        # Bonus pour métriques quantifiables
        if metrics:
            score += 0.2 * min(len(metrics), 2)  # Max 0.4
        
        # Bonus pour structure de phrase complète
        if len(sentence.split()) >= 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def format_extracted_requirements(self, requirements: List[RequirementElement]) -> str:
        """Formate les requirements extraits pour affichage"""
        if not requirements:
            return "Aucun requirement extrait."
        
        output = "## Requirements Extraits avec Analyse Linguistique\n\n"
        
        for i, req in enumerate(requirements, 1):
            output += f"### Requirement {i}\n\n"
            output += f"**Texte:** {req.text}\n\n"
            output += f"**Niveau d'obligation:** {req.obligation_level.value} ({req.obligation_verb})\n\n"
            
            if req.system_entity:
                output += f"**Entité système:** {req.system_entity}\n\n"
            
            if req.action:
                output += f"**Action:** {req.action}\n\n"
            
            if req.conditions:
                output += f"**Conditions:** {', '.join(req.conditions)}\n\n"
            
            if req.constraints:
                output += f"**Contraintes:** {', '.join(req.constraints)}\n\n"
            
            if req.metrics:
                output += "**Métriques quantifiables:**\n"
                for metric in req.metrics:
                    output += f"- {metric['full_match']} (contexte: {metric['context']})\n"
                output += "\n"
            
            output += f"**Score de confiance:** {req.confidence_score:.2f}\n\n"
            output += "---\n\n"
        
        return output
    
    def get_statistics(self, requirements: List[RequirementElement]) -> Dict[str, any]:
        """Génère des statistiques sur les requirements extraits"""
        if not requirements:
            return {}
        
        # Compter par niveau d'obligation
        obligation_counts = {}
        for req in requirements:
            level = req.obligation_level.value
            obligation_counts[level] = obligation_counts.get(level, 0) + 1
        
        # Compter par contexte de métrique
        metric_contexts = {}
        for req in requirements:
            for metric in req.metrics:
                context = metric['context']
                metric_contexts[context] = metric_contexts.get(context, 0) + 1
        
        # Score de confiance moyen
        avg_confidence = sum(req.confidence_score for req in requirements) / len(requirements)
        
        # Requirements avec métriques
        reqs_with_metrics = sum(1 for req in requirements if req.metrics)
        
        return {
            "total_requirements": len(requirements),
            "obligation_distribution": obligation_counts,
            "metric_contexts": metric_contexts,
            "average_confidence": avg_confidence,
            "requirements_with_metrics": reqs_with_metrics,
            "metrics_percentage": (reqs_with_metrics / len(requirements)) * 100
        } 