# Guide du Système RAG Persistant avec Embedding Nomic

## 🎯 Vue d'ensemble

Le système MBSE RAG a été considérablement amélioré avec les nouvelles fonctionnalités suivantes :

### ✨ Nouvelles fonctionnalités

#### 🔧 Embedding Nomic
- **Modèle utilisé** : `nomic-embed-text:latest` depuis le serveur Ollama
- **Avantages** : Embeddings de haute qualité, optimisés pour la recherche sémantique
- **Performance** : Dimension vectorielle optimisée pour les documents techniques

#### 🗂️ Gestion de projets persistants
- **Persistance complète** : Plus de perte de données lors du rechargement
- **Gestion multi-projets** : Travaillez sur plusieurs projets simultanément
- **Traçabilité** : Historique complet des traitements et générations

#### ⚡ Optimisation intelligente
- **Détection de doublons** : Évite le retraitement des fichiers déjà analysés
- **Cache de chunks** : Réutilise les embeddings existants
- **Performance** : Temps de traitement considérablement réduits

## 🚀 Démarrage rapide

### 1. Vérification du système

Avant d'utiliser le système, lancez le script de test :

```bash
python test_persistent_system.py
```

Ce script vérifie :
- ✅ Connexion au serveur Ollama
- ✅ Fonctionnement du modèle Nomic
- ✅ Base de données SQLite
- ✅ Système vectoriel ChromaDB
- ✅ Génération de requirements

### 2. Lancement de l'interface

```bash
streamlit run ui/app.py
```

## 📋 Workflow recommandé

### Étape 1 : Créer un projet

1. **Accédez à la sidebar** : Section "🗂️ Gestion des Projets"
2. **Développez "➕ Nouveau Projet"**
3. **Remplissez les informations** :
   - Nom du projet
   - Description (optionnelle)
   - Texte de proposition initiale (optionnel)
4. **Cliquez sur "Créer le projet"**

Le projet est immédiatement créé et sélectionné.

### Étape 2 : Ajouter des documents

1. **Onglet "📄 Documents"** dans le tableau de bord
2. **Section "📤 Ajouter des documents"**
3. **Sélectionnez vos fichiers** : PDF, TXT, MD, DOCX
4. **Cliquez sur "🚀 Traiter les documents"**

Le système :
- ✅ Vérifie si les fichiers ont déjà été traités
- ✅ Extrait le contenu et crée des chunks
- ✅ Génère les embeddings avec Nomic
- ✅ Sauvegarde tout en base de données

### Étape 3 : Générer des requirements

1. **Onglet "📝 Génération"**
2. **Configurez les paramètres** :
   - Phase ARCADIA (operational, system, logical, physical)
   - Types de requirements (functional, non_functional, stakeholder)
   - Options avancées (analyse structurée, inter-phases)
3. **Saisissez ou modifiez le texte de proposition**
4. **Cliquez sur "🚀 Générer les Requirements"**

Les requirements sont automatiquement sauvegardés dans le projet.

### Étape 4 : Explorer avec le chat

1. **Onglet "🔍 Recherche"** ou **Onglet "💬 Chat"**
2. **Posez des questions** sur vos documents
3. **Le système recherche** uniquement dans les documents du projet actuel
4. **Résultats contextualisés** avec scores de similarité

## 🗃️ Structure de la base de données

### Tables principales

#### `projects`
- Informations des projets
- Métadonnées de création et modification
- Compteurs de documents et requirements

#### `processed_documents`
- Documents traités avec hash de vérification
- Statut de traitement (pending, completed, failed)
- Métadonnées d'embedding (modèle utilisé)

#### `document_chunks`
- Chunks de contenu avec embeddings
- Liens vers les documents et projets
- Métadonnées de recherche

#### `requirements`
- Requirements générés par phase et type
- Liens vers les projets
- Historique de mise à jour

## 🔧 Configuration avancée

### Paramètres d'embedding

Dans `config/config.py` :

