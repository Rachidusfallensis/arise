# Guide - Gestion de Projets Intégrée dans ARISE

## 🎯 Vue d'ensemble

ARISE dispose maintenant d'une **gestion complète des projets MBSE** intégrée directement dans l'interface principale. Cette fonctionnalité permet de :

- 🗂️ **Gérer plusieurs projets MBSE** simultanément
- 📄 **Upload et déduplication** intelligente des documents
- 🔍 **Recherche vectorielle** scopée par projet
- 📊 **Statistiques et métriques** détaillées
- 💾 **Persistance complète** des données entre les sessions
- 📤 **Export d'analyses ARCADIA** complètes

## 🚀 Comment accéder aux nouvelles fonctionnalités

### 1. Lancement de l'application
```bash
streamlit run ui/app.py
```

### 2. Interface intégrée
L'application dispose maintenant de **4 onglets principaux** :

- 🗂️ **Project Management** - Gestion complète des projets (avec génération de requirements intégrée)
- 🏗️ **ARCADIA Analysis** - Analyse structurée ARCADIA
- 💬 **Document Chat** - Chat avec les documents
- 📊 **Quality Evaluation** - Évaluation de la qualité

## 🗂️ Onglet Project Management

### Sidebar de gestion des projets
La **sidebar gauche** contient maintenant :

#### ➕ Création de nouveaux projets
```
📝 Nom du projet : "Smart Transportation System"
📄 Description : "Système de transport intelligent..."  
📋 Texte de proposition : "Développement d'un système..."
```

#### 📂 Sélection de projets existants
- Liste des projets avec nombre de documents
- Sélection rapide via selectbox
- Informations détaillées du projet actuel

#### ℹ️ Informations du projet
- ID unique du projet
- Dates de création/modification
- Statistiques (documents, requirements)
- Description complète

### Dashboard principal
L'onglet **Project Management** offre 4 sections :

#### 📄 Documents
- **Upload de nouveaux documents** (PDF, TXT, MD, DOCX)
- **Détection automatique des doublons** via hash SHA-256
- **Traitement et chunking** automatique
- **Liste des documents traités** avec statuts
- **Filtres et tri** par statut, date, nom, taille

#### 📝 Requirements ⭐ NOUVEAU !
L'onglet Requirements dispose maintenant de **2 sous-onglets** :

##### 📝 Requirements Générés
- **Affichage des requirements générés** par phase et type
- **Statistiques** : total requirements par phase
- **Navigation** par phases ARCADIA
- **Aperçu rapide** des requirements sauvegardés

##### 🚀 Générer Requirements ⭐ INTÉGRÉ !
- **Configuration ARCADIA** : phases, types de requirements
- **Options avancées** : qualité, vérification, analyse structurée
- **Génération basée sur les documents du projet** automatiquement
- **Sauvegarde automatique** dans le projet sélectionné
- **Affichage des résultats** avec statistiques
- **Validation** : vérification des documents avant génération

#### 🔍 Recherche
- **Recherche vectorielle** dans les documents du projet
- **Nombre de résultats configurable** (1-20)
- **Affichage des résultats** avec scores de similarité
- **Métadonnées** des documents sources

#### ⚙️ Paramètres
- **Informations détaillées** du projet (JSON)
- **Actions de maintenance** (nettoyage, diagnostic)
- **Type de système** utilisé (Enhanced/Simple)
- **Statistiques avancées**

## 🔄 Workflow de travail

### Étape 1 : Création d'un projet
1. **Ouvrir la sidebar** et aller dans "➕ Nouveau Projet"
2. **Remplir le formulaire** :
   - Nom du projet
   - Description (optionnelle)
   - Texte de proposition initiale (optionnel)
3. **Cliquer "Créer le projet"**
4. ✅ Le projet est créé et automatiquement sélectionné

### Étape 2 : Ajout de documents
1. **Aller dans l'onglet "Project Management"**
2. **Section "Documents"** → "📤 Ajouter des documents"
3. **Upload des fichiers** (formats supportés : PDF, TXT, MD, DOCX)
4. **Cliquer "🚀 Traiter les documents"**
5. ✅ **Déduplication automatique** - les fichiers déjà traités sont ignorés
6. ✅ **Chunking et embedding** automatiques

### Étape 3 : Génération de requirements ⭐ NOUVEAU !
1. **Rester dans l'onglet "Project Management"**
2. **Aller dans la section "Requirements"**
3. **Cliquer sur le sous-onglet "🚀 Générer Requirements"**
4. **Configurer la génération** :
   - Sélectionner les phases ARCADIA (Operational, System, Logical, Physical)
   - Choisir les types (Functional, Non-Functional, Stakeholder)
   - Ajuster les options avancées
5. **Cliquer "🚀 Générer Requirements"**
6. ✅ **Génération automatique** basée sur les documents du projet
7. ✅ **Sauvegarde automatique** dans le projet
8. ✅ **Affichage des résultats** avec statistiques

### Étape 4 : Consultation des requirements
1. **Dans la section "Requirements"**
2. **Cliquer sur "📝 Requirements Générés"**
3. **Explorer les requirements** par phase et type
4. **Consulter les statistiques** du projet

### Étape 5 : Analyse ARCADIA
1. **Aller dans l'onglet "ARCADIA Analysis"** (séparé)
2. **Consulter les analyses détaillées** par phase
3. **Explorer** : Operational, System, Logical, Physical
4. **Examiner** les liens de traçabilité cross-phase

