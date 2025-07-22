import streamlit as st
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import json

# Support for both RAG system types
try:
    from src.core.enhanced_persistent_rag_system import EnhancedPersistentRAGSystem
    from src.core.simple_persistent_rag_system import SimplePersistentRAGSystem
    # Type union to support both systems
    PersistentRAGSystem = Union[EnhancedPersistentRAGSystem, SimplePersistentRAGSystem]
except ImportError:
    # Fallback if one of the imports fails
    try:
        from src.core.simple_persistent_rag_system import SimplePersistentRAGSystem
        PersistentRAGSystem = SimplePersistentRAGSystem  # type: ignore
    except ImportError:
        from src.core.rag_system import SAFEMBSERAGSystem
        PersistentRAGSystem = SAFEMBSERAGSystem  # type: ignore

from src.services.persistence_service import Project, ProcessedDocument

class ProjectManager:
    """Interface manager for MBSE projects - Compatible with all RAG systems"""
    
    def __init__(self, rag_system: PersistentRAGSystem):
        self.rag_system = rag_system
        
        # Check system capabilities
        self.has_persistence = hasattr(rag_system, 'get_all_projects')
        self.has_project_management = hasattr(rag_system, 'create_project')
        self.has_document_management = hasattr(rag_system, 'add_documents_to_project')
    
    def render_project_sidebar(self) -> Optional[str]:
        """Display the project management sidebar"""
        if not self.has_persistence:
            st.sidebar.info("🔧 Traditional mode - Project management not available")
            return None
            
        st.sidebar.markdown("## 🗂️ Project Management")
        
        # Get all projects
        try:
            projects = self.rag_system.get_all_projects()
        except Exception as e:
            st.sidebar.error(f"❌ Error retrieving projects: {str(e)}")
            return None
        
        # Display current project
        current_project = self.rag_system.get_current_project() if hasattr(self.rag_system, 'get_current_project') else None
        if current_project:
            st.sidebar.success(f"📋 **Current Project:**\n{current_project.name}")
        else:
            st.sidebar.info("No project selected")
        
        # Enhanced project creation section
        if self.has_project_management:
            with st.sidebar.expander("➕ New Project", expanded=False):
                with st.form("new_project_form"):
                    new_name = st.text_input("Project Name", placeholder="My new MBSE project", max_chars=100)
                    new_description = st.text_area("Description", placeholder="Brief project description...", max_chars=1000, height=100)
                    new_proposal = st.text_area("Proposal Text", placeholder="Initial proposal text...", max_chars=5000, height=150)
                    
                    # Enhanced form validation
                    if st.form_submit_button("Create Project", type="primary"):
                        # Validate input
                        is_valid, error_message = self.validate_project_data(new_name, new_description, new_proposal)
                        
                        if not is_valid:
                            st.sidebar.error(f"❌ {error_message}")
                            return None
                        
                        try:
                            # Create project with validation
                            project_id = self.rag_system.create_project(
                                name=new_name.strip(),
                                description=new_description.strip(),
                                proposal_text=new_proposal.strip()
                            )
                            
                            # Success feedback
                            st.sidebar.success(f"✅ Project created: {new_name}")
                            st.sidebar.balloons()
                            
                            # Auto-load the new project
                            if hasattr(self.rag_system, 'load_project'):
                                self.rag_system.load_project(project_id)
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.sidebar.error(f"❌ Error creating project: {str(e)}")
                            # Log error for debugging
                            import logging
                            logging.error(f"Project creation failed: {str(e)}")
                
        # Project selection section
        if projects:
            st.sidebar.markdown("### 📂 Existing Projects")
            
            # Options for selectbox
            project_options = {f"{p.name} ({getattr(p, 'documents_count', 0)} docs)": p.id for p in projects}
            current_selection = None
            
            if current_project:
                for display_name, proj_id in project_options.items():
                    if proj_id == current_project.id:
                        current_selection = display_name
                        break
            
            selected_display = st.sidebar.selectbox(
                "Select a project",
                options=list(project_options.keys()),
                index=list(project_options.keys()).index(current_selection) if current_selection else 0,
                key="project_selector"
            )
            
            selected_project_id = project_options[selected_display]
            
            # Load project if different
            if not current_project or current_project.id != selected_project_id:
                if hasattr(self.rag_system, 'load_project') and self.rag_system.load_project(selected_project_id):
                    st.rerun()
            
            # Selected project information
            if current_project:
                self._render_project_info_sidebar(current_project)
            
            return selected_project_id
        else:
            st.sidebar.info("No projects available. Create a new one!")
            return None
    
    def _render_project_info_sidebar(self, project: Project):
        """Display project information in the sidebar with enhanced CRUD operations"""
        with st.sidebar.expander("ℹ️ Project Information", expanded=True):
            st.write(f"**ID:** `{project.id}`")
            st.write(f"**Created:** {project.created_at.strftime('%d/%m/%Y %H:%M')}")
            st.write(f"**Modified:** {project.updated_at.strftime('%d/%m/%Y %H:%M')}")
            
            # Statistics if available
            if hasattr(project, 'documents_count'):
                st.write(f"**Documents:** {project.documents_count}")
            if hasattr(project, 'requirements_count'):
                st.write(f"**Requirements:** {project.requirements_count}")
            
            if project.description:
                st.write(f"**Description:**")
                st.write(project.description)
            
            # Enhanced CRUD operations
            st.markdown("---")
            st.markdown("**🔧 Project Actions**")
            
            # Quick update project
            if st.button("✏️ Edit Project", use_container_width=True, key="edit_project_sidebar"):
                st.session_state.show_edit_project_modal = True
            
            # Delete project (with confirmation)
            if st.button("🗑️ Delete Project", use_container_width=True, key="delete_project_sidebar", type="secondary"):
                st.session_state.show_delete_project_modal = True
        
        # Handle modals
        self._handle_project_modals(project)
    
    def render_project_dashboard(self) -> Dict[str, Any]:
        """Afficher le tableau de bord du projet simplifié"""
        if not self.has_persistence:
            st.warning("🔧 Mode traditionnel - Tableau de bord de projet non disponible")
            return {}
            
        current_project = self.rag_system.get_current_project() if hasattr(self.rag_system, 'get_current_project') else None
        
        if not current_project:
            st.warning("⚠️ Aucun projet sélectionné. Veuillez en créer un ou en sélectionner un dans la sidebar.")
            return {}
        
        # En-tête du projet simplifié
        st.markdown(f"## 📋 {current_project.name}")
        if current_project.description:
            st.write(current_project.description)
        
        # Statistiques rapides si disponibles
        if hasattr(self.rag_system, 'get_project_statistics'):
            try:
                stats = self.rag_system.get_project_statistics()
                if not stats.get("error"):
                    self._render_quick_stats(stats)
            except Exception as e:
                st.warning(f"⚠️ Statistiques indisponibles : {str(e)}")
        
        return {}
    
    def _render_quick_stats(self, stats: Dict[str, Any]):
        """Afficher les statistiques rapides"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📄 Documents",
                value=stats.get("documents", {}).get("total", 0),
                delta=f"Modèle: {stats.get('documents', {}).get('embedding_model', 'N/A')}"
            )
        
        with col2:
            st.metric(
                label="🧩 Chunks",
                value=stats.get("chunks", {}).get("total", 0),
                delta=f"Vectorstore: {stats.get('chunks', {}).get('vectorstore_count', 0)}"
            )
        
        with col3:
            st.metric(
                label="📝 Requirements",
                value=stats.get("requirements", {}).get("total", 0),
                delta="Total toutes phases"
            )
        
        with col4:
            total_size_mb = stats.get("documents", {}).get("total_size", 0) / (1024 * 1024)
            st.metric(
                label="💾 Taille totale",
                value=f"{total_size_mb:.1f} MB",
                delta="Tous documents"
            )
    
    def process_uploaded_files_simple(self, uploaded_files):
        """Version simplifiée du traitement de fichiers"""
        if not uploaded_files:
            return
        
        try:
            # Sauvegarder temporairement les fichiers
            temp_paths = []
            
            for uploaded_file in uploaded_files:
                temp_path = f"temp/{uploaded_file.name}"
                
                # Créer le répertoire temp si nécessaire
                import os
                os.makedirs("temp", exist_ok=True)
                
                # Sauvegarder le fichier
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                temp_paths.append(temp_path)
            
            # Traiter avec le système RAG
            with st.spinner("🔄 Traitement en cours..."):
                if hasattr(self.rag_system, 'add_documents_to_project'):
                    results = self.rag_system.add_documents_to_project(temp_paths)
                else:
                    st.error("❌ Fonction de traitement de documents non disponible")
                    return
            
            # Afficher les résultats de manière simplifiée
            if results.get("errors"):
                st.error(f"❌ Erreurs : {', '.join(results['errors'])}")
            
            if results.get("processed_files"):
                st.success(f"✅ {len(results['processed_files'])} fichier(s) traité(s)!")
                if results.get("new_chunks", 0) > 0:
                    st.info(f"🧩 {results.get('new_chunks', 0)} nouveaux chunks créés")
            
            if results.get("skipped_files"):
                st.info(f"ℹ️ {len(results['skipped_files'])} fichier(s) déjà traité(s)")
            
            # Nettoyer les fichiers temporaires
            for temp_path in temp_paths:
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Erreur lors du traitement : {str(e)}")
    
    def get_project_documents_simple(self, current_project):
        """Récupérer les documents du projet de manière simplifiée"""
        if not hasattr(self.rag_system, 'persistence_service'):
            return []
        
        try:
            return self.rag_system.persistence_service.get_project_documents(current_project.id)
        except Exception as e:
            st.error(f"❌ Erreur récupération documents : {str(e)}")
            return []
    
    def _show_project_statistics(self):
        """Afficher les statistiques du projet dans une modale"""
        if hasattr(self.rag_system, 'get_project_statistics'):
            try:
                stats = self.rag_system.get_project_statistics()
                
                if not stats.get("error"):
                    st.markdown("### 📊 Statistiques détaillées du projet")
                    
                    # Documents
                    docs_stats = stats.get("documents", {})
                    with st.expander("📄 Documents", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total", docs_stats.get("total", 0))
                            st.metric("Taille totale", f"{docs_stats.get('total_size', 0) / 1024 / 1024:.1f} MB")
                        with col2:
                            st.write(f"**Modèle d'embedding :** {docs_stats.get('embedding_model', 'N/A')}")
                            st.write(f"**Types de fichiers :** {', '.join(docs_stats.get('file_types', []))}")
                    
                    # Chunks
                    chunks_stats = stats.get("chunks", {})
                    with st.expander("🧩 Chunks", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total chunks", chunks_stats.get("total", 0))
                            st.metric("Dans vectorstore", chunks_stats.get("vectorstore_count", 0))
                        with col2:
                            avg_size = chunks_stats.get("average_size", 0)
                            st.metric("Taille moyenne", f"{avg_size:.0f} caractères")
                    
                    # Requirements
                    req_stats = stats.get("requirements", {})
                    if req_stats.get("total", 0) > 0:
                        with st.expander("📝 Requirements", expanded=True):
                            st.metric("Total requirements", req_stats.get("total", 0))
                            if req_stats.get("by_phase"):
                                st.write("**Par phase :**")
                                for phase, count in req_stats["by_phase"].items():
                                    st.write(f"- {phase}: {count}")
                else:
                    st.error(f"❌ {stats.get('error', 'Erreur inconnue')}")
            except Exception as e:
                st.error(f"❌ Erreur récupération statistiques : {str(e)}")
        else:
            st.info("🔧 Statistiques non disponibles dans ce mode")
    
    def _handle_project_modals(self, project: Project):
        """Handle project edit and delete modals"""
        # Edit project modal
        if st.session_state.get('show_edit_project_modal', False):
            self._render_edit_project_modal(project)
        
        # Delete project modal
        if st.session_state.get('show_delete_project_modal', False):
            self._render_delete_project_modal(project)
    
    def _render_edit_project_modal(self, project: Project):
        """Render edit project modal"""
        with st.sidebar.container():
            st.markdown("### ✏️ Edit Project")
            
            with st.form("edit_project_form"):
                # Pre-fill with current values
                new_name = st.text_input("Project Name", value=project.name)
                new_description = st.text_area("Description", value=project.description, height=100)
                new_proposal = st.text_area("Proposal Text", value=project.proposal_text, height=150)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        try:
                            # Validate inputs
                            if not new_name.strip():
                                st.error("Project name cannot be empty")
                                return
                            
                            # Update project
                            success = self.rag_system.persistence_service.update_project(
                                project.id,
                                name=new_name.strip() if new_name.strip() != project.name else None,
                                description=new_description.strip() if new_description.strip() != project.description else None,
                                proposal_text=new_proposal.strip() if new_proposal.strip() != project.proposal_text else None
                            )
                            
                            if success:
                                st.success("✅ Project updated successfully!")
                                st.session_state.show_edit_project_modal = False
                                st.rerun()
                            else:
                                st.error("❌ Failed to update project")
                                
                        except Exception as e:
                            st.error(f"❌ Update error: {str(e)}")
                
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.show_edit_project_modal = False
                        st.rerun()
    
    def _render_delete_project_modal(self, project: Project):
        """Render delete project modal with confirmation"""
        with st.sidebar.container():
            st.markdown("### 🗑️ Delete Project")
            st.warning("⚠️ **This action cannot be undone!**")
            
            st.markdown(f"""
            **Project to delete:** {project.name}
            
            This will permanently delete:
            • All project documents and chunks
            • All requirements and analyses
            • All stakeholder information
            • All project history
            """)
            
            with st.form("delete_project_form"):
                # Confirmation inputs
                confirm_delete = st.checkbox("I understand this action is irreversible")
                confirmation_text = st.text_input(
                    "Type the project name to confirm deletion",
                    placeholder=project.name
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("🗑️ DELETE PROJECT", type="secondary"):
                        if not confirm_delete:
                            st.error("Please confirm you understand this action is irreversible")
                            return
                        
                        if confirmation_text != project.name:
                            st.error("Project name doesn't match. Please type the exact project name.")
                            return
                        
                        try:
                            # Delete project
                            success = self.rag_system.persistence_service.delete_project(project.id)
                            
                            if success:
                                st.success("✅ Project deleted successfully!")
                                st.session_state.show_delete_project_modal = False
                                
                                # Clear current project
                                if hasattr(self.rag_system, 'current_project'):
                                    self.rag_system.current_project = None
                                
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete project")
                                
                        except Exception as e:
                            st.error(f"❌ Delete error: {str(e)}")
                
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.show_delete_project_modal = False
                        st.rerun()
    
    def render_enhanced_project_list(self) -> Dict[str, Any]:
        """Render enhanced project list with CRUD operations"""
        if not self.has_persistence:
            st.warning("🔧 Traditional mode - Enhanced project list not available")
            return {}
        
        try:
            projects = self.rag_system.get_all_projects()
        except Exception as e:
            st.error(f"❌ Error loading projects: {str(e)}")
            return {}
        
        st.markdown("### 📋 All Projects")
        
        if not projects:
            st.info("📭 No projects found. Create your first project!")
            return {}
        
        # Enhanced project list with actions
        for project in projects:
            with st.container():
                # Project header
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**📋 {project.name}**")
                    if project.description:
                        st.caption(project.description[:100] + "..." if len(project.description) > 100 else project.description)
                    
                    # Project stats
                    stats_text = f"📄 {project.documents_count} docs • 📝 {project.requirements_count} reqs"
                    st.caption(stats_text)
                
                with col2:
                    st.caption(f"Created: {project.created_at.strftime('%d/%m/%Y')}")
                    st.caption(f"Updated: {project.updated_at.strftime('%d/%m/%Y')}")
                
                with col3:
                    # Action buttons
                    if st.button("📂 Select", key=f"select_{project.id}"):
                        if hasattr(self.rag_system, 'load_project'):
                            self.rag_system.load_project(project.id)
                        st.success(f"Selected: {project.name}")
                        st.rerun()
                    
                    if st.button("✏️ Edit", key=f"edit_{project.id}"):
                        st.session_state.current_editing_project = project.id
                        st.session_state.show_edit_project_modal = True
                        st.rerun()
                
                st.markdown("---")
        
        return {"projects": projects, "total": len(projects)}
    
    def validate_project_data(self, name: str, description: str = "", proposal_text: str = "") -> tuple[bool, str]:
        """Validate project data before creation/update"""
        # Name validation
        if not name or not name.strip():
            return False, "Project name is required"
        
        if len(name.strip()) < 3:
            return False, "Project name must be at least 3 characters long"
        
        if len(name.strip()) > 100:
            return False, "Project name must be less than 100 characters"
        
        # Description validation
        if description and len(description) > 1000:
            return False, "Description must be less than 1000 characters"
        
        # Proposal text validation
        if proposal_text and len(proposal_text) > 5000:
            return False, "Proposal text must be less than 5000 characters"
        
        # Check for duplicate names
        try:
            existing_projects = self.rag_system.get_all_projects()
            for project in existing_projects:
                if project.name.lower().strip() == name.lower().strip():
                    return False, f"A project with the name '{name}' already exists"
        except Exception as e:
            # If we can't check for duplicates, still allow creation
            pass
        
        return True, "Valid"
    
    def export_project_data(self, project: Project) -> dict:
        """Export project data for backup or migration"""
        try:
            export_data = {
                "project_info": {
                    "name": project.name,
                    "description": project.description,
                    "proposal_text": project.proposal_text,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat()
                },
                "documents": [],
                "requirements": {},
                "stakeholders": [],
                "sessions": []
            }
            
            # Export documents
            if hasattr(self.rag_system, 'persistence_service'):
                try:
                    documents = self.rag_system.persistence_service.get_project_documents(project.id)
                    export_data["documents"] = [
                        {
                            "filename": doc.filename,
                            "file_size": doc.file_size,
                            "chunks_count": doc.chunks_count,
                            "processing_status": doc.processing_status,
                            "processed_at": doc.processed_at.isoformat()
                        }
                        for doc in documents
                    ]
                except Exception as e:
                    export_data["documents"] = f"Error loading documents: {str(e)}"
                
                # Export requirements
                try:
                    requirements = self.rag_system.persistence_service.get_project_requirements(project.id)
                    export_data["requirements"] = requirements
                except Exception as e:
                    export_data["requirements"] = f"Error loading requirements: {str(e)}"
                
                # Export stakeholders
                try:
                    stakeholders = self.rag_system.persistence_service.get_project_stakeholders(project.id)
                    export_data["stakeholders"] = stakeholders
                except Exception as e:
                    export_data["stakeholders"] = f"Error loading stakeholders: {str(e)}"
                
                # Export recent sessions
                try:
                    sessions = self.rag_system.persistence_service.get_project_sessions(project.id, limit=20)
                    export_data["sessions"] = sessions
                except Exception as e:
                    export_data["sessions"] = f"Error loading sessions: {str(e)}"
            
            return export_data
            
        except Exception as e:
            return {"error": f"Export failed: {str(e)}"}
    
    def get_project_health_check(self, project: Project) -> dict:
        """Perform health check on project data"""
        health_check = {
            "status": "healthy",
            "issues": [],
            "recommendations": [],
            "score": 100
        }
        
        try:
            # Check if project has documents
            if hasattr(self.rag_system, 'persistence_service'):
                documents = self.rag_system.persistence_service.get_project_documents(project.id)
                
                if not documents:
                    health_check["issues"].append("No documents uploaded")
                    health_check["recommendations"].append("Upload project documents to enable full functionality")
                    health_check["score"] -= 30
                
                # Check document processing status
                processing_docs = [doc for doc in documents if doc.processing_status != "completed"]
                if processing_docs:
                    health_check["issues"].append(f"{len(processing_docs)} documents still processing")
                    health_check["recommendations"].append("Wait for document processing to complete")
                    health_check["score"] -= 10
                
                # Check requirements
                requirements = self.rag_system.persistence_service.get_project_requirements(project.id)
                if not requirements.get("requirements"):
                    health_check["issues"].append("No requirements generated")
                    health_check["recommendations"].append("Generate requirements using the Requirements & Analysis tab")
                    health_check["score"] -= 20
                
                # Check stakeholders
                stakeholders = self.rag_system.persistence_service.get_project_stakeholders(project.id)
                if not stakeholders:
                    health_check["issues"].append("No stakeholders identified")
                    health_check["recommendations"].append("Identify and document project stakeholders")
                    health_check["score"] -= 15
            
            # Determine overall status
            if health_check["score"] >= 80:
                health_check["status"] = "healthy"
            elif health_check["score"] >= 60:
                health_check["status"] = "warning"
            else:
                health_check["status"] = "critical"
                
        except Exception as e:
            health_check["status"] = "error"
            health_check["issues"].append(f"Health check failed: {str(e)}")
            health_check["score"] = 0
        
        return health_check