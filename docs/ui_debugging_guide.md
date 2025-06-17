# 🐛 Guide de Débogage - Interface UI & Système Enhanced

## Issues Identifiées et Corrigées

### **Problème 1 : Erreur de formatage dans System Analysis**
**Symptôme :** `Error in system analysis: Invalid format specifier ' 1, "function": "alt function"' for object of type 'str'`

**Cause :** Accolades mal échappées dans le template JSON de `_extract_functional_chains`

**Solution :** ✅ Corrigé - Double échappement des accolades dans `src/core/system_analysis_extractor.py:422`

### **Problème 2 : Requirements non affichés dans l'UI**
**Symptôme :** Interface montre 0 requirements générés, même si la génération semble réussie

**Cause :** Le système enhanced retournait une structure différente de celle attendue par l'UI

**Solution :** ✅ Corrigé - Modification de `_combine_traditional_and_structured_results` pour exposer les requirements traditionnels au niveau supérieur

### **Problème 3 : Méthode manquante**
**Symptôme :** `_extract_proposal_context` method not found

**Cause :** Méthode non implémentée dans `EnhancedStructuredRAGSystem`

**Solution :** ✅ Corrigé - Ajout de la méthode avec chunking automatique du texte de proposition

### **Problème 4 : Gestion d'erreur insuffisante**
**Symptôme :** Erreurs dans l'analyse structurée empêchent l'affichage des requirements traditionnels

**Cause :** Gestion d'erreur non robuste

**Solution :** ✅ Corrigé - Amélioration de la gestion d'erreur avec fallback gracieux

## Tests de Validation

### Exécuter le Script de Test
```bash
# Test complet du système enhanced
python test_enhanced_system_ui.py
```

### Vérifications Manuelles dans l'UI

#### 1. **Test de Génération Basique**
- [ ] Ouvrir l'interface Streamlit
- [ ] Charger un exemple ou coller du texte
- [ ] Activer "Structured ARCADIA Analysis" 
- [ ] Cliquer "Generate Requirements"
- [ ] Vérifier que des requirements s'affichent

#### 2. **Test des Métriques**
- [ ] Vérifier que "Total Requirements" > 0
- [ ] Vérifier que "Phases Covered" > 0
- [ ] Vérifier que le graphique des priorités s'affiche

#### 3. **Test des Onglets**
- [ ] Onglet "Generate Requirements" : Requirements visibles
- [ ] Onglet "Structured ARCADIA Analysis" : Analyse structurée si activée
- [ ] Exports disponibles avec nouveaux formats ARCADIA

#### 4. **Test de Fallback**
- [ ] Désactiver "Structured ARCADIA Analysis"
- [ ] Générer des requirements
- [ ] Vérifier que les requirements traditionnels fonctionnent toujours

## Debugging des Logs

### Logs Importants à Surveiller
```bash
# Dans les logs, chercher ces indicateurs de succès :
grep "Enhanced generation completed" logs/requirements_generation.log
grep "Traditional requirements:" logs/requirements_generation.log
grep "Enhanced system initialized" logs/requirements_generation.log
```

### Logs d'Erreur Typiques
```bash
# Erreurs à surveiller :
grep "Error in structured analysis" logs/requirements_generation.log
grep "Invalid format specifier" logs/requirements_generation.log
grep "Error extracting" logs/requirements_generation.log
```

## Structure des Résultats Enhanced

### Format Attendu par l'UI
```json
{
  "requirements": {
    "operational": {
      "functional": [...],
      "non_functional": [...]
    }
  },
  "statistics": {
    "total_requirements": 10,
    "by_priority": {"MUST": 3, "SHOULD": 5, "COULD": 2}
  },
  "stakeholders": {...},
  "traditional_requirements": {...},
  "structured_analysis": {...},
  "enhancement_summary": {...}
}
```

### Vérification de la Structure
```python
# Dans Python/IPython :
results = rag_system.generate_enhanced_requirements_from_proposal(...)
print("Has requirements:", 'requirements' in results)
print("Has statistics:", 'statistics' in results)  
print("Total reqs:", results.get('statistics', {}).get('total_requirements', 0))
```

## Solutions aux Problèmes Courants

### **UI ne montre aucun requirement**
1. Vérifier les logs pour erreurs de génération
2. Tester le script de validation : `python test_enhanced_system_ui.py`
3. Vérifier que `'requirements'` existe dans les résultats
4. Essayer avec analyse structurée désactivée

### **Erreurs de formatage LLM**
1. Vérifier la connectivité au serveur Ollama
2. Tester avec un texte de proposition plus simple
3. Vérifier les templates JSON dans les extracteurs

### **Performance lente**
1. Réduire le nombre de phases analysées
2. Désactiver l'analyse cross-phase
3. Vérifier la charge du serveur Ollama

### **Exports ne fonctionnent pas**
1. Vérifier que `enhanced_results` est disponible dans la session
2. Tester les exports ARCADIA séparément
3. Utiliser les exports traditionnels comme fallback

## Commandes de Debug Rapide

```bash
# Redémarrer l'interface proprement
streamlit run ui/app.py --server.port 8501

# Tester le système sans interface
python -c "
from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem
system = EnhancedStructuredRAGSystem()
print('✅ System initialized')
"

# Vérifier les dépendances
python -c "
import streamlit as st
import pandas as pd
import plotly.express as px
print('✅ UI dependencies OK')
"
```

## Contact de Support

Si les problèmes persistent après ces vérifications :

1. **Collecter les informations :**
   - Logs complets de `logs/requirements_generation.log`
   - Résultat du script de test
   - Version de Python et dépendances

2. **Informations système :**
   - OS et version
   - Version Ollama et modèles disponibles
   - Mémoire disponible

3. **Étapes de reproduction :**
   - Texte de proposition utilisé
   - Paramètres sélectionnés
   - Erreur exacte observée 