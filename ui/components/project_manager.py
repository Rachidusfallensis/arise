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
        
        # Project creation section
        if self.has_project_management:
            with st.sidebar.expander("➕ New Project", expanded=False):
                with st.form("new_project_form"):
                    new_name = st.text_input("Project Name", placeholder="My new MBSE project")
                    new_description = st.text_area("Description", placeholder="Project description...")
                    new_proposal = st.text_area("Proposal Text", placeholder="Initial proposal text...")
                    
                    if st.form_submit_button("Create Project", type="primary"):
                        if new_name.strip():
                            try:
                                project_id = self.rag_system.create_project(
                                    name=new_name.strip(),
                                    description=new_description.strip(),
                                    proposal_text=new_proposal.strip()
                                )
                                st.sidebar.success(f"✅ Project created: {new_name}")
                                st.sidebar.balloons()
                                st.rerun()
                            except Exception as e:
                                st.sidebar.error(f"❌ Error: {str(e)}")
                        else:
                            st.sidebar.error("Project name is required")
        
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
        """Display project information in the sidebar"""
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