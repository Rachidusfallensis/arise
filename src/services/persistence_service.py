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
                    SELECT p.*, 
                           COUNT(DISTINCT pd.id) as docs_count,
                           COUNT(DISTINCT r.id) as reqs_count
                    FROM projects p
                    LEFT JOIN processed_documents pd ON p.id = pd.project_id
                    LEFT JOIN requirements r ON p.id = r.project_id
                    WHERE p.status = 'active'
                    GROUP BY p.id
                    ORDER BY p.updated_at DESC
                """)
                
                projects = []
                for row in cursor.fetchall():
                    projects.append(Project(
                        id=row[0],
                        name=row[1],
                        description=row[2] or "",
                        proposal_text=row[3] or "",
                        created_at=datetime.fromisoformat(row[4]),
                        updated_at=datetime.fromisoformat(row[5]),
                        documents_count=row[9] or 0,
                        requirements_count=row[10] or 0,
                        status=row[8] or "active"
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
                    SELECT p.*, 
                           COUNT(DISTINCT pd.id) as docs_count,
                           COUNT(DISTINCT r.id) as reqs_count
                    FROM projects p
                    LEFT JOIN processed_documents pd ON p.id = pd.project_id
                    LEFT JOIN requirements r ON p.id = r.project_id
                    WHERE p.id = ?
                    GROUP BY p.id
                """, (project_id,))
                
                row = cursor.fetchone()
                if row:
                    return Project(
                        id=row[0],
                        name=row[1],
                        description=row[2] or "",
                        proposal_text=row[3] or "",
                        created_at=datetime.fromisoformat(row[4]),
                        updated_at=datetime.fromisoformat(row[5]),
                        documents_count=row[9] or 0,
                        requirements_count=row[10] or 0,
                        status=row[8] or "active"
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
    
    def get_project_documents(self, project_id: str) -> List[ProcessedDocument]:
        """Récupérer tous les documents d'un projet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM processed_documents 
                    WHERE project_id = ?
                    ORDER BY processed_at DESC
                """, (project_id,))
                
                documents = []
                for row in cursor.fetchall():
                    documents.append(ProcessedDocument(
                        id=row[0],
                        filename=row[1],
                        file_path=row[2],
                        file_hash=row[3],
                        file_size=row[4],
                        processed_at=datetime.fromisoformat(row[5]),
                        project_id=row[6],
                        chunks_count=row[7] or 0,
                        embedding_model=row[8] or "nomic-embed-text",
                        processing_status=row[9] or "pending"
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
                cursor.execute("""
                    SELECT * FROM requirements 
                    WHERE project_id = ?
                    ORDER BY phase, type, title
                """, (project_id,))
                
                # Organiser par phase et type
                requirements: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
                for row in cursor.fetchall():
                    # Correct column indices based on table schema:
                    # 0:id, 1:project_id, 2:phase, 3:type, 4:title, 5:description, 
                    # 6:priority, 7:verification_method, 8:rationale, 9:priority_confidence, 
                    # 10:created_at, 11:updated_at
                    phase = row[2]
                    req_type = row[3]
                    
                    if phase not in requirements:
                        requirements[phase] = {}
                    if req_type not in requirements[phase]:
                        requirements[phase][req_type] = []
                    
                    requirements[phase][req_type].append({
                        "id": row[0],
                        "title": row[4],
                        "description": row[5],
                        "priority": row[6],
                        "verification_method": row[7] or "",
                        "rationale": row[8] or "",
                        "priority_confidence": row[9] or 0.0,
                        "created_at": row[10],
                        "updated_at": row[11]
                    })
                
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
                        SELECT * FROM arcadia_analyses 
                        WHERE project_id = ? AND phase_type = ?
                        ORDER BY created_at DESC
                    """, (project_id, phase_type))
                else:
                    cursor.execute("""
                        SELECT * FROM arcadia_analyses 
                        WHERE project_id = ?
                        ORDER BY phase_type, created_at DESC
                    """, (project_id,))
                
                analyses = []
                for row in cursor.fetchall():
                    analyses.append({
                        "id": row[0],
                        "project_id": row[1],
                        "phase_type": row[2],
                        "analysis_data": json.loads(row[3]) if row[3] else {},
                        "metadata": json.loads(row[4]) if row[4] else {},
                        "created_at": row[5],
                        "updated_at": row[6]
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
                cursor.execute("""
                    SELECT * FROM stakeholders 
                    WHERE project_id = ?
                    ORDER BY name
                """, (project_id,))
                
                stakeholders = []
                for row in cursor.fetchall():
                    stakeholders.append({
                        "id": row[0],
                        "name": row[2],
                        "role": row[3] or "",
                        "category": row[4] or "",
                        "needs": json.loads(row[5]) if row[5] else [],
                        "created_at": row[6]
                    })
                
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
                    SELECT * FROM project_sessions 
                    WHERE project_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (project_id, limit))
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        "id": row[0],
                        "project_id": row[1],
                        "action_type": row[2],
                        "action_description": row[3],
                        "result_data": json.loads(row[4]) if row[4] else {},
                        "user_id": row[5],
                        "created_at": row[6]
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
    
    def check_file_hash_globally(self, file_hash: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Vérifier si un fichier a déjà été traité dans n'importe quel projet"""
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