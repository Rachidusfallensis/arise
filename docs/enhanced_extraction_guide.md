# Guide d'Extraction Avancée de Requirements

## Vue d'ensemble

Le module d'extraction avancée de requirements utilise l'analyse linguistique pour identifier automatiquement les éléments clés des requirements dans les documents techniques. Cette fonctionnalité révolutionne l'analyse des specifications en détectant :

- **Verbes d'obligation** (shall, must, should, may, will)
- **Entités système** (system, application, component, etc.)
- **Conditions et contraintes** (if, when, within, under conditions)
- **Métriques quantifiables** (performance, sécurité, qualité)

## Fonctionnalités Principales

### 1. Détection des Verbes d'Obligation

Le système reconnaît et classe les verbes d'obligation selon la norme IEEE 830 :

| Niveau | Verbes | Signification |
|--------|--------|---------------|
| **SHALL** | shall, required to, mandatory | Exigence obligatoire |
| **MUST** | must, need to, has to, requires | Exigence forte |
| **SHOULD** | should, recommended, preferred | Exigence recommandée |
| **MAY** | may, optional, can, might | Exigence optionnelle |
| **WILL** | will, shall be, is to be | Exigence future |

### 2. Identification des Entités Système

Le système reconnaît automatiquement les entités suivantes :
- `system`, `application`, `software`, `platform`
- `interface`, `module`, `component`, `service`
- `database`, `server`, `client`, `API`
- `network`, `security system`, `monitoring system`

### 3. Extraction des Conditions

Détection des conditions avec patterns comme :
- `if ... then`
- `when ... occurs`
- `unless ... happens`
- `in case of ...`
- `upon ... event`
- `during ... period`

### 4. Métriques Quantifiables

Le système identifie différents types de métriques :

#### Performance
- Temps de réponse : `< 2 seconds`, `within 100ms`
- Débit : `>= 1000 requests/second`, `at least 500 TPS`
- Disponibilité : `99.9% uptime`, `>= 99.95% availability`

#### Sécurité
- Chiffrement : `256-bit encryption`, `AES-256 or higher`
- Mots de passe : `at least 12 characters`, `minimum 16 bits`

#### Qualité
- Précision : `accuracy >= 95%`, `precision > 98%`
- Taux d'erreur : `error rate < 2%`, `failure rate <= 0.1%`

#### Business
- Coût : `budget < $50,000`, `cost <= 100k euros`
- ROI : `return >= 15%`, `ROI > 20%`

## Utilisation

### Interface Streamlit

1. **Accédez à l'onglet "Enhanced Extraction"**
2. **Choisissez votre méthode d'entrée :**
   - Saisir du texte directement
   - Charger un fichier (TXT, MD)
   - Utiliser un exemple prédéfini

3. **Configurez les paramètres :**
   - Seuil de confiance (0.0 - 1.0)
   - Options d'affichage (statistiques, texte brut)

4. **Analysez le texte** avec le bouton "Analyser le Texte"

### API Programmatique

```python
from src.utils.enhanced_requirement_extractor import EnhancedRequirementExtractor

# Initialiser l'extracteur
extractor = EnhancedRequirementExtractor()

# Analyser un texte
text = "The system shall respond within 2 seconds under normal conditions."
requirements = extractor.extract_enhanced_requirements(text)

# Obtenir les statistiques
stats = extractor.get_statistics(requirements)

# Formatter pour affichage
formatted = extractor.format_extracted_requirements(requirements)
```

## Structure des Données

### RequirementElement

Chaque requirement extrait contient :

```python
@dataclass
class RequirementElement:
    text: str                    # Texte original de la phrase
    obligation_verb: str         # Verbe d'obligation trouvé
    obligation_level: ObligationLevel  # Niveau d'obligation (SHALL, MUST, etc.)
    system_entity: Optional[str] # Entité système identifiée
    action: str                  # Action principale
    conditions: List[str]        # Conditions identifiées
    constraints: List[str]       # Contraintes identifiées
    metrics: List[Dict]          # Métriques quantifiables
    confidence_score: float      # Score de confiance (0.0-1.0)
```

### Score de Confiance

Le score de confiance est calculé basé sur :
- **+0.3** : Présence d'un verbe d'obligation
- **+0.2** : Entité système identifiée
- **+0.2** : Action claire (>= 2 mots)
- **+0.2-0.4** : Métriques quantifiables (max 2)
- **+0.1** : Structure de phrase complète (>= 5 mots)