### Étape 6 : Export des résultats
1. **Dans l'onglet "ARCADIA Analysis"**
2. **Sélectionner le format d'export** :
   - `ARCADIA_Analysis_JSON` - Détails complets toutes phases
   - `Analysis_Markdown` - Rapport compréhensif
   - `Analysis_Excel` - Données structurées (CSV)
3. **Cliquer "📤 Export Analysis"**
4. ✅ **Téléchargement automatique** du fichier

## 💾 Persistance des données

### Base de données SQLite
- **Fichier** : `data/safe_mbse.db`
- **Tables** :
  - `projects` - Métadonnées des projets
  - `processed_documents` - Documents avec hash de déduplication
  - `document_chunks` - Contenu segmenté avec embeddings
  - `requirements` - Requirements générés par projet

### Déduplication intelligente
- **Hash SHA-256** de chaque fichier
- **Vérification automatique** avant traitement
- **Économies** : 90%+ de temps sur les retraitements
- **Message informatif** : "X fichier(s) déjà traité(s)"

### Statistiques temps réel
```json
{
  "documents": {"total": 5, "embedding_model": "nomic-embed-text"},
  "chunks": {"total": 127, "vectorstore_count": 127},
  "requirements": {"total": 45}
}
```

## 🔧 Systèmes et fallbacks

### Système Enhanced (Recommandé)
- **Embeddings Nomic** via Ollama (`nomic-embed-text:latest`)
- **Performances optimales** pour la recherche vectorielle
- **Toutes les fonctionnalités** disponibles

### Système Simple (Fallback)
- **Embeddings par défaut** de ChromaDB
- **Fonctionnalités complètes** de gestion de projets
- **Compatible** avec tous les environnements

### Système Traditionnel (Ultime fallback)
- **Mode de compatibilité** sans persistance
- **Fonctionnalités de base** uniquement
- **Utilisé** en cas d'échec des systèmes persistants

## 🔍 Recherche et navigation

### Recherche par projet
- **Scope automatique** au projet sélectionné
- **Recherche vectorielle** dans tous les documents du projet
- **Résultats triés** par pertinence (score de similarité)
- **Métadonnées** : nom du fichier, chunk, position

### Navigation multi-projets
- **Switch rapide** entre projets via sidebar
- **État persistant** : dernière sélection mémorisée
- **Isolation des données** : pas de confusion entre projets
- **Statistiques séparées** par projet

## 📊 Monitoring et statistiques

### Métriques projet
- **Nombre de documents** traités
- **Total de chunks** créés
- **Requirements générés** par phase/type
- **Modèle d'embedding** utilisé
- **Taille totale** des données

### Performance
- **Temps de traitement** par document
- **Efficacité de déduplication** (fichiers sautés)
- **Utilisation mémoire** vectorstore
- **Temps de réponse** recherche

## 🛠️ Dépannage

### Vérification du système
```bash
python demo_project_management.py
```

### Diagnostic de base de données
```bash
python fix_chromadb_conflict.py
```

### Logs détaillés
- **Fichier** : `logs/requirements_generation.log`
- **Niveau** : INFO/WARNING/ERROR
- **Console** : Affichage temps réel

### Problèmes courants

#### ❌ "Mode traditionnel - Gestion de projets non disponible"
**Cause** : Système persistant non disponible  
**Solution** : Vérifier Ollama server + modèle `nomic-embed-text:latest`

#### ❌ "Erreur récupération projets"
**Cause** : Base de données corrompue ou verrouillée  
**Solution** : `python fix_chromadb_conflict.py`

#### ⚠️ "X fichier(s) déjà traité(s)"
**Cause** : Déduplication automatique (comportement normal)  
**Info** : Économie de temps - aucune action requise

## 🎯 Bonnes pratiques

### Organisation des projets
- **Noms descriptifs** : "Smart Transportation V2.1"
- **Descriptions complètes** : objectifs, scope, stakeholders
- **Documents groupés** par livrable ou phase ARCADIA

### Gestion des documents
- **Formats préférés** : PDF pour specs, MD pour documentation
- **Noms cohérents** : éviter les caractères spéciaux
- **Versions** : inclure version/date dans le nom de fichier

### Workflow ARCADIA
- **Phase par phase** : commencer par Operational Analysis
- **Validation** : vérifier la cohérence entre phases
- **Export régulier** : sauvegarder les analyses à chaque étape

### Performance
- **Chunks raisonnables** : éviter les documents > 50MB
- **Batch processing** : traiter plusieurs documents ensemble
- **Nettoyage régulier** : supprimer les projets obsolètes

---

## ✨ Résumé des avantages

✅ **Persistance complète** - Aucune perte de données  
✅ **Multi-projets** - Travail simultané sur plusieurs projets MBSE  
✅ **Déduplication** - Économie 90%+ de temps de traitement  
✅ **Interface intégrée** - Tout accessible depuis une seule application  
✅ **Export complet** - Analyses ARCADIA détaillées  
✅ **Recherche scopée** - Résultats pertinents par projet  
✅ **Fallback robuste** - Fonctionne même en cas de problème  
✅ **Monitoring** - Statistiques et métriques temps réel  

**Votre système ARISE dispose maintenant d'une gestion de projets MBSE professionnelle !** 🚀 