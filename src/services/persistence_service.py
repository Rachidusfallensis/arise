import sqlite3
import json
import hashlib
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass, asdict

@dataclass
class ProcessedDocument:
    """Represents a processed document with its metadata"""
    id: str
    filename: str
    file_path: str
    file_hash: str
    file_size: int
    processed_at: datetime
    project_id: str
    chunks_count: int
    embedding_model: str
    processing_status: str = "completed"

@dataclass
class Project:
    """Represents a project with its information"""
    id: str
    name: str
    description: str
    proposal_text: str
    created_at: datetime
    updated_at: datetime
    documents_count: int = 0
    requirements_count: int = 0
    status: str = "active"

class PersistenceService:
    """Persistence service to manage projects, documents and chunks"""
    
    def __init__(self, db_path: str = "./data/safe_mbse.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._ensure_db_structure()
        
    def _ensure_db_structure(self):
        """Assure que la structure de base de données est à jour"""
        try:
            # Créer le répertoire si nécessaire
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des projets améliorée
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        proposal_text TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        documents_count INTEGER DEFAULT 0,
                        requirements_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'active'
                    )
                """)
                
                # Table des documents traités
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processed_documents (
                        id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        file_hash TEXT NOT NULL UNIQUE,
                        file_size INTEGER NOT NULL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        project_id TEXT NOT NULL,
                        chunks_count INTEGER DEFAULT 0,
                        embedding_model TEXT DEFAULT 'nomic-embed-text',
                        processing_status TEXT DEFAULT 'pending',
                        metadata TEXT,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                """)
                
                # Table des chunks améliorée
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id TEXT PRIMARY KEY,
                        document_id TEXT NOT NULL,
                        project_id TEXT NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        content_hash TEXT NOT NULL,
                        embedding_vector TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (document_id) REFERENCES processed_documents (id),
                        FOREIGN KEY (project_id) REFERENCES projects (id),
                        UNIQUE(document_id, chunk_index)
                    )
                """)
                
                # Table des requirements (NOUVELLE)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS requirements (
                        id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        phase TEXT NOT NULL,
                        type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        priority TEXT DEFAULT 'SHOULD',
                        verification_method TEXT,
                        rationale TEXT,
                        priority_confidence REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                """)
                
                # Table des analyses ARCADIA (NOUVELLE)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS arcadia_analyses (
                        id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        phase_type TEXT NOT NULL,
                        analysis_data TEXT NOT NULL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                """)
                
                # Table des sessions utilisateur (améliorée)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS project_sessions (
                        id TEXT PRIMARY KEY,
                        project_id TEXT,
                        action_type TEXT NOT NULL,
                        action_description TEXT,
                        result_data TEXT,
                        user_id TEXT DEFAULT 'default_user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                """)
                
                # Table des stakeholders pour traçabilité (NOUVELLE)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stakeholders (
                        id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        role TEXT,
                        category TEXT,
                        needs TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                """)
                
                # Index pour optimiser les performances
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_project ON processed_documents(project_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_hash ON processed_documents(file_hash)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_project ON document_chunks(project_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_requirements_project ON requirements(project_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_requirements_phase ON requirements(phase)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_arcadia_project ON arcadia_analyses(project_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_arcadia_phase ON arcadia_analyses(phase_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_project ON project_sessions(project_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_stakeholders_project ON stakeholders(project_id)")
                
                conn.commit()
                self.logger.info("Structure de base de données initialisée avec succès")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de la base de données : {str(e)}")
            raise
    
    def create_project(self, name: str, description: str = "", proposal_text: str = "") -> str:
        """Créer un nouveau projet"""
        project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(name) % 10000:04d}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO projects (id, name, description, proposal_text)
                    VALUES (?, ?, ?, ?)
                """, (project_id, name, description, proposal_text))
                conn.commit()
                
                self.logger.info(f"Projet créé : {project_id} - {name}")
                return project_id
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du projet : {str(e)}")
            raise
    
    def get_all_projects(self) -> List[Project]:
        """Récupérer tous les projets"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.id, p.name, p.description, p.proposal_text, p.created_at, p.updated_at,
                           p.documents_count, p.requirements_count, p.status,
                           COUNT(DISTINCT pd.id) as docs_count,
                           COUNT(DISTINCT r.id) as reqs_count
                    FROM projects p
                    LEFT JOIN processed_documents pd ON p.id = pd.project_id
                    LEFT JOIN requirements r ON p.id = r.project_id
                    WHERE p.status = 'active'
                    GROUP BY p.id, p.name, p.description, p.proposal_text, p.created_at, p.updated_at,
                             p.documents_count, p.requirements_count, p.status
                    ORDER BY p.updated_at DESC
                """)
                
                projects = []
                for row in cursor.fetchall():
                    # Safe access with bounds checking
                    if len(row) < 11:
                        self.logger.warning(f"Incomplete project record found: {len(row)} columns instead of 11")
                        continue
                        
                    projects.append(Project(
                        id=row[0] if row[0] else "",
                        name=row[1] if row[1] else "",
                        description=row[2] if row[2] else "",
                        proposal_text=row[3] if row[3] else "",
                        created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                        updated_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                        documents_count=row[9] if len(row) > 9 and row[9] is not None else 0,
                        requirements_count=row[10] if len(row) > 10 and row[10] is not None else 0,
                        status=row[8] if len(row) > 8 and row[8] else "active"
                    ))
                
                return projects
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des projets : {str(e)}")
            return []
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Récupérer un projet par son ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.id, p.name, p.description, p.proposal_text, p.created_at, p.updated_at,
                           p.documents_count, p.requirements_count, p.status,
                           COUNT(DISTINCT pd.id) as docs_count,
                           COUNT(DISTINCT r.id) as reqs_count
                    FROM projects p
                    LEFT JOIN processed_documents pd ON p.id = pd.project_id
                    LEFT JOIN requirements r ON p.id = r.project_id
                    WHERE p.id = ?
                    GROUP BY p.id, p.name, p.description, p.proposal_text, p.created_at, p.updated_at,
                             p.documents_count, p.requirements_count, p.status
                """, (project_id,))
                
                row = cursor.fetchone()
                if row:
                    # Safe access with bounds checking
                    if len(row) < 11:
                        self.logger.warning(f"Incomplete project record found: {len(row)} columns instead of 11")
                        return None
                        
                    return Project(
                        id=row[0] if row[0] else "",
                        name=row[1] if row[1] else "",
                        description=row[2] if row[2] else "",
                        proposal_text=row[3] if row[3] else "",
                        created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                        updated_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                        documents_count=row[9] if len(row) > 9 and row[9] is not None else 0,
                        requirements_count=row[10] if len(row) > 10 and row[10] is not None else 0,
                        status=row[8] if len(row) > 8 and row[8] else "active"
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du projet {project_id} : {str(e)}")
            return None
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculer le hash SHA-256 d'un fichier"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du hash pour {file_path} : {str(e)}")
            return ""
    
    def is_document_processed(self, file_path: str, project_id: str) -> Tuple[bool, Optional[str]]:
        """Vérifier si un document a déjà été traité pour ce projet"""
        try:
            file_hash = self.calculate_file_hash(file_path)
            if not file_hash:
                return False, None
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, processing_status 
                    FROM processed_documents 
                    WHERE file_hash = ? AND project_id = ? AND processing_status = 'completed'
                """, (file_hash, project_id))
                
                result = cursor.fetchone()
                if result:
                    return True, result[0]
                return False, None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du document : {str(e)}")
            return False, None
    
    def register_document(self, file_path: str, project_id: str) -> str:
        """Enregistrer un nouveau document à traiter"""
        try:
            file_hash = self.calculate_file_hash(file_path)
            file_stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file_path) % 10000:04d}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO processed_documents 
                    (id, filename, file_path, file_hash, file_size, project_id, processing_status)
                    VALUES (?, ?, ?, ?, ?, ?, 'processing')
                """, (doc_id, filename, file_path, file_hash, file_stat.st_size, project_id))
                conn.commit()
                
                self.logger.info(f"Document enregistré : {doc_id} - {filename}")
                return doc_id
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement du document : {str(e)}")
            raise
    
    def save_document_chunks(self, document_id: str, project_id: str, chunks: List[Dict[str, Any]]) -> bool:
        """Sauvegarder les chunks d'un document"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Supprimer les anciens chunks
                cursor.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
                
                # Insérer les nouveaux chunks
                for i, chunk in enumerate(chunks):
                    chunk_id = f"chunk_{document_id}_{i:04d}"
                    content = chunk.get("content", "")
                    content_hash = hashlib.sha256(content.encode()).hexdigest()
                    metadata = json.dumps(chunk.get("metadata", {}))
                    
                    cursor.execute("""
                        INSERT INTO document_chunks 
                        (id, document_id, project_id, chunk_index, content, content_hash, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (chunk_id, document_id, project_id, i, content, content_hash, metadata))
                
                # Mettre à jour le statut du document
                cursor.execute("""
                    UPDATE processed_documents 
                    SET processing_status = 'completed', chunks_count = ?
                    WHERE id = ?
                """, (len(chunks), document_id))
                
                conn.commit()
                self.logger.info(f"Sauvegardé {len(chunks)} chunks pour le document {document_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des chunks : {str(e)}")
            return False
    
    def get_project_chunks(self, project_id: str) -> List[Dict[str, Any]]:
        """Récupérer tous les chunks d'un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT dc.content, dc.metadata, pd.filename
                    FROM document_chunks dc
                    JOIN processed_documents pd ON dc.document_id = pd.id
                    WHERE dc.project_id = ?
                    ORDER BY pd.filename, dc.chunk_index
                """, (project_id,))
                
                chunks = []
                for row in cursor.fetchall():
                    metadata = json.loads(row[1]) if row[1] else {}
                    metadata["source_filename"] = row[2]
                    
                    chunks.append({
                        "content": row[0],
                        "metadata": metadata
                    })
                
                return chunks
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des chunks du projet : {str(e)}")
            return []
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Récupérer tous les chunks d'un document spécifique"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT dc.content, dc.metadata, pd.filename
                    FROM document_chunks dc
                    JOIN processed_documents pd ON dc.document_id = pd.id
                    WHERE dc.document_id = ?
                    ORDER BY dc.chunk_index
                """, (document_id,))
                
                chunks = []
                for row in cursor.fetchall():
                    metadata = json.loads(row[1]) if row[1] else {}
                    metadata["source_filename"] = row[2]
                    
                    chunks.append({
                        "content": row[0],
                        "metadata": metadata
                    })
                
                return chunks
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des chunks du document : {str(e)}")
            return []
    
    def get_project_documents(self, project_id: str) -> List[ProcessedDocument]:
        """Récupérer tous les documents d'un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, file_path, file_hash, file_size, processed_at,
                           project_id, chunks_count, embedding_model, processing_status
                    FROM processed_documents 
                    WHERE project_id = ?
                    ORDER BY processed_at DESC
                """, (project_id,))
                
                documents = []
                for row in cursor.fetchall():
                    # Safe access with bounds checking
                    if len(row) < 10:
                        self.logger.warning(f"Incomplete document record found: {len(row)} columns instead of 10")
                        continue
                        
                    documents.append(ProcessedDocument(
                        id=row[0] if row[0] else "",
                        filename=row[1] if row[1] else "",
                        file_path=row[2] if row[2] else "",
                        file_hash=row[3] if row[3] else "",
                        file_size=row[4] if row[4] and isinstance(row[4], (int, float)) else 0,
                        processed_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                        project_id=row[6] if row[6] else "",
                        chunks_count=row[7] if row[7] is not None else 0,
                        embedding_model=row[8] if row[8] else "nomic-embed-text",
                        processing_status=row[9] if row[9] else "pending"
                    ))
                
                return documents
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des documents : {str(e)}")
            return []
    
    def save_project_requirements(self, project_id: str, requirements: Dict[str, Any]) -> bool:
        """Sauvegarder les requirements générés pour un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Parcourir les requirements par phase et type
                for phase, phase_reqs in requirements.get("requirements", {}).items():
                    for req_type, reqs in phase_reqs.items():
                        if isinstance(reqs, list):
                            for req in reqs:
                                req_id = req.get("id", f"req_{hash(str(req)) % 100000:05d}")
                                
                                # Vérifier si le requirement existe déjà
                                cursor.execute("""
                                    SELECT id FROM requirements 
                                    WHERE id = ? AND project_id = ?
                                """, (req_id, project_id))
                                
                                if cursor.fetchone():
                                    # Mettre à jour
                                    cursor.execute("""
                                        UPDATE requirements SET
                                        title = ?, description = ?, priority = ?,
                                        verification_method = ?, rationale = ?,
                                        updated_at = CURRENT_TIMESTAMP
                                        WHERE id = ? AND project_id = ?
                                    """, (
                                        req.get("title", ""),
                                        req.get("description", ""),
                                        req.get("priority", "SHOULD"),
                                        req.get("verification_method", ""),
                                        req.get("rationale", ""),
                                        req_id, project_id
                                    ))
                                else:
                                    # Insérer nouveau
                                    cursor.execute("""
                                        INSERT INTO requirements 
                                        (id, phase, type, title, description, priority, 
                                         verification_method, rationale, project_id)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        req_id, phase, req_type,
                                        req.get("title", ""),
                                        req.get("description", ""),
                                        req.get("priority", "SHOULD"),
                                        req.get("verification_method", ""),
                                        req.get("rationale", ""),
                                        project_id
                                    ))
                
                conn.commit()
                self.logger.info(f"Requirements sauvegardés pour le projet {project_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des requirements : {str(e)}")
            return False
    
    def get_project_requirements(self, project_id: str) -> Dict[str, Any]:
        """Récupérer les requirements d'un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First check which columns exist in the requirements table
                cursor.execute("PRAGMA table_info(requirements)")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Build query based on available columns
                base_columns = ["id", "project_id", "phase", "type", "title", "description", "priority"]
                optional_columns = ["verification_method", "rationale", "priority_confidence", "created_at", "updated_at"]
                
                # Only select columns that exist
                select_columns = []
                for col in base_columns:
                    if col in columns:
                        select_columns.append(col)
                
                for col in optional_columns:
                    if col in columns:
                        select_columns.append(col)
                
                if not select_columns:
                    self.logger.error("No valid columns found in requirements table")
                    return {"requirements": {}}
                
                query = f"""
                    SELECT {', '.join(select_columns)}
                    FROM requirements 
                    WHERE project_id = ?
                    ORDER BY phase, type, title
                """
                
                cursor.execute(query, (project_id,))
                
                # Organiser par phase et type
                requirements: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
                for row in cursor.fetchall():
                    # Safe access to row elements with bounds checking
                    if len(row) < len(base_columns):  # Ensure we have at least basic columns
                        self.logger.warning(f"Incomplete requirement record found: {len(row)} columns")
                        continue
                    
                    # Create column mapping
                    col_map = {col: idx for idx, col in enumerate(select_columns)}
                    
                    phase = row[col_map.get("phase", 2)] if "phase" in col_map else "unknown"
                    req_type = row[col_map.get("type", 3)] if "type" in col_map else "unknown"
                    
                    if phase not in requirements:
                        requirements[phase] = {}
                    if req_type not in requirements[phase]:
                        requirements[phase][req_type] = []
                    
                    # Build requirement object based on available columns
                    req_obj = {}
                    
                    # Basic required fields
                    req_obj["id"] = row[col_map.get("id", 0)] if "id" in col_map and row[col_map["id"]] else ""
                    req_obj["title"] = row[col_map.get("title", 4)] if "title" in col_map and row[col_map["title"]] else ""
                    req_obj["description"] = row[col_map.get("description", 5)] if "description" in col_map and row[col_map["description"]] else ""
                    req_obj["priority"] = row[col_map.get("priority", 6)] if "priority" in col_map and row[col_map["priority"]] else "SHOULD"
                    
                    # Optional fields with defaults
                    req_obj["verification_method"] = ""
                    req_obj["rationale"] = ""
                    req_obj["priority_confidence"] = 0.0
                    req_obj["created_at"] = ""
                    req_obj["updated_at"] = ""
                    
                    # Update with actual values if columns exist
                    if "verification_method" in col_map and col_map["verification_method"] < len(row):
                        req_obj["verification_method"] = row[col_map["verification_method"]] or ""
                    if "rationale" in col_map and col_map["rationale"] < len(row):
                        req_obj["rationale"] = row[col_map["rationale"]] or ""
                    if "priority_confidence" in col_map and col_map["priority_confidence"] < len(row):
                        req_obj["priority_confidence"] = row[col_map["priority_confidence"]] if row[col_map["priority_confidence"]] is not None else 0.0
                    if "created_at" in col_map and col_map["created_at"] < len(row):
                        req_obj["created_at"] = row[col_map["created_at"]] or ""
                    if "updated_at" in col_map and col_map["updated_at"] < len(row):
                        req_obj["updated_at"] = row[col_map["updated_at"]] or ""
                    
                    requirements[phase][req_type].append(req_obj)
                
                return {"requirements": requirements}
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des requirements : {str(e)}")
            return {"requirements": {}}
    
    def save_arcadia_analysis(self, project_id: str, phase_type: str, analysis_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Sauvegarder une analyse ARCADIA pour un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                analysis_id = f"arcadia_{project_id}_{phase_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO arcadia_analyses 
                    (id, project_id, phase_type, analysis_data, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    analysis_id, 
                    project_id, 
                    phase_type, 
                    json.dumps(analysis_data),
                    json.dumps(metadata or {})
                ))
                
                conn.commit()
                self.logger.info(f"Analyse ARCADIA sauvegardée : {phase_type} pour projet {project_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de l'analyse ARCADIA : {str(e)}")
            return False
    
    def get_project_arcadia_analyses(self, project_id: str, phase_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupérer les analyses ARCADIA d'un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if phase_type:
                    cursor.execute("""
                        SELECT id, project_id, phase_type, analysis_data, metadata, created_at, updated_at
                        FROM arcadia_analyses 
                        WHERE project_id = ? AND phase_type = ?
                        ORDER BY created_at DESC
                    """, (project_id, phase_type))
                else:
                    cursor.execute("""
                        SELECT id, project_id, phase_type, analysis_data, metadata, created_at, updated_at
                        FROM arcadia_analyses 
                        WHERE project_id = ?
                        ORDER BY phase_type, created_at DESC
                    """, (project_id,))
                
                analyses = []
                for row in cursor.fetchall():
                    # Safe access with bounds checking
                    if len(row) < 7:
                        self.logger.warning(f"Incomplete analysis record found: {len(row)} columns instead of 7")
                        continue
                        
                    analyses.append({
                        "id": row[0] if row[0] else "",
                        "project_id": row[1] if row[1] else "",
                        "phase_type": row[2] if row[2] else "",
                        "analysis_data": json.loads(row[3]) if row[3] else {},
                        "metadata": json.loads(row[4]) if row[4] else {},
                        "created_at": row[5] if row[5] else "",
                        "updated_at": row[6] if row[6] else ""
                    })
                
                return analyses
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des analyses ARCADIA : {str(e)}")
            return []
    
    def save_stakeholders(self, project_id: str, stakeholders: List[Dict[str, Any]]) -> bool:
        """Sauvegarder les stakeholders d'un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Supprimer les anciens stakeholders du projet
                cursor.execute("DELETE FROM stakeholders WHERE project_id = ?", (project_id,))
                
                # Insérer les nouveaux stakeholders
                for stakeholder in stakeholders:
                    stakeholder_id = f"stakeholder_{project_id}_{hash(stakeholder.get('name', '')) % 10000:04d}"
                    
                    cursor.execute("""
                        INSERT INTO stakeholders 
                        (id, project_id, name, role, category, needs)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        stakeholder_id,
                        project_id,
                        stakeholder.get('name', ''),
                        stakeholder.get('role', ''),
                        stakeholder.get('category', ''),
                        json.dumps(stakeholder.get('needs', []))
                    ))
                
                conn.commit()
                self.logger.info(f"Sauvegardé {len(stakeholders)} stakeholders pour le projet {project_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des stakeholders : {str(e)}")
            return False
    
    def get_project_stakeholders(self, project_id: str) -> List[Dict[str, Any]]:
        """Récupérer les stakeholders d'un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First check which columns exist in the stakeholders table
                cursor.execute("PRAGMA table_info(stakeholders)")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Build query based on available columns
                base_columns = ["id", "project_id", "name"]
                optional_columns = ["role", "category", "needs", "created_at"]
                
                # Only select columns that exist
                select_columns = []
                for col in base_columns:
                    if col in columns:
                        select_columns.append(col)
                
                for col in optional_columns:
                    if col in columns:
                        select_columns.append(col)
                
                if not select_columns:
                    self.logger.error("No valid columns found in stakeholders table")
                    return []
                
                query = f"""
                    SELECT {', '.join(select_columns)}
                    FROM stakeholders 
                    WHERE project_id = ?
                    ORDER BY name
                """
                
                cursor.execute(query, (project_id,))
                
                stakeholders = []
                for row in cursor.fetchall():
                    # Safe access with bounds checking
                    if len(row) < len(base_columns):
                        self.logger.warning(f"Incomplete stakeholder record found: {len(row)} columns")
                        continue
                    
                    # Create column mapping
                    col_map = {col: idx for idx, col in enumerate(select_columns)}
                    
                    # Build stakeholder object based on available columns
                    stakeholder_obj = {}
                    
                    # Basic required fields
                    stakeholder_obj["id"] = row[col_map.get("id", 0)] if "id" in col_map and row[col_map["id"]] else ""
                    stakeholder_obj["name"] = row[col_map.get("name", 2)] if "name" in col_map and row[col_map["name"]] else ""
                    
                    # Optional fields with defaults
                    stakeholder_obj["role"] = ""
                    stakeholder_obj["category"] = ""
                    stakeholder_obj["needs"] = []
                    stakeholder_obj["created_at"] = ""
                    
                    # Update with actual values if columns exist
                    if "role" in col_map and col_map["role"] < len(row):
                        stakeholder_obj["role"] = row[col_map["role"]] if row[col_map["role"]] else ""
                    if "category" in col_map and col_map["category"] < len(row):
                        stakeholder_obj["category"] = row[col_map["category"]] if row[col_map["category"]] else ""
                    if "needs" in col_map and col_map["needs"] < len(row):
                        stakeholder_obj["needs"] = json.loads(row[col_map["needs"]]) if row[col_map["needs"]] else []
                    if "created_at" in col_map and col_map["created_at"] < len(row):
                        stakeholder_obj["created_at"] = row[col_map["created_at"]] if row[col_map["created_at"]] else ""
                    
                    stakeholders.append(stakeholder_obj)
                
                return stakeholders
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des stakeholders : {str(e)}")
            return []
    
    def log_project_session(self, project_id: str, action_type: str, action_description: str, result_data: Optional[Dict[str, Any]] = None) -> bool:
        """Enregistrer une action dans l'historique du projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                
                cursor.execute("""
                    INSERT INTO project_sessions 
                    (id, project_id, action_type, action_description, result_data)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id,
                    project_id,
                    action_type,
                    action_description,
                    json.dumps(result_data or {})
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement de la session : {str(e)}")
            return False
    
    def get_project_sessions(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupérer l'historique des sessions d'un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, project_id, action_type, action_description, result_data, user_id, created_at
                    FROM project_sessions 
                    WHERE project_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (project_id, limit))
                
                sessions = []
                for row in cursor.fetchall():
                    # Safe access with bounds checking
                    if len(row) < 7:
                        self.logger.warning(f"Incomplete session record found: {len(row)} columns instead of 7")
                        continue
                        
                    sessions.append({
                        "id": row[0] if row[0] else "",
                        "project_id": row[1] if row[1] else "",
                        "action_type": row[2] if row[2] else "",
                        "action_description": row[3] if row[3] else "",
                        "result_data": json.loads(row[4]) if row[4] else {},
                        "user_id": row[5] if row[5] else "default_user",
                        "created_at": row[6] if row[6] else ""
                    })
                
                return sessions
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des sessions : {str(e)}")
            return []
    
    def delete_project(self, project_id: str) -> bool:
        """Supprimer un projet et toutes ses données associées"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Supprimer dans l'ordre des dépendances
                cursor.execute("DELETE FROM document_chunks WHERE project_id = ?", (project_id,))
                cursor.execute("DELETE FROM processed_documents WHERE project_id = ?", (project_id,))
                cursor.execute("DELETE FROM requirements WHERE project_id = ?", (project_id,))
                cursor.execute("DELETE FROM arcadia_analyses WHERE project_id = ?", (project_id,))
                cursor.execute("DELETE FROM stakeholders WHERE project_id = ?", (project_id,))
                cursor.execute("DELETE FROM project_sessions WHERE project_id = ?", (project_id,))
                cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                
                conn.commit()
                self.logger.info(f"Projet supprimé : {project_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression du projet : {str(e)}")
            return False
    
    def update_project(self, project_id: str, name: Optional[str] = None, description: Optional[str] = None, proposal_text: Optional[str] = None) -> bool:
        """Mettre à jour les informations d'un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Construire la requête dynamiquement
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = ?")
                    params.append(name)
                
                if description is not None:
                    updates.append("description = ?")
                    params.append(description)
                
                if proposal_text is not None:
                    updates.append("proposal_text = ?")
                    params.append(proposal_text)
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(project_id)
                
                if updates:
                    query = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(query, params)
                    conn.commit()
                    
                    self.logger.info(f"Projet mis à jour : {project_id}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du projet : {str(e)}")
            return False
    
    def check_file_hash_in_project(self, file_hash: str, project_id: str) -> Tuple[bool, Optional[str]]:
        """Vérifier si un fichier a déjà été traité dans le projet spécifique (RECOMMANDÉ)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, processed_at 
                    FROM processed_documents 
                    WHERE file_hash = ? AND project_id = ? AND processing_status = 'completed'
                    ORDER BY processed_at DESC
                    LIMIT 1
                """, (file_hash, project_id))
                
                result = cursor.fetchone()
                if result:
                    return True, result[0]  # found, document_id
                return False, None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du hash dans le projet : {str(e)}")
            return False, None

    def check_file_hash_globally(self, file_hash: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Vérifier si un fichier a déjà été traité dans n'importe quel projet (AVANCÉ)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, project_id, filename, processed_at 
                    FROM processed_documents 
                    WHERE file_hash = ? AND processing_status = 'completed'
                    ORDER BY processed_at DESC
                    LIMIT 1
                """, (file_hash,))
                
                result = cursor.fetchone()
                if result:
                    return True, result[0], result[1]  # found, document_id, project_id
                return False, None, None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification globale du hash : {str(e)}")
            return False, None, None
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Obtenir des statistiques globales de la base de données"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Statistiques des projets
                cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'")
                stats['active_projects'] = cursor.fetchone()[0]
                
                # Statistiques des documents
                cursor.execute("SELECT COUNT(*), SUM(file_size) FROM processed_documents WHERE processing_status = 'completed'")
                doc_result = cursor.fetchone()
                stats['total_documents'] = doc_result[0]
                stats['total_file_size'] = doc_result[1] or 0
                
                # Statistiques des chunks
                cursor.execute("SELECT COUNT(*) FROM document_chunks")
                stats['total_chunks'] = cursor.fetchone()[0]
                
                # Statistiques des requirements
                cursor.execute("SELECT COUNT(*) FROM requirements")
                stats['total_requirements'] = cursor.fetchone()[0]
                
                # Statistiques des analyses ARCADIA
                cursor.execute("SELECT COUNT(*) FROM arcadia_analyses")
                stats['total_arcadia_analyses'] = cursor.fetchone()[0]
                
                # Statistiques des stakeholders
                cursor.execute("SELECT COUNT(*) FROM stakeholders")
                stats['total_stakeholders'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des statistiques : {str(e)}")
            return {"error": str(e)}
    
    def _get_db_connection(self):
        """Helper method to get database connection"""
        return sqlite3.connect(self.db_path)
    
    def link_document_to_project(self, existing_doc_id: str, target_project_id: str) -> bool:
        """Link an existing document to a new project by copying its data and chunks"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get the existing document details
                cursor.execute("""
                    SELECT filename, file_path, file_hash, file_size, chunks_count, 
                           embedding_model, processing_status, metadata
                    FROM processed_documents 
                    WHERE id = ? AND processing_status = 'completed'
                """, (existing_doc_id,))
                
                existing_doc = cursor.fetchone()
                if not existing_doc:
                    self.logger.error(f"Document {existing_doc_id} not found or not completed")
                    return False
                
                # Check if document already exists in target project
                cursor.execute("""
                    SELECT id FROM processed_documents 
                    WHERE file_hash = ? AND project_id = ?
                """, (existing_doc[2], target_project_id))
                
                if cursor.fetchone():
                    self.logger.info(f"Document already exists in project {target_project_id}")
                    return True  # Consider it successful if already exists
                
                # Create new document entry for the target project
                new_doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(f'{existing_doc_id}_{target_project_id}') % 10000:04d}"
                
                cursor.execute("""
                    INSERT INTO processed_documents 
                    (id, filename, file_path, file_hash, file_size, project_id, 
                     chunks_count, embedding_model, processing_status, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    new_doc_id,
                    existing_doc[0],  # filename
                    existing_doc[1],  # file_path
                    existing_doc[2],  # file_hash
                    existing_doc[3],  # file_size
                    target_project_id,
                    existing_doc[4],  # chunks_count
                    existing_doc[5] if existing_doc[5] else 'nomic-embed-text',  # embedding_model
                    'completed',      # processing_status
                    existing_doc[7]   # metadata
                ))
                
                # Copy all chunks from the existing document to the new project
                cursor.execute("""
                    SELECT chunk_index, content, content_hash, embedding_vector, metadata
                    FROM document_chunks 
                    WHERE document_id = ?
                    ORDER BY chunk_index
                """, (existing_doc_id,))
                
                chunks = cursor.fetchall()
                
                for chunk in chunks:
                    new_chunk_id = f"chunk_{new_doc_id}_{chunk[0]:04d}"
                    cursor.execute("""
                        INSERT INTO document_chunks 
                        (id, document_id, project_id, chunk_index, content, content_hash, 
                         embedding_vector, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        new_chunk_id,
                        new_doc_id,
                        target_project_id,
                        chunk[0],  # chunk_index
                        chunk[1],  # content
                        chunk[2],  # content_hash
                        chunk[3],  # embedding_vector
                        chunk[4]   # metadata
                    ))
                
                conn.commit()
                
                self.logger.info(f"Successfully linked document {existing_doc[0]} to project {target_project_id}")
                self.logger.info(f"Created new document {new_doc_id} with {len(chunks)} chunks")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error linking document to project: {str(e)}")
            return False 