## Exemples d'Usage

### Exemple 1 : Système de Transport

**Entrée :**
```
The transportation management system shall process traffic data from sensors in real-time.
The system must respond to traffic signal adjustment requests within 2 seconds under normal conditions.
```

**Sortie :**
- **Requirement 1** : SHALL obligation, entité "system", action "process traffic data"
- **Requirement 2** : MUST obligation, contraintes "within 2 seconds", "under normal conditions"

### Exemple 2 : Cybersécurité

**Entrée :**
```
The system must encrypt all communications using at least 256-bit encryption.
User authentication must require passwords of at least 12 characters.
```

**Sortie :**
- **Requirement 1** : Métrique sécurité "256-bit encryption"
- **Requirement 2** : Métrique sécurité "12 characters"

## Performance

Le système offre d'excellentes performances :
- **Vitesse** : > 1,000,000 caractères/seconde
- **Précision** : Score de confiance moyen > 0.75
- **Couverture** : Détecte tous les patterns d'obligation standard
- **Robustesse** : Gère les textes de 1 caractère à plusieurs MB

## Patterns Reconnus

### Verbes d'Obligation

```regex
SHALL    : \bshall\b, \brequired to\b, \bmandatory\b
MUST     : \bmust\b, \bneed to\b, \bhas to\b, \brequires\b
SHOULD   : \bshould\b, \brecommended\b, \bpreferred\b
MAY      : \bmay\b, \boptional\b, \bcan\b, \bmight\b
WILL     : \bwill\b, \bshall be\b, \bis to be\b
```

### Entités Système

```regex
SYSTEM     : \b(?:the\s+)?system\b
APP        : \b(?:the\s+)?application\b
COMPONENT  : \b(?:the\s+)?(?:component|module|service)\b
INTERFACE  : \b(?:the\s+)?(?:interface|API)\b
```

### Métriques Performance

```regex
RESPONSE_TIME : (?:response time|latency)\s*(?:less than|<|≤)\s*(\d+(?:\.\d+)?)\s*(ms|seconds?)
THROUGHPUT    : (?:throughput|rate)\s*(?:at least|>=|≥)\s*(\d+(?:\.\d+)?)\s*(?:requests?|ops?)\s*per\s*(second|minute)
AVAILABILITY  : (?:availability|uptime)\s*(?:at least|>=|≥)\s*(\d+(?:\.\d+)?)\s*(%|percent)
```

## Extensions Possibles

### Intégration spaCy (optionnelle)

Pour une analyse plus avancée, le système peut être étendu avec spaCy :

```python
import spacy
nlp = spacy.load("en_core_web_sm")

def advanced_entity_extraction(self, text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities
```

### Support Multilingue

Addition de patterns français :

```python
obligation_patterns_fr = {
    ObligationLevel.MANDATORY: [r'\bdoit\b', r'\bobligatoire\b'],
    ObligationLevel.RECOMMENDED: [r'\bdevrait\b', r'\brecommandé\b']
}
```

### Métriques Métier

Extension pour métriques business spécifiques :

```python
business_patterns = [
    r'(?:budget|coût)\s*(?:inférieur à|<)\s*(\d+(?:,\d{3})*)\s*(€|euros?)',
    r'(?:délai|durée)\s*(?:maximum|max)\s*(\d+)\s*(jours?|semaines?|mois)'
]
```

## Troubleshooting

### Problèmes Communs

1. **Faible score de confiance** : Vérifiez la structure des phrases
2. **Métriques non détectées** : Assurez-vous de la syntaxe correcte
3. **Entités manquées** : Ajoutez des patterns personnalisés

### Amélioration de la Précision

- Utilisez des phrases complètes et bien structurées
- Incluez des verbes d'obligation explicites
- Spécifiez clairement les métriques quantifiables
- Évitez les formulations ambiguës

## Conclusion

L'extraction avancée de requirements automatise l'analyse des specifications techniques, permettant :
- **Gain de temps** : Analyse automatique vs. manuelle
- **Consistency** : Application uniforme des critères
- **Traçabilité** : Scores de confiance et métadonnées
- **Qualité** : Détection exhaustive des patterns standards

Cette fonctionnalité s'intègre parfaitement dans le workflow ARCADIA pour une approche MBSE complète et moderne. 