```python
# Modèle d'embedding Nomic
EMBEDDING_MODEL = "nomic-embed-text:latest"

# Configuration ChromaDB
VECTORDB_PATH = "./data/vectordb"
COLLECTION_NAME = "safe_mbse_requirements"

# Chunking des documents
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

### Optimisation des performances

#### Taille des chunks
- **Recommandé** : 1000 caractères avec 200 de recouvrement
- **Documents techniques** : Peut être augmenté à 1500
- **Documents courts** : Réduire à 500

#### Paramètres de recherche
- **top_k par défaut** : 5 résultats
- **Seuil de similarité** : Ajustable selon le contexte
- **Filtrage par projet** : Automatique

## 📊 Surveillance et maintenance

### Statistiques de projet

Chaque projet affiche :
- 📄 **Nombre de documents** et leur statut
- 🧩 **Nombre de chunks** et taille vectorstore
- 📝 **Nombre de requirements** par phase
- 💾 **Taille totale** des documents

### Actions de maintenance

#### Nettoyage des vecteurs
```python
rag_system.cleanup_project_vectors(project_id)
```

#### Retraitement de documents
- Possible via l'interface ou programmatiquement
- Recalcule les embeddings avec le modèle actuel
- Préserve l'historique

#### Export de données
- Formats supportés : JSON, Markdown, Excel, DOORS, ReqIF
- Export complet ou par phase
- Métadonnées de traçabilité incluses

## 🚨 Résolution de problèmes

### Erreurs courantes

#### "Erreur d'embedding Nomic"
- **Cause** : Serveur Ollama inaccessible ou modèle non disponible
- **Solution** : Vérifier la connexion et la disponibilité du modèle
```bash
ollama list  # Vérifier les modèles disponibles
ollama pull nomic-embed-text  # Télécharger si nécessaire
```

#### "Document déjà traité"
- **Cause** : Le hash du fichier existe déjà dans la base
- **Solution** : Normal et souhaitable ! Le système évite les doublons
- **Forcer le retraitement** : Utiliser l'option "🔄 Retraiter"

#### "Aucun résultat de recherche"
- **Cause** : Pas de documents dans le projet ou query mal formulée
- **Solution** : 
  1. Vérifier que des documents sont traités
  2. Utiliser des termes plus génériques
  3. Vérifier les statistiques du projet

#### "Erreur de base de données"
- **Cause** : Problème de permissions ou corruption
- **Solution** : 
  1. Vérifier les droits d'écriture dans `/data`
  2. Sauvegarder et recréer la base si nécessaire

### Logs et diagnostic

#### Fichiers de logs
- `logs/requirements_generation.log` : Logs généraux
- `logs/test_persistent_system.log` : Logs des tests
- `logs/app_refactored.log` : Logs de l'interface

#### Diagnostic système
```bash
# Test complet
python test_persistent_system.py

# Test connexion Ollama
curl http://llm-eva.univ-pau.fr:11434/api/version

# Vérification base de données
sqlite3 data/safe_mbse.db ".tables"
```

## 🔄 Migration depuis l'ancien système

### Données existantes
- L'ancien système continue de fonctionner
- Nouvelle base de données créée à côté
- Pas de perte de données existantes

### Procédure de migration
1. **Sauvegarder** les données actuelles
2. **Créer de nouveaux projets** dans le système persistant
3. **Réimporter les documents** (détection automatique des doublons)
4. **Régénérer les requirements** avec les nouvelles fonctionnalités

## 🔮 Fonctionnalités à venir

### Version suivante
- 🔄 **Synchronisation multi-utilisateurs**
- 📈 **Analytics avancés** des projets
- 🌐 **API REST** pour intégration externe
- 📱 **Interface mobile** responsive
- 🔐 **Gestion d'utilisateurs** et permissions

### Intégrations
- **Git** : Versioning des projets
- **Jenkins** : CI/CD pour les requirements
- **Jira** : Synchronisation des issues
- **Confluence** : Publication automatique

## 💡 Conseils d'utilisation

### Organisation des projets
- **Un projet par système** à développer
- **Nommage cohérent** : "PROJET_VERSION_DATE"
- **Descriptions détaillées** pour faciliter la recherche

### Optimisation des documents
- **Formats préférés** : Markdown, PDF avec texte
- **Éviter** : Images scannées, documents protégés
- **Structurer** : Utiliser des titres et sections claires

### Génération de requirements
- **Commencer par la phase operational** : Base pour les autres
- **Itérer** : Affiner les textes de proposition
- **Vérifier** : Toujours examiner les results avant export

### Recherche efficace
- **Termes techniques** : Utiliser le vocabulaire du domaine
- **Questions ouvertes** : "Comment le système gère-t-il..." 
- **Contexte** : Préciser la phase ARCADIA concernée

---

## 📞 Support

Pour toute question ou problème :
1. **Consulter ce guide** et les logs
2. **Lancer les tests** de diagnostic
3. **Vérifier la configuration** du serveur Ollama
4. **Contacter l'équipe** avec les logs d'erreur 