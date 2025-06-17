import streamlit as st
import os
import json
import sys
from pathlib import Path
from datetime import datetime
import time

# Add the project root to Python path for proper imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.rag_system import SAFEMBSERAGSystem
from src.core.enhanced_structured_rag_system import EnhancedStructuredRAGSystem
from src.services.evaluation_service import EvaluationService
from config import config, arcadia_config
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging

# Configure logging for terminal output (Streamlit-compatible)
import os
from pathlib import Path

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Clear any existing handlers
logging.getLogger().handlers.clear()

# Configure logging with force and explicit stream
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # Use stderr instead of stdout for Streamlit
        logging.FileHandler('logs/requirements_generation.log', mode='a')
    ],
    force=True  # Force reconfiguration
)

# Create logger with explicit configuration
logger = logging.getLogger("ARCADIA_RAG_System")
logger.setLevel(logging.INFO)

# Add console handler if not already present
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Test logging on startup
logger.info("Logger initialized successfully - terminal logging active")

# Page configuration
st.set_page_config(
    page_title="ARCADIA Requirements Generator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS styling
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #2c5aa0 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 300;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e1e5e9;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #2c5aa0 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 2rem;
        font-weight: 300;
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Requirements display */
    .requirement-item {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .requirement-header {
        font-weight: 600;
        font-size: 1.1rem;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .requirement-description {
        color: #666;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .requirement-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.9rem;
    }
    
    .priority-high { color: #e74c3c; font-weight: 600; }
    .priority-medium { color: #f39c12; font-weight: 600; }
    .priority-low { color: #27ae60; font-weight: 600; }
    
    /* Chat interface */
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e1e5e9;
    }
    
    .chat-message {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        background: #f8f9fa;
    }
    
    .user-message {
        border-left-color: #667eea;
        background: linear-gradient(135deg, #667eea 0%, #2c5aa0 100%);
        color: white;
        margin-left: 2rem;
    }
    
    .assistant-message {
        border-left-color: #27ae60;
        background: #f8f9fa;
        margin-right: 2rem;
    }
    
    .source-citation {
        background: #e8f4f8;
        border: 1px solid #d1ecf1;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* Phase headers */
    .phase-section {
        background: linear-gradient(90deg, #667eea 0%, #2c5aa0 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
    }
    
    .phase-section h3 {
        margin: 0;
        font-weight: 400;
    }
    
    /* Structured analysis styling */
    .analysis-overview {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    
    .actor-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .capability-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .function-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .traceability-link {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .gap-analysis {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .gap-critical {
        background: #f8d7da;
        border-color: #f5c6cb;
    }
    
    .gap-major {
        background: #fff3cd;
        border-color: #ffeaa7;
    }
    
    .gap-minor {
        background: #d1ecf1;
        border-color: #bee5eb;
    }
    
    /* Enhanced metrics */
    .enhanced-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .enhanced-metric h3 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 300;
    }
    
    .enhanced-metric p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #2c5aa0 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed #667eea;
        border-radius: 8px;
        padding: 1rem;
        background: #f8f9fa;
    }
    
    /* Progress indicators */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #2c5aa0 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #2c5aa0 100%);
        color: white;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# ARCADIA methodology reference links
ARCADIA_REFERENCES = {
    "Getting Started": "https://gettingdesignright.com/GDR-Educate/Capella_Tutorial_v6_0/GettingStarted.html",
    "Installation": "https://gettingdesignright.com/GDR-Educate/Capella_Tutorial_v6_0/GettingStarted.html#Installation",
    "Operational Analysis": "https://gettingdesignright.com/GDR-Educate/Capella_Tutorial_v6_0/OperationalAnalysis.html",
    "System Analysis": "https://gettingdesignright.com/GDR-Educate/Capella_Tutorial_v6_0/SystemAnalysis.html",
    "Logical Architecture": "https://gettingdesignright.com/GDR-Educate/Capella_Tutorial_v6_0/LogicalArchitecture.html",
    "Physical Architecture": "https://gettingdesignright.com/GDR-Educate/Capella_Tutorial_v6_0/PhysicalArchitecture.html"
}

# MBSE context prompts for better responses
MBSE_CONTEXT_PROMPTS = {
    "operational": "Focus on operational activities, actors, and capabilities from an Operational Analysis perspective.",
    "system": "Consider system functions, interfaces, and requirements from a System Analysis viewpoint.",
    "logical": "Analyze logical components, their interactions, and behavioral aspects from a Logical Architecture perspective.",
    "physical": "Examine physical components, deployment, and implementation from a Physical Architecture standpoint.",
    "verification": "Address verification and validation approaches for MBSE artifacts.",
    "traceability": "Consider traceability links between different architectural levels."
}

# Initialize services
@st.cache_resource
def init_services(use_enhanced=True):
    """Initialize and cache the RAG system and evaluation service"""
    try:
        if use_enhanced:
            rag_system = EnhancedStructuredRAGSystem()
            logger.info("Enhanced Structured RAG System initialized successfully")
        else:
            rag_system = SAFEMBSERAGSystem()
            logger.info("Traditional RAG System initialized successfully")
        
        eval_service = EvaluationService()
        logger.info("Services initialized successfully with caching")
        return rag_system, eval_service, use_enhanced
    except Exception as e:
        logger.error(f"Error initializing enhanced services: {str(e)}")
        logger.info("Falling back to traditional RAG system")
        # Fallback to traditional system if enhanced fails
        return SAFEMBSERAGSystem(), EvaluationService(), False

def load_chats():
    """Load saved chats from file"""
    chats_file = Path("data/saved_chats.json")
    chats_file.parent.mkdir(parents=True, exist_ok=True)
    if chats_file.exists():
        try:
            with open(chats_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading chats: {str(e)}")
            return {}
    return {}

def save_chats(chats):
    """Save chats to file"""
    try:
        chats_file = Path("data/saved_chats.json")
        chats_file.parent.mkdir(parents=True, exist_ok=True)
        with open(chats_file, "w", encoding="utf-8") as f:
            json.dump(chats, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(chats)} chat sessions")
    except Exception as e:
        logger.error(f"Error saving chats: {str(e)}")

def get_enhanced_prompt(user_prompt, context_type=None):
    """Enhance user prompt with MBSE context"""
    if context_type and context_type != "None" and context_type in MBSE_CONTEXT_PROMPTS:
        enhanced_prompt = f"{MBSE_CONTEXT_PROMPTS[context_type]}\n\nUser Question: {user_prompt}"
        return enhanced_prompt
    return user_prompt

def display_arcadia_references():
    """Display Arcadia methodology reference links"""
    st.markdown("### ARCADIA Methodology References")
    st.markdown("Educational resources for each ARCADIA phase:")
    for phase, url in ARCADIA_REFERENCES.items():
        st.markdown(f"• [{phase}]({url})")

def get_fallback_example(example_type: str) -> str:
    """Provide fallback examples when files are not available."""
    
    if example_type == "safe":
        return """
# Systems Engineering Project Proposal

## Project Overview
Development of an intelligent transportation management system for smart city infrastructure using Model-Based Systems Engineering (MBSE) approach.

## Objectives
1. Design integrated traffic management system following ARCADIA methodology
2. Implement real-time traffic optimization algorithms  
3. Create stakeholder-centric interface for city operators
4. Establish quality assessment framework for system requirements

## Stakeholders
- Traffic Control Operators: Monitor and manage traffic flow
- City Planners: Strategic planning and infrastructure development
- Emergency Services: Priority routing and incident response
- Citizens: End users expecting efficient transportation

## Work Packages
WP1: Operational Analysis - Define stakeholder needs and use cases
WP2: System Analysis - Specify system-level functions and requirements
WP3: Logical Architecture - Design logical components and interfaces
WP4: Physical Architecture - Define implementation and deployment

## Technical Requirements
- The system shall process traffic data from 500+ sensors in real-time
- Response time for traffic signal adjustments must be under 2 seconds  
- System availability shall be 99.9% or higher
- Integration with emergency services dispatch systems is mandatory
"""
    
    elif example_type == "cyderco":
        return """
# Cybersecurity Infrastructure Project

## Project Description  
CYDERCO (Cyber Defense and Response Coordination) serves as a reference implementation for critical infrastructure protection systems.

## Mission Statement
Develop comprehensive cyber defense capabilities that can detect, analyze, and respond to sophisticated threats targeting critical infrastructure.

## Key Objectives
1. Implement advanced threat detection using machine learning
2. Develop automated incident response protocols
3. Create real-time monitoring and alerting systems
4. Establish coordination mechanisms for multi-agency response

## Stakeholders
- Security Operations Center (SOC) Analysts: Threat monitoring and analysis
- Incident Response Teams: Handle and contain security incidents  
- Infrastructure Operators: Maintain critical systems security
- Regulatory Bodies: Ensure compliance with security standards

## Functional Requirements
- Threat detection algorithms shall identify anomalies within 5 seconds
- Automated response must activate within 30 seconds of confirmed threat
- All security events must be logged for forensic analysis
- System shall integrate with existing SIEM platforms

## Non-Functional Requirements
- System availability must exceed 99.99%
- Threat detection accuracy shall be above 95%
- False positive rate must be below 2%
- Data encryption required for all communications
"""
    
    else:  # simple example
        return """
# Industrial Automation System

## Project Goal
Design and implement an intelligent manufacturing automation system that optimizes production efficiency while ensuring worker safety.

## Objectives
1. Automate production line operations and quality control
2. Implement predictive maintenance capabilities
3. Develop safety monitoring and emergency response systems
4. Create operator interface for system management

## Stakeholders
- Production Managers: Oversee manufacturing operations and efficiency
- Machine Operators: Interface with automated systems daily
- Quality Assurance Teams: Monitor and validate product quality
- Safety Officers: Ensure compliance with safety regulations

## System Requirements
- The system shall monitor production line status in real-time
- Predictive maintenance algorithms must forecast equipment failures 48 hours in advance
- Emergency stop functionality shall halt all operations within 0.5 seconds
- Quality control systems must inspect 100% of manufactured products
- Operator interfaces should provide intuitive control and monitoring capabilities
"""

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>ARCADIA Requirements Generator</h1>
        <p>AI-Driven Requirements Generation using ARCADIA Methodology & RAG</p>
    </div>
    """, unsafe_allow_html=True)
    
    logger.info("=== ARCADIA Requirements Generator Started ===")
    
    # Initialize services
    rag_system, eval_service, is_enhanced = init_services(use_enhanced=True)
    logger.info("Core services initialized successfully")
    
    # Initialize chat system in session state
    if "chats" not in st.session_state:
        st.session_state.chats = load_chats()
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### Configuration")
        
        # Phase selection
        target_phase = st.selectbox(
            "Target ARCADIA Phase",
            ["all"] + list(arcadia_config.ARCADIA_PHASES.keys()),
            format_func=lambda x: "All Phases" if x == "all" else arcadia_config.ARCADIA_PHASES[x]["name"]
        )
        
        # Requirement types
        req_types = st.multiselect(
            "Requirement Types",
            ["functional", "non_functional", "stakeholder"],
            default=["functional", "non_functional"]
        )
        
        # Enhanced Analysis Options (only if enhanced system is available)
        if is_enhanced:
            st.markdown("#### Enhanced Analysis")
            enable_structured_analysis = st.checkbox(
                "Enable Structured ARCADIA Analysis",
                value=True,
                help="Generate structured analysis with actors, capabilities, and cross-phase traceability"
            )
            enable_cross_phase_analysis = st.checkbox(
                "Enable Cross-Phase Analysis", 
                value=True,
                help="Perform traceability analysis, gap detection, and quality metrics across ARCADIA phases"
            )
        else:
            enable_structured_analysis = False
            enable_cross_phase_analysis = False
        
        # Export format
        export_formats = config.REQUIREMENTS_OUTPUT_FORMATS + ["ARCADIA_JSON", "Structured_Markdown"]
        export_format = st.selectbox(
            "Export Format",
            export_formats
        )
        
        st.markdown("---")
        
        # ARCADIA references
        display_arcadia_references()
        
        st.markdown("---")
        
        # Debug options (only in development)
        st.markdown("### Debug Options")
        if st.button("Clear Service Cache"):
            st.cache_resource.clear()
            st.success("Cache cleared! Please refresh the page.")
        
        if st.button("Test RAG System"):
            try:
                test_rag = SAFEMBSERAGSystem()
                st.success("RAG system can be initialized")
            except Exception as e:
                st.error(f"RAG system error: {str(e)}")
    
    # Main interface tabs
    if is_enhanced:
        tab1, tab2, tab3, tab4 = st.tabs([
            "Generate Requirements", 
            "Structured ARCADIA Analysis",
            "Chat with Documents", 
            "Evaluation"
        ])
        
        with tab1:
            generate_requirements_tab(rag_system, target_phase, req_types, export_format, 
                                    enable_structured_analysis, enable_cross_phase_analysis, is_enhanced)
        
        with tab2:
            structured_arcadia_tab(rag_system)
        
        with tab3:
            chat_tab(rag_system)
        
        with tab4:
            evaluation_tab(rag_system, eval_service)
    else:
        tab1, tab2, tab3 = st.tabs([
            "Generate Requirements", 
            "Chat with Documents", 
            "Evaluation"
        ])
        
        with tab1:
            generate_requirements_tab(rag_system, target_phase, req_types, export_format, 
                                    False, False, is_enhanced)
        
        with tab2:
            chat_tab(rag_system)
        
        with tab3:
            evaluation_tab(rag_system, eval_service)

def generate_requirements_tab(rag_system, target_phase, req_types, export_format, 
                             enable_structured_analysis=False, enable_cross_phase_analysis=False, is_enhanced=False):
    st.markdown("### Requirements Generation")
    
    # Clear any previous file upload errors
    if 'upload_error' in st.session_state:
        del st.session_state['upload_error']
    
    # Input methods
    input_method = st.radio(
        "Input Method",
        ["Upload Document", "Paste Text", "Load Example"],
        key="input_method_radio"
    )
    
    proposal_text = ""
    
    if input_method == "Upload Document":
        st.markdown("#### Document Upload")
        
        # Add file size warning
        st.info("Maximum file size: 50MB • Supported formats: TXT, MD, PDF, DOCX")
        
        # Add error handling wrapper for file upload
        try:
            uploaded_file = st.file_uploader(
                "Upload project proposal",
                type=['txt', 'md', 'pdf', 'docx'],
                help="Upload your project proposal document",
                accept_multiple_files=False,
                key="document_uploader"
            )
            logger.info("File uploader component rendered successfully")
            
        except Exception as upload_error:
            logger.error(f"File uploader component error: {str(upload_error)}")
            st.error("File upload component error. Please refresh the page and try again.")
            uploaded_file = None
        
        if uploaded_file is not None:
            logger.info(f"File upload initiated: {uploaded_file.name}")
            logger.info(f"   • File type: {uploaded_file.type}")
            logger.info(f"   • File size: {uploaded_file.size} bytes ({uploaded_file.size / 1024 / 1024:.2f} MB)")
            
            # Check file size limit (50MB)
            max_size_mb = 50
            if uploaded_file.size > max_size_mb * 1024 * 1024:
                error_msg = f"File too large: {uploaded_file.size / 1024 / 1024:.2f} MB (max: {max_size_mb} MB)"
                logger.error(f"{error_msg}")
                st.error(error_msg)
                proposal_text = ""
            else:
                try:
                    logger.info("Starting document processing...")
                    
                    # Process uploaded file based on type
                    if uploaded_file.type == "text/plain" or uploaded_file.name.endswith('.txt'):
                        logger.info("Processing TXT file...")
                        file_content = uploaded_file.read()
                        logger.info(f"   • Raw content size: {len(file_content)} bytes")
                        proposal_text = str(file_content, "utf-8")
                        logger.info(f"TXT file processed successfully: {len(proposal_text)} characters")
                        
                    elif uploaded_file.name.endswith('.md'):
                        logger.info("Processing Markdown file...")
                        file_content = uploaded_file.read()
                        logger.info(f"   • Raw content size: {len(file_content)} bytes")
                        proposal_text = str(file_content, "utf-8")
                        logger.info(f"Markdown file processed successfully: {len(proposal_text)} characters")
                        
                    elif uploaded_file.type == "application/pdf" or uploaded_file.name.endswith('.pdf'):
                        logger.info("Processing PDF file...")
                        try:
                            import PyPDF2
                            import io
                            
                            # Read file content
                            file_content = uploaded_file.read()
                            logger.info(f"   • PDF raw size: {len(file_content)} bytes")
                            
                            # Create PDF reader
                            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                            logger.info(f"   • PDF pages detected: {len(pdf_reader.pages)}")
                            
                            proposal_text = ""
                            for page_num, page in enumerate(pdf_reader.pages):
                                logger.info(f"   • Processing page {page_num + 1}...")
                                try:
                                    page_text = page.extract_text()
                                    proposal_text += page_text + "\n"
                                    logger.info(f"     - Page {page_num + 1}: {len(page_text)} characters extracted")
                                except Exception as page_error:
                                    logger.warning(f"     - Page {page_num + 1} extraction failed: {str(page_error)}")
                            
                            if not proposal_text.strip():
                                logger.warning("PDF text extraction yielded empty result")
                                st.error("Could not extract text from PDF. The PDF might be image-based or encrypted. Please try copy-paste instead.")
                                proposal_text = ""
                            else:
                                logger.info(f"PDF processed successfully: {len(pdf_reader.pages)} pages, {len(proposal_text)} characters")
                                
                        except Exception as e:
                            logger.error(f"PDF processing error: {str(e)}")
                            logger.error(f"   • Error type: {type(e).__name__}")
                            st.error(f"Error processing PDF file: {str(e)}. Try using a different PDF or copy-paste the text.")
                            proposal_text = ""
                            
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or uploaded_file.name.endswith('.docx'):
                        logger.info("Processing DOCX file...")
                        try:
                            from docx import Document
                            import io
                            
                            # Read file content
                            file_content = uploaded_file.read()
                            logger.info(f"   • DOCX raw size: {len(file_content)} bytes")
                            
                            # Create document reader
                            doc = Document(io.BytesIO(file_content))
                            logger.info(f"   • DOCX paragraphs detected: {len(doc.paragraphs)}")
                            
                            proposal_text = ""
                            for para_num, paragraph in enumerate(doc.paragraphs):
                                para_text = paragraph.text
                                proposal_text += para_text + "\n"
                                if para_text.strip():  # Only log non-empty paragraphs
                                    logger.info(f"     - Paragraph {para_num + 1}: {len(para_text)} characters")
                                
                            if not proposal_text.strip():
                                logger.warning("DOCX text extraction yielded empty result")
                                st.error("Could not extract text from DOCX. The document might be empty or contain only images.")
                                proposal_text = ""
                            else:
                                logger.info(f"DOCX processed successfully: {len(doc.paragraphs)} paragraphs, {len(proposal_text)} characters")
                                
                        except Exception as e:
                            logger.error(f"DOCX processing error: {str(e)}")
                            logger.error(f"   • Error type: {type(e).__name__}")
                            st.error(f"Error processing DOCX file: {str(e)}. Try using a different file or copy-paste the text.")
                            proposal_text = ""
                            
                    else:
                        logger.warning(f"Unsupported file type: {uploaded_file.type}")
                        st.error(f"Unsupported file type: {uploaded_file.type}. Please upload TXT, MD, PDF, or DOCX files.")
                        proposal_text = ""
                        
                    # Show file info if successfully processed
                    if proposal_text:
                        st.success(f"File processed: {uploaded_file.name} ({len(proposal_text)} characters)")
                        logger.info(f"Document processing completed successfully!")
                        
                        # Show preview of extracted text
                        with st.expander("Preview extracted text (first 500 characters)"):
                            preview_text = proposal_text[:500] + "..." if len(proposal_text) > 500 else proposal_text
                            st.text(preview_text)
                        
                except Exception as e:
                    logger.error(f"File processing error: {str(e)}")
                    logger.error(f"   • Error type: {type(e).__name__}")
                    logger.error(f"   • Full traceback: ", exc_info=True)
                    st.error(f"Error reading file: {str(e)}")
                    proposal_text = ""
    
    elif input_method == "Paste Text":
        proposal_text = st.text_area(
            "Paste your project proposal text",
            height=300,
            help="Paste the text of your project proposal here"
        )
    
    elif input_method == "Load Example":
        example_choice = st.selectbox(
            "Choose Example",
            ["Transportation System", "Cybersecurity Infrastructure", "Industrial Automation"]
        )
        
        if st.button("Load Example"):
            try:
                if example_choice == "Transportation System":
                    # Load transportation system example
                    example_path = Path("data/examples/transportation_system.md")
                    if example_path.exists():
                        with open(example_path, "r", encoding="utf-8") as f:
                            proposal_text = f.read()
                    else:
                        st.info("Using built-in transportation system example.")
                        proposal_text = get_fallback_example("safe")
                        
                elif example_choice == "Cybersecurity Infrastructure":
                    # Load cybersecurity example (CYDERCO reference)
                    example_path = Path("data/examples/cyberco_reference.md")
                    if example_path.exists():
                        with open(example_path, "r", encoding="utf-8") as f:
                            proposal_text = f.read()
                    else:
                        st.info("Using built-in cybersecurity infrastructure example (CYDERCO reference).")
                        proposal_text = get_fallback_example("cyderco")
                        
                else:  # Industrial Automation
                    proposal_text = get_fallback_example("simple")
                    st.info("Using built-in industrial automation example.")
                    
                if proposal_text:
                    st.success(f"Example loaded: {example_choice}")
                    logger.info(f"Loaded example: {example_choice} ({len(proposal_text)} characters)")
                    
            except Exception as e:
                st.error(f"Error loading example: {str(e)}")
                logger.error(f"Error loading example {example_choice}: {str(e)}")
                proposal_text = get_fallback_example("simple")
    
    # Generation controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### Generation Parameters")
        
        # Advanced options
        with st.expander("Advanced Options"):
            max_requirements = st.slider("Max Requirements per Type", 5, 50, 20)
            include_rationale = st.checkbox("Include Rationale", True)
            include_verification = st.checkbox("Include Verification Methods", True)
            quality_threshold = st.slider("Quality Threshold", 0.5, 1.0, 0.7)
    
    with col2:
        st.markdown("#### Actions")
        generate_btn = st.button("Generate Requirements", type="primary")
        
        if proposal_text:
            st.success(f"Input ready ({len(proposal_text)} characters)")
    
    # Generation process
    if generate_btn and proposal_text:
        start_time = time.time()
        
        logger.info("Starting requirements generation process...")
        logger.info(f"Input: {len(proposal_text)} characters, Target Phase: {target_phase}, Types: {req_types}")
        logger.info(f"Generation started at: {datetime.now().strftime('%H:%M:%S')}")
        
        with st.spinner("Generating requirements..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Analyze proposal
            step1_start = time.time()
            status_text.text("Analyzing proposal...")
            logger.info("Step 1: Analyzing project proposal and extracting context...")
            progress_bar.progress(20)
            
            # Step 2: Generate requirements
            step2_start = time.time()
            step1_duration = step2_start - step1_start
            logger.info(f"Step 1 completed in {step1_duration:.1f} seconds")
            
            status_text.text("Generating requirements...")
            logger.info("Step 2: Initiating AI-driven requirements generation...")
            logger.info(f"Targeting ARCADIA phases: {target_phase}")
            logger.info(f"Requirement types: {', '.join(req_types)}")
            logger.info("Note: This may take several minutes due to LLM processing time...")
            
            # Estimate time based on phases and types
            phases_to_process = [target_phase] if target_phase != "all" else list(arcadia_config.ARCADIA_PHASES.keys())
            estimated_calls = len(phases_to_process) * len(req_types) + 1  # +1 for stakeholders
            logger.info(f"Estimated LLM calls: {estimated_calls} (each may take 30-120 seconds)")
            logger.info(f"Estimated total time: {estimated_calls * 60 / 60:.1f}-{estimated_calls * 120 / 60:.1f} minutes")
            
            progress_bar.progress(60)
            
            try:
                if is_enhanced and hasattr(rag_system, 'generate_enhanced_requirements_from_proposal'):
                    # Use enhanced generation with structured analysis
                    results = rag_system.generate_enhanced_requirements_from_proposal(
                        proposal_text=proposal_text,
                        target_phase=target_phase,
                        requirement_types=req_types,
                        enable_structured_analysis=enable_structured_analysis,
                        enable_cross_phase_analysis=enable_cross_phase_analysis
                    )
                    # Store enhanced results for the new tab
                    st.session_state['enhanced_results'] = results
                    logger.info(f"Enhanced generation completed - Traditional requirements: {len(results.get('requirements', {}))}")
                else:
                    # Use traditional generation
                    results = rag_system.generate_requirements_from_proposal(
                        proposal_text, target_phase, req_types
                    )
                    logger.info(f"Traditional generation completed - Requirements: {len(results.get('requirements', {}))}")
                
                step3_start = time.time()
                step2_duration = step3_start - step2_start
                logger.info(f"Step 2 completed in {step2_duration:.1f} seconds ({step2_duration/60:.1f} minutes)")
                logger.info("Requirements generation completed successfully")
                
                # Log generation statistics
                stats = results.get('statistics', {})
                total_reqs = stats.get('total_requirements', 0)
                logger.info(f"Generation Statistics:")
                logger.info(f"   • Total Requirements Generated: {total_reqs}")
                logger.info(f"   • Phases Covered: {len(results.get('requirements', {}))}")
                logger.info(f"   • Stakeholders Identified: {len(results.get('stakeholders', {}))}")
                
                # Log priority distribution
                priority_dist = stats.get('by_priority', {})
                logger.info(f"   • Priority Distribution:")
                logger.info(f"     - MUST (Critical): {priority_dist.get('MUST', 0)}")
                logger.info(f"     - SHOULD (Important): {priority_dist.get('SHOULD', 0)}")
                logger.info(f"     - COULD (Nice-to-have): {priority_dist.get('COULD', 0)}")
                
                # Log requirements by phase and type
                for phase, phase_reqs in results.get('requirements', {}).items():
                    phase_total = sum(len(reqs) if isinstance(reqs, list) else 0 for reqs in phase_reqs.values())
                    logger.info(f"   • {phase.upper()} Phase: {phase_total} requirements")
                    for req_type, reqs in phase_reqs.items():
                        count = len(reqs) if isinstance(reqs, list) else 0
                        logger.info(f"     - {req_type}: {count} requirements")
                
            except Exception as e:
                logger.error(f"Error during requirements generation: {str(e)}")
                st.error(f"Error during generation: {str(e)}")
                return
            
            # Step 3: Post-processing
            status_text.text("Post-processing...")
            logger.info("Step 3: Post-processing and quality validation...")
            progress_bar.progress(80)
            
            progress_bar.progress(100)
            status_text.text("Generation completed!")
            
            # Calculate total time
            total_time = time.time() - start_time
            logger.info(f"Requirements generation process completed successfully!")
            logger.info(f"Total generation time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
            logger.info(f"Completed at: {datetime.now().strftime('%H:%M:%S')}")
            
            # Store results in session state
            st.session_state['generation_results'] = results
            st.session_state['proposal_text'] = proposal_text
            st.session_state['generation_time'] = total_time
    
    # Display results
    if 'generation_results' in st.session_state:
        results = st.session_state['generation_results']
        display_generation_results(results, export_format, rag_system)

def display_generation_results(results, export_format, rag_system):
    st.markdown("### Generated Requirements")
    
    # Performance information
    if 'generation_time' in st.session_state:
        generation_time = st.session_state['generation_time']
        with st.expander("Performance Information"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Generation Time", f"{generation_time:.1f}s")
            with col2:
                st.metric("Time (minutes)", f"{generation_time/60:.1f}min")
            with col3:
                avg_per_req = generation_time / max(1, results.get('statistics', {}).get('total_requirements', 1))
                st.metric("Avg per Requirement", f"{avg_per_req:.1f}s")
            
            st.info("""
            **Why does generation take time?**
            - Each ARCADIA phase requires separate LLM processing
            - Complex reasoning for requirements quality and traceability  
            - Multiple requirement types (functional, non-functional, stakeholder)
            - Network latency to Ollama server
            """)
    
    # Statistics overview
    stats = results.get('statistics', {})
    priority_dist = stats.get('by_priority', {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Requirements", stats.get('total_requirements', 0))
    with col2:
        st.metric("Stakeholders", len(results.get('stakeholders', {})))
    with col3:
        st.metric("Phases Covered", len(results.get('requirements', {})))
    with col4:
        st.metric("Quality Score", f"{stats.get('average_quality', 0):.1%}")
    
    # Priority distribution overview
    if priority_dist:
        st.markdown("#### Priority Distribution Analysis")
        
        priority_col1, priority_col2, priority_col3 = st.columns(3)
        total_reqs = max(stats.get('total_requirements', 1), 1)
        
        with priority_col1:
            must_count = priority_dist.get('MUST', 0)
            must_percentage = (must_count / total_reqs) * 100
            st.metric("MUST (Critical)", must_count, delta=f"{must_percentage:.1f}%")
            
        with priority_col2:
            should_count = priority_dist.get('SHOULD', 0)
            should_percentage = (should_count / total_reqs) * 100
            st.metric("SHOULD (Important)", should_count, delta=f"{should_percentage:.1f}%")
            
        with priority_col3:
            could_count = priority_dist.get('COULD', 0)
            could_percentage = (could_count / total_reqs) * 100
            st.metric("COULD (Nice-to-have)", could_count, delta=f"{could_percentage:.1f}%")
        
        # Priority distribution chart
        import plotly.express as px
        priority_data = pd.DataFrame([
            {"Priority": "MUST (Critical)", "Count": must_count, "Percentage": must_percentage},
            {"Priority": "SHOULD (Important)", "Count": should_count, "Percentage": should_percentage},
            {"Priority": "COULD (Nice-to-have)", "Count": could_count, "Percentage": could_percentage}
        ])
        
        if priority_data['Count'].sum() > 0:
            fig = px.pie(priority_data, values='Count', names='Priority', 
                       title="Requirements Priority Distribution (ARCADIA-Compliant)",
                       color_discrete_map={
                           "MUST (Critical)": "#FF4B4B",
                           "SHOULD (Important)": "#FFA500", 
                           "COULD (Nice-to-have)": "#00D4AA"
                       })
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Expected vs actual distribution analysis
            st.info("""
            **ARCADIA Priority Guidelines Met:**
            - MUST (SHALL): Core security, regulatory compliance, safety-critical operations
            - SHOULD: Important operational features, performance requirements  
            - COULD: Enhancement features, convenience functions
            
            **Healthy Distribution:** 30-40% MUST, 40-50% SHOULD, 10-20% COULD
            """)
            
            # Color-coded priority health indicator
            if must_percentage > 50:
                st.warning("⚠️ High proportion of MUST requirements - consider if all are truly critical")
            elif must_percentage < 20:
                st.warning("⚠️ Low proportion of MUST requirements - ensure critical requirements are identified")
            else:
                st.success("✅ Balanced priority distribution aligned with ARCADIA methodology")
    
    # Requirements by phase
    for phase, phase_reqs in results.get('requirements', {}).items():
        phase_info = arcadia_config.ARCADIA_PHASES.get(phase, {})
        
        st.markdown(f"""
        <div class="phase-section">
            <h3>{phase_info.get('name', phase.title())} Phase</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Phase description
        st.write(phase_info.get('description', ''))
        
        # Requirements tabs for this phase
        if phase_reqs:
            phase_tabs = st.tabs([req_type.title() for req_type in phase_reqs.keys()])
            
            for i, (req_type, reqs) in enumerate(phase_reqs.items()):
                with phase_tabs[i]:
                    display_requirements_list(reqs, req_type)
    
    # Export section
    st.markdown("### Export Requirements")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Export Requirements"):
            # Check if we have enhanced results and the format is ARCADIA-specific
            enhanced_results = st.session_state.get('enhanced_results')
            
            if export_format in ["ARCADIA_JSON", "Structured_Markdown"] and enhanced_results and hasattr(rag_system, 'export_structured_requirements'):
                exported_content = rag_system.export_structured_requirements(enhanced_results, export_format)
            else:
                # Use traditional export for regular results
                export_results = enhanced_results.get('traditional_requirements', results) if enhanced_results else results
                exported_content = rag_system.export_requirements(export_results, export_format)
            
            if export_format == "JSON":
                st.download_button(
                    "Download JSON",
                    exported_content,
                    "requirements.json",
                    "application/json"
                )
            elif export_format == "ARCADIA_JSON":
                st.download_button(
                    "Download ARCADIA JSON",
                    exported_content,
                    "arcadia_analysis.json",
                    "application/json"
                )
            elif export_format == "Structured_Markdown":
                st.download_button(
                    "Download Structured Report",
                    exported_content,
                    "arcadia_structured_report.md",
                    "text/markdown"
                )
            elif export_format == "Markdown":
                st.download_button(
                    "Download Markdown",
                    exported_content,
                    "requirements.md",
                    "text/markdown"
                )
            elif export_format == "Excel":
                st.download_button(
                    "Download Excel (CSV)",
                    exported_content,
                    "requirements.csv",
                    "text/csv"
                )
            elif export_format == "DOORS":
                st.download_button(
                    "Download DOORS",
                    exported_content,
                    "requirements.dxl",
                    "text/plain"
                )
            elif export_format == "ReqIF":
                st.download_button(
                    "Download ReqIF",
                    exported_content,
                    "requirements.reqif",
                    "application/xml"
                )
    
    with col2:
        st.info(f"Export format: {export_format}")

def display_requirements_list(requirements, req_type):
    if not requirements:
        st.info(f"No {req_type} requirements generated")
        return
    
    for req in requirements:
        # Determine priority class
        priority = req.get('priority', 'N/A').lower()
        if priority == 'must':
            priority_class = 'priority-high'
        elif priority == 'should':
            priority_class = 'priority-medium'
        else:
            priority_class = 'priority-low'
        
        # Get priority confidence and rationale
        priority_confidence = req.get('priority_confidence', 0.0)
        priority_rationale = req.get('rationale', 'No rationale provided')
        
        # Create expandable details for priority analysis
        priority_analysis = req.get('priority_analysis', {})
        analysis_summary = ""
        if priority_analysis:
            indicators = priority_analysis.get('indicators_found', [])
            if indicators:
                categories = set(ind['category'] for ind in indicators)
                analysis_summary = f"Based on: {', '.join(categories)}"
        
        st.markdown(f"""
        <div class="requirement-item">
            <div class="requirement-header">{req.get('id', 'N/A')}: {req.get('title', 'Untitled')}</div>
            <div class="requirement-description">{req.get('description', 'No description')}</div>
            <div class="requirement-meta">
                <span><strong>Priority:</strong> <span class="{priority_class}">{req.get('priority', 'N/A')}</span> 
                      (Confidence: {priority_confidence:.1f})</span>
                <span><strong>Verification:</strong> {req.get('verification_method', 'N/A')}</span>
            </div>
            <div class="requirement-analysis" style="font-size: 0.9em; color: #666; margin-top: 8px;">
                <strong>Priority Analysis:</strong> {analysis_summary}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add expandable details for priority rationale
        with st.expander(f"Priority Rationale for {req.get('id', 'N/A')}", expanded=False):
            st.write(priority_rationale)
            
            if priority_analysis:
                st.subheader("Detailed Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Stakeholder Alignment", f"{priority_analysis.get('stakeholder_alignment', 0):.2f}")
                    st.metric("Regulatory Compliance", f"{priority_analysis.get('regulatory_compliance', 0):.2f}")
                    st.metric("Safety Criticality", f"{priority_analysis.get('safety_criticality', 0):.2f}")
                
                with col2:
                    st.metric("Component Specificity", f"{priority_analysis.get('component_specificity', 0):.2f}")
                    st.metric("Phase Relevance", f"{priority_analysis.get('phase_relevance', 0):.2f}")
                
                # Show indicators found
                indicators_found = priority_analysis.get('indicators_found', [])
                if indicators_found:
                    st.subheader("Criticality Indicators Found")
                    for indicator in indicators_found:
                        st.write(f"• **{indicator['keyword']}** ({indicator['category']}) - Weight: {indicator['weight']:.2f}")
        



def evaluation_tab(rag_system, eval_service):
    st.markdown("### System Evaluation")
    
    if 'generation_results' in st.session_state:
        results = st.session_state['generation_results']
        
        # Evaluation metrics
        st.markdown("#### Evaluation Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Evaluate against CYDERCO"):
                with st.spinner("Evaluating..."):
                    evaluation = rag_system.evaluate_against_cyderco(results)
                    st.session_state['evaluation_results'] = evaluation
        
        with col2:
            if st.button("Quality Assessment"):
                with st.spinner("Assessing quality..."):
                    quality_assessment = eval_service.assess_requirement_quality(results)
                    st.session_state['quality_assessment'] = quality_assessment
        
        # Display evaluation results
        if 'evaluation_results' in st.session_state:
            evaluation = st.session_state['evaluation_results']
            
            st.markdown("#### CYDERCO Compatibility")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Coverage Score", f"{evaluation['coverage_score']:.1f}%")
            with col2:
                st.metric("Missing Requirements", len(evaluation['missing_requirements']))
            with col3:
                st.metric("Additional Requirements", len(evaluation['additional_requirements']))
            
            # Quality metrics
            if 'quality_assessment' in st.session_state:
                quality = st.session_state['quality_assessment']
                
                st.markdown("#### Quality Metrics")
                
                metrics_df = pd.DataFrame([
                    {"Metric": "Completeness", "Score": quality['completeness']},
                    {"Metric": "Consistency", "Score": quality['consistency']},
                    {"Metric": "Traceability", "Score": quality['traceability']},
                    {"Metric": "Testability", "Score": quality['testability']},
                    {"Metric": "Clarity", "Score": quality['clarity']}
                ])
                
                # Display metrics as a chart
                fig = px.bar(
                    metrics_df,
                    x="Metric",
                    y="Score",
                    title="Requirements Quality Assessment",
                    color="Score",
                    color_continuous_scale="RdYlGn"
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig)
                
                # Display detailed metrics
                for _, row in metrics_df.iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{row['Metric']}**")
                    with col2:
                        score_color = "green" if row['Score'] > 0.8 else "orange" if row['Score'] > 0.6 else "red"
                        st.markdown(f"<span style='color: {score_color}'>{row['Score']:.1%}</span>", unsafe_allow_html=True)
    
    else:
        st.info("Generate requirements first to see evaluation results")



def chat_tab(rag_system):
    """Enhanced chat interface with document interaction"""
    st.markdown("### Chat with Documents")
    
    # Create layout
    col1, col2, col3 = st.columns([2, 6, 2])
    
    with col1:
        st.markdown("#### Chat Management")
        
        # New chat button
        if st.button("New Chat", type="primary", use_container_width=True):
            new_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            st.session_state.current_chat_id = new_chat_id
            st.session_state.chats[new_chat_id] = {
                "title": "New Chat",
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "document_count": 0
            }
            save_chats(st.session_state.chats)
            st.rerun()
        
        # Chat history
        st.markdown("#### Chat History")
        if st.session_state.chats:
            with st.container():
                for chat_id, chat_data in sorted(st.session_state.chats.items(), 
                                               key=lambda x: x[1].get('created_at', ''), reverse=True):
                    title = chat_data.get('title', 'Untitled Chat')
                    msg_count = len(chat_data.get('messages', []))
                    
                    # Create a more informative button label
                    button_label = f"{title[:25]}{'...' if len(title) > 25 else ''}"
                    if msg_count > 0:
                        button_label += f" ({msg_count} msgs)"
                    
                    if st.button(button_label, key=f"chat_{chat_id}", use_container_width=True):
                        st.session_state.current_chat_id = chat_id
                        st.rerun()
                        
                    # Delete chat option
                    if st.button("Delete", key=f"delete_{chat_id}", help="Delete this chat"):
                        del st.session_state.chats[chat_id]
                        if st.session_state.current_chat_id == chat_id:
                            st.session_state.current_chat_id = None
                        save_chats(st.session_state.chats)
                        st.rerun()
        else:
            st.info("No previous chats. Create a new chat to get started!")
        
        # Clear all chats
        if st.session_state.chats and st.button("Clear All Chats", type="secondary"):
            if st.checkbox("Confirm deletion of all chats"):
                st.session_state.chats = {}
                st.session_state.current_chat_id = None
                save_chats(st.session_state.chats)
                st.success("All chats cleared!")
                st.rerun()
    
    with col2:
        st.markdown("#### Document Management")
        
        # Document Upload Section
        with st.expander("Upload Documents", expanded=False):
            st.markdown("""
            **Supported formats:** PDF, DOCX, TXT, MD, XML, JSON, AIRD, Capella  
            **Purpose:** Add documents to the knowledge base for chat interaction
            """)
            
            uploaded_files = st.file_uploader(
                "Add documents to the knowledge base",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'txt', 'md', 'xml', 'json', 'aird', 'capella'],
                help="Upload multiple documents to enhance the chat knowledge base"
            )
            
            if uploaded_files:
                st.info(f"{len(uploaded_files)} file(s) selected")
                
                if st.button("Process Documents", type="primary"):
                    with st.spinner("Processing documents..."):
                        logger.info(f"Processing {len(uploaded_files)} documents for chat...")
                        
                        temp_paths = []
                        processed_files = []
                        
                        try:
                            # Save uploaded files temporarily
                            for uploaded_file in uploaded_files:
                                temp_path = Path(f"temp_{uploaded_file.name}")
                                with open(temp_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                temp_paths.append(str(temp_path))
                                processed_files.append(uploaded_file.name)
                                logger.info(f"   Saved: {uploaded_file.name} ({uploaded_file.size} bytes)")
                            
                            # Process documents through RAG system
                            results = rag_system.add_documents_to_vectorstore(temp_paths)
                            
                            # Clean up temporary files
                            for temp_path in temp_paths:
                                try:
                                    os.remove(temp_path)
                                except:
                                    pass
                            
                            # Display results
                            st.success(f"Processed {results.get('processed', 0)} files successfully!")
                            st.info(f"Added {results.get('chunks_added', 0)} text chunks to knowledge base")
                            
                            # Show errors outside the expander to avoid nesting
                            if results.get('errors'):
                                st.error("Processing Errors:")
                                for error in results['errors']:
                                    st.error(f"{error}")
                            
                            # Update current chat document count
                            if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chats:
                                current_chat = st.session_state.chats[st.session_state.current_chat_id]
                                current_chat['document_count'] = current_chat.get('document_count', 0) + results.get('processed', 0)
                                save_chats(st.session_state.chats)
                            
                            logger.info(f"Document processing completed for chat interface")
                            
                        except Exception as e:
                            logger.error(f"Error processing documents for chat: {str(e)}")
                            st.error(f"Error processing documents: {str(e)}")
                            
                            # Clean up on error
                            for temp_path in temp_paths:
                                try:
                                    os.remove(temp_path)
                                except:
                                    pass
        
        # Chat Interface
        st.markdown("#### Conversation")
        
        if st.session_state.current_chat_id:
            current_chat = st.session_state.chats[st.session_state.current_chat_id]
            
            # Display chat title
            chat_title = st.text_input(
                "Chat Title", 
                value=current_chat.get('title', 'New Chat'),
                key="chat_title_input"
            )
            
            # Update title if changed
            if chat_title != current_chat.get('title', 'New Chat'):
                current_chat['title'] = chat_title
                save_chats(st.session_state.chats)
            
            # Chat messages container
            chat_container = st.container()
            
            with chat_container:
                # Display existing messages
                for i, message in enumerate(current_chat["messages"]):
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div class="chat-message user-message">
                            <strong>You:</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:  # assistant
                        st.markdown(f"""
                        <div class="chat-message assistant-message">
                            <strong>Assistant:</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show context sources if available
                        if "context" in message and message["context"]:
                            with st.container():
                                st.markdown(f"**Sources ({len(message['context'])} documents):**")
                                for j, doc in enumerate(message["context"]):
                                    st.markdown(f"""
                                    <div class="source-citation">
                                        <strong>Source {j+1}:</strong> {doc.get('metadata', {}).get('source', 'Unknown')}<br>
                                        <strong>Content Preview:</strong> {doc.get('content', '')[:300]}...
                                    </div>
                                    """, unsafe_allow_html=True)
            
            # Chat input
            user_prompt = st.chat_input("Ask about your documents, ARCADIA methodology, or MBSE concepts...")
            
            if user_prompt:
                logger.info(f"New chat message in session {st.session_state.current_chat_id}: {user_prompt[:100]}...")
                
                # Update chat title if it's the first message
                if not current_chat["messages"]:
                    current_chat["title"] = user_prompt[:50] + ("..." if len(user_prompt) > 50 else "")
                
                # Add user message
                current_chat["messages"].append({
                    "role": "user", 
                    "content": user_prompt,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Generate response
                with st.spinner("Analyzing documents and generating response..."):
                    try:
                        # Get MBSE context from settings
                        mbse_context = st.session_state.get('mbse_context', 'None')
                        enhanced_prompt = get_enhanced_prompt(user_prompt, mbse_context)
                        
                        # Use RAG system to generate response
                        response_data = rag_system.query_documents(enhanced_prompt)
                        
                        if isinstance(response_data, dict):
                            response = response_data.get('answer', 'I apologize, but I could not generate a response.')
                            context_docs = response_data.get('sources', [])
                        else:
                            response = str(response_data)
                            context_docs = []
                        
                        logger.info(f"Generated response with {len(context_docs)} context sources")
                        
                        # Add assistant response
                        current_chat["messages"].append({
                            "role": "assistant",
                            "content": response,
                            "context": [{"content": doc.page_content, "metadata": doc.metadata} for doc in context_docs] if context_docs else [],
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Save chats
                        save_chats(st.session_state.chats)
                        
                        # Rerun to show new messages
                        st.rerun()
                        
                    except Exception as e:
                        logger.error(f"Error generating chat response: {str(e)}")
                        error_message = f"I apologize, but I encountered an error: {str(e)}"
                        
                        current_chat["messages"].append({
                            "role": "assistant",
                            "content": error_message,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        save_chats(st.session_state.chats)
                        st.rerun()
        
        else:
            st.info("Create a new chat or select an existing one to start chatting with your documents!")
            
            # Quick start suggestions
            st.markdown("""
            **Quick Start Tips:**
            1. Click **"New Chat"** to create a conversation
            2. Upload documents to build your knowledge base
            3. Ask questions about your documents, ARCADIA methodology, or MBSE concepts
            4. Use the settings panel to configure MBSE context for specialized responses
            """)
    
    with col3:
        st.markdown("#### Chat Settings")
        
        # Model selection
        available_models = ["llama3:instruct", "gemma3:27b", "gemma3:12b", "gemma3:4b", "mistral:latest", "deepseek-r1:7b"]
        selected_model = st.selectbox(
            "Chat Model",
            available_models,
            index=0,
            key="chat_model",
            help="Select the language model for chat responses"
        )
        
        # Context settings
        context_length = st.slider(
            "Context Documents",
            min_value=1,
            max_value=10,
            value=5,
            key="context_length",
            help="Number of document chunks to use as context"
        )
        
        # MBSE context selection
        mbse_context = st.selectbox(
            "MBSE Context",
            ["None"] + list(MBSE_CONTEXT_PROMPTS.keys()),
            key="mbse_context",
            help="Apply specialized MBSE perspective to responses"
        )
        
        if mbse_context != "None":
            st.info(f"**Context Applied:** {MBSE_CONTEXT_PROMPTS[mbse_context]}")
        
        # Chat statistics
        if st.session_state.chats:
            st.markdown("#### Chat Statistics")
            
            total_chats = len(st.session_state.chats)
            total_messages = sum(len(chat.get('messages', [])) for chat in st.session_state.chats.values())
            
            st.metric("Total Chats", total_chats)
            st.metric("Total Messages", total_messages)
            
            if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chats:
                current_chat = st.session_state.chats[st.session_state.current_chat_id]
                current_messages = len(current_chat.get('messages', []))
                st.metric("Current Chat Messages", current_messages)

def structured_arcadia_tab(rag_system):
    """Enhanced tab for structured ARCADIA analysis with visualizations"""
    st.markdown("### 🏗️ Structured ARCADIA Analysis")
    
    # Check if we have enhanced results
    enhanced_results = st.session_state.get('enhanced_results')
    
    if not enhanced_results:
        st.info("""
        **No structured analysis available yet.**
        
        To generate structured ARCADIA analysis:
        1. Go to the **Generate Requirements** tab
        2. Enable **"Structured ARCADIA Analysis"** in the sidebar
        3. Upload a document or paste text and generate requirements
        4. Return here to view detailed structured insights
        """)
        
        # Add example of what will be available
        st.markdown("#### What you'll see here:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🎭 Operational Analysis**
            - Stakeholder identification
            - Operational capabilities
            - Mission scenarios
            - Activity processes
            
            **🏗️ System Analysis**  
            - System boundary definition
            - System functions & interfaces
            - Capability realization
            - Functional chains
            """)
        with col2:
            st.markdown("""
            **🧩 Logical Architecture**
            - Logical components & hierarchies
            - Logical functions & behaviors
            - Logical interfaces & data flows
            - Logical scenarios & interactions
            
            **🔧 Physical Architecture**
            - Physical components & platforms
            - Implementation constraints
            - Deployment configurations
            - Performance characteristics
            """)
        
        st.markdown("""
        **🔗 Cross-Phase Analysis**
        - Bidirectional traceability between all phases
        - Gap identification across architecture levels
        - Architecture consistency validation
        - Quality metrics and recommendations
        """)
        return
    
    # Get structured analysis summary
    if hasattr(rag_system, 'get_structured_analysis_summary'):
        try:
            analysis_summary = rag_system.get_structured_analysis_summary(enhanced_results)
        except Exception as e:
            st.error(f"Error getting analysis summary: {str(e)}")
            analysis_summary = {}
    else:
        analysis_summary = {}
    
    # Main content tabs for structured analysis (All ARCADIA phases)
    struct_tab1, struct_tab2, struct_tab3, struct_tab4, struct_tab5, struct_tab6 = st.tabs([
        "📊 Analysis Overview",
        "🎭 Operational Analysis", 
        "🏗️ System Analysis",
        "🧩 Logical Architecture",
        "🔧 Physical Architecture",
        "🔗 Cross-Phase Insights"
    ])
    
    with struct_tab1:
        display_analysis_overview(enhanced_results, analysis_summary)
    
    with struct_tab2:
        display_operational_analysis(enhanced_results)
    
    with struct_tab3:
        display_system_analysis(enhanced_results)
    
    with struct_tab4:
        display_logical_analysis(enhanced_results)
    
    with struct_tab5:
        display_physical_analysis(enhanced_results)
    
    with struct_tab6:
        display_cross_phase_analysis(enhanced_results, analysis_summary)

def display_analysis_overview(enhanced_results, analysis_summary):
    """Display high-level overview of the structured analysis"""
    st.markdown("#### Analysis Overview")
    
    # Enhancement summary
    enhancement_summary = enhanced_results.get('enhancement_summary', {})
    
    # Key metrics - All ARCADIA phases
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            "Phases Analyzed", 
            len(enhancement_summary.get('phases_analyzed', [])),
            help="Number of ARCADIA phases successfully analyzed"
        )
    
    with col2:
        st.metric(
            "Total Actors", 
            enhancement_summary.get('total_actors_identified', 0),
            help="Actors identified in operational and system phases"
        )
    
    with col3:
        st.metric(
            "Total Capabilities", 
            enhancement_summary.get('total_capabilities_identified', 0),
            help="Capabilities identified in operational and system phases"
        )
    
    with col4:
        st.metric(
            "Total Components", 
            enhancement_summary.get('total_components_identified', 0),
            help="Components identified in logical and physical phases"
        )
    
    with col5:
        st.metric(
            "Total Functions", 
            enhancement_summary.get('total_functions_identified', 0),
            help="Functions identified across system, logical, and physical phases"
        )
    
    with col6:
        st.metric(
            "Cross-Phase Links", 
            enhancement_summary.get('cross_phase_links', 0),
            help="Traceability links between phases"
        )
    
    # Phase coverage visualization
    if 'extraction_statistics' in analysis_summary:
        st.markdown("#### Phase Coverage Analysis")
        
        extraction_stats = analysis_summary['extraction_statistics']
        
        # Create coverage data for visualization (all ARCADIA phases)
        coverage_data = []
        for phase, stats in extraction_stats.items():
            total_elements = sum(stats.values())
            phase_data = {
                'Phase': phase.title(),
                'Elements': total_elements,
                'Actors': stats.get('actors', 0),
                'Capabilities': stats.get('capabilities', 0),
                'Functions': stats.get('functions', 0),
                'Scenarios': stats.get('scenarios', 0)
            }
            
            # Add phase-specific metrics
            if phase == 'logical':
                phase_data.update({
                    'Components': stats.get('components', 0),
                    'Interfaces': stats.get('interfaces', 0)
                })
            elif phase == 'physical':
                phase_data.update({
                    'Components': stats.get('components', 0),
                    'Constraints': stats.get('implementation_constraints', 0)
                })
            
            coverage_data.append(phase_data)
        
        if coverage_data:
            coverage_df = pd.DataFrame(coverage_data)
            
            # Create stacked bar chart
            fig = px.bar(
                coverage_df, 
                x='Phase', 
                y=['Actors', 'Capabilities', 'Functions', 'Scenarios'],
                title="Elements Extracted by Phase",
                color_discrete_sequence=['#667eea', '#2c5aa0', '#5a67d8', '#4c51bf']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Quality scores
    if 'quality_scores' in analysis_summary:
        st.markdown("#### Quality Assessment")
        
        quality_scores = analysis_summary['quality_scores']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quality metrics as gauge charts
            for metric_name, score_info in quality_scores.items():
                percentage = score_info['percentage']
                
                # Color based on score
                if percentage >= 80:
                    color = "green"
                elif percentage >= 60:
                    color = "orange"
                else:
                    color = "red"
                
                st.metric(
                    metric_name, 
                    f"{percentage:.1f}%",
                    help=f"Score: {score_info['score']:.2f}/{score_info['max_score']}"
                )
        
        with col2:
            # Quality score visualization
            quality_data = []
            for metric_name, score_info in quality_scores.items():
                quality_data.append({
                    'Metric': metric_name,
                    'Score': score_info['percentage']
                })
            
            if quality_data:
                quality_df = pd.DataFrame(quality_data)
                fig = px.bar(
                    quality_df,
                    x='Score',
                    y='Metric',
                    orientation='h',
                    title="Quality Metrics",
                    color='Score',
                    color_continuous_scale='RdYlGn',
                    range_color=[0, 100]
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    if 'recommendations' in analysis_summary:
        st.markdown("#### Recommendations")
        recommendations = analysis_summary['recommendations']
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.info(f"**{i}.** {rec}")
        else:
            st.success("✅ Analysis completed successfully with good quality scores!")

def display_operational_analysis(enhanced_results):
    """Display detailed operational analysis results"""
    st.markdown("#### 🎭 Operational Analysis Details")
    
    structured_analysis = enhanced_results.get('structured_analysis')
    if not structured_analysis or not structured_analysis.operational_analysis:
        st.warning("No operational analysis data available")
        return
    
    op_analysis = structured_analysis.operational_analysis
    
    # Operational Actors Section
    with st.expander("👥 Operational Actors", expanded=True):
        if op_analysis.actors:
            for i, actor in enumerate(op_analysis.actors):
                with st.container():
                    st.markdown(f"""
                    <div class="requirement-item">
                        <div class="requirement-header">{actor.name} ({actor.id})</div>
                        <div class="requirement-description">
                            <strong>Role:</strong> {actor.role_definition}<br>
                            <strong>Description:</strong> {actor.description}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if actor.responsibilities:
                        st.markdown("**Responsibilities:**")
                        for resp in actor.responsibilities:
                            st.markdown(f"• {resp}")
                    
                    if actor.capabilities:
                        st.markdown("**Capabilities:**")
                        for cap in actor.capabilities:
                            st.markdown(f"• {cap}")
                    
                    if i < len(op_analysis.actors) - 1:
                        st.markdown("---")
        else:
            st.info("No operational actors identified")
    
    # Operational Capabilities Section
    with st.expander("🎯 Operational Capabilities", expanded=True):
        if op_analysis.capabilities:
            for i, capability in enumerate(op_analysis.capabilities):
                with st.container():
                    st.markdown(f"""
                    <div class="requirement-item">
                        <div class="requirement-header">{capability.name} ({capability.id})</div>
                        <div class="requirement-description">
                            <strong>Mission:</strong> {capability.mission_statement}<br>
                            <strong>Description:</strong> {capability.description}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if capability.involved_actors:
                        st.markdown(f"**Involved Actors:** {', '.join(capability.involved_actors)}")
                    
                    if capability.performance_constraints:
                        st.markdown("**Performance Constraints:**")
                        for constraint in capability.performance_constraints:
                            st.markdown(f"• {constraint}")
                    
                    if i < len(op_analysis.capabilities) - 1:
                        st.markdown("---")
        else:
            st.info("No operational capabilities identified")
    
    # Operational Scenarios Section
    with st.expander("📋 Operational Scenarios", expanded=False):
        if op_analysis.scenarios:
            for scenario in op_analysis.scenarios:
                st.markdown(f"**{scenario.name} ({scenario.id})**")
                st.write(f"Type: {scenario.scenario_type}")
                st.write(f"Description: {scenario.description}")
                st.markdown("---")
        else:
            st.info("No operational scenarios identified")

def display_system_analysis(enhanced_results):
    """Display detailed system analysis results"""
    st.markdown("#### 🏗️ System Analysis Details")
    
    structured_analysis = enhanced_results.get('structured_analysis')
    if not structured_analysis or not structured_analysis.system_analysis:
        st.warning("No system analysis data available")
        return
    
    sys_analysis = structured_analysis.system_analysis
    
    # System Boundary Section
    with st.expander("🔲 System Boundary", expanded=True):
        boundary = sys_analysis.system_boundary
        st.markdown(f"""
        <div class="info-card">
            <h4>Scope Definition</h4>
            <p>{boundary.scope_definition}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if boundary.included_elements:
                st.markdown("**Included Elements:**")
                for element in boundary.included_elements:
                    st.markdown(f"✅ {element}")
        
        with col2:
            if boundary.excluded_elements:
                st.markdown("**Excluded Elements:**")
                for element in boundary.excluded_elements:
                    st.markdown(f"❌ {element}")
    
    # System Functions Section
    with st.expander("⚙️ System Functions", expanded=True):
        if sys_analysis.functions:
            for i, function in enumerate(sys_analysis.functions):
                with st.container():
                    st.markdown(f"""
                    <div class="requirement-item">
                        <div class="requirement-header">{function.name} ({function.id})</div>
                        <div class="requirement-description">
                            <strong>Type:</strong> {function.function_type}<br>
                            <strong>Description:</strong> {function.description}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if function.allocated_actors:
                        st.markdown(f"**Allocated Actors:** {', '.join(function.allocated_actors)}")
                    
                    if function.performance_requirements:
                        st.markdown("**Performance Requirements:**")
                        for req in function.performance_requirements:
                            st.markdown(f"• {req}")
                    
                    if i < len(sys_analysis.functions) - 1:
                        st.markdown("---")
        else:
            st.info("No system functions identified")
    
    # System Capabilities Section
    with st.expander("🎯 System Capabilities", expanded=False):
        if sys_analysis.capabilities:
            for capability in sys_analysis.capabilities:
                st.markdown(f"**{capability.name} ({capability.id})**")
                st.write(f"Description: {capability.description}")
                if capability.implementing_functions:
                    st.write(f"Implementing Functions: {', '.join(capability.implementing_functions)}")
                st.markdown("---")
        else:
            st.info("No system capabilities identified")

def display_logical_analysis(enhanced_results):
    """Display detailed logical architecture results"""
    st.markdown("#### 🧩 Logical Architecture Details")
    
    structured_analysis = enhanced_results.get('structured_analysis')
    if not structured_analysis or not structured_analysis.logical_architecture:
        st.warning("No logical architecture data available. Please ensure logical architecture extraction is enabled.")
        return
    
    logical_arch = structured_analysis.logical_architecture
    
    # Logical Components Section
    with st.expander("🧩 Logical Components", expanded=True):
        if logical_arch.components:
            for i, component in enumerate(logical_arch.components):
                with st.container():
                    st.markdown(f"""
                    <div class="requirement-item">
                        <div class="requirement-header">{component.name} ({component.id})</div>
                        <div class="requirement-description">
                            <strong>Type:</strong> {component.component_type}<br>
                            <strong>Description:</strong> {component.description}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if component.responsibilities:
                        st.markdown("**Responsibilities:**")
                        for resp in component.responsibilities:
                            st.markdown(f"• {resp}")
                    
                    if component.sub_components:
                        st.markdown(f"**Sub-components:** {', '.join(component.sub_components)}")
                    
                    if i < len(logical_arch.components) - 1:
                        st.markdown("---")
        else:
            st.info("No logical components identified")
    
    # Logical Functions Section
    with st.expander("⚙️ Logical Functions", expanded=True):
        if logical_arch.functions:
            for i, function in enumerate(logical_arch.functions):
                with st.container():
                    st.markdown(f"""
                    <div class="requirement-item">
                        <div class="requirement-header">{function.name} ({function.id})</div>
                        <div class="requirement-description">
                            <strong>Behavior:</strong> {function.behavioral_specification}<br>
                            <strong>Description:</strong> {function.description}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if function.allocated_components:
                        st.markdown(f"**Allocated Components:** {', '.join(function.allocated_components)}")
                    
                    if function.input_flows:
                        st.markdown("**Input Flows:**")
                        for flow in function.input_flows:
                            st.markdown(f"• {flow}")
                    
                    if function.output_flows:
                        st.markdown("**Output Flows:**")
                        for flow in function.output_flows:
                            st.markdown(f"• {flow}")
                    
                    if i < len(logical_arch.functions) - 1:
                        st.markdown("---")
        else:
            st.info("No logical functions identified")
    
    # Logical Interfaces Section
    with st.expander("🔌 Logical Interfaces", expanded=False):
        if logical_arch.interfaces:
            for interface in logical_arch.interfaces:
                st.markdown(f"**{interface.name} ({interface.id})**")
                st.write(f"Protocol: {interface.protocol}")
                st.write(f"Provider: {interface.provider} → Consumer: {interface.consumer}")
                if interface.data_elements:
                    st.write(f"Data Elements: {', '.join(interface.data_elements)}")
                st.markdown("---")
        else:
            st.info("No logical interfaces identified")
    
    # Logical Scenarios Section
    with st.expander("📋 Logical Scenarios", expanded=False):
        if logical_arch.scenarios:
            for scenario in logical_arch.scenarios:
                st.markdown(f"**{scenario.name} ({scenario.id})**")
                st.write(f"Context: {scenario.scenario_context}")
                st.write(f"Description: {scenario.description}")
                if scenario.component_interactions:
                    st.markdown("**Component Interactions:**")
                    for interaction in scenario.component_interactions:
                        st.markdown(f"• {interaction}")
                st.markdown("---")
        else:
            st.info("No logical scenarios identified")

def display_physical_analysis(enhanced_results):
    """Display detailed physical architecture results"""
    st.markdown("#### 🔧 Physical Architecture Details")
    
    structured_analysis = enhanced_results.get('structured_analysis')
    if not structured_analysis or not structured_analysis.physical_architecture:
        st.warning("No physical architecture data available. Please ensure physical architecture extraction is enabled.")
        return
    
    physical_arch = structured_analysis.physical_architecture
    
    # Physical Components Section
    with st.expander("🔧 Physical Components", expanded=True):
        if physical_arch.components:
            for i, component in enumerate(physical_arch.components):
                with st.container():
                    st.markdown(f"""
                    <div class="requirement-item">
                        <div class="requirement-header">{component.name} ({component.id})</div>
                        <div class="requirement-description">
                            <strong>Type:</strong> {component.component_type}<br>
                            <strong>Technology Platform:</strong> {component.technology_platform}<br>
                            <strong>Description:</strong> {component.description}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if component.resource_requirements:
                        st.markdown("**Resource Requirements:**")
                        for req in component.resource_requirements:
                            st.markdown(f"• {req}")
                    
                    if component.deployment_location:
                        st.markdown(f"**Deployment Location:** {component.deployment_location}")
                    
                    if i < len(physical_arch.components) - 1:
                        st.markdown("---")
        else:
            st.info("No physical components identified")
    
    # Implementation Constraints Section
    with st.expander("⚠️ Implementation Constraints", expanded=True):
        if physical_arch.constraints:
            # Group constraints by type
            constraint_types = {}
            for constraint in physical_arch.constraints:
                constraint_type = constraint.constraint_type
                if constraint_type not in constraint_types:
                    constraint_types[constraint_type] = []
                constraint_types[constraint_type].append(constraint)
            
            for constraint_type, constraints in constraint_types.items():
                st.markdown(f"**{constraint_type.title()} Constraints:**")
                for constraint in constraints:
                    st.markdown(f"• **{constraint.description}**")
                    if hasattr(constraint, 'rationale') and constraint.rationale:
                        st.markdown(f"  💡 *{constraint.rationale}*")
                st.markdown("---")
        else:
            st.info("No implementation constraints identified")
    
    # Physical Functions Section
    with st.expander("⚙️ Physical Functions", expanded=False):
        if physical_arch.functions:
            for function in physical_arch.functions:
                st.markdown(f"**{function.name} ({function.id})**")
                st.write(f"Description: {function.description}")
                if function.resource_requirements:
                    st.write(f"Resource Requirements: {', '.join(function.resource_requirements)}")
                if function.timing_constraints:
                    st.write(f"Timing Constraints: {', '.join(function.timing_constraints)}")
                st.markdown("---")
        else:
            st.info("No physical functions identified")
    
    # Physical Scenarios Section
    with st.expander("📋 Physical Scenarios", expanded=False):
        if physical_arch.scenarios:
            for scenario in physical_arch.scenarios:
                st.markdown(f"**{scenario.name} ({scenario.id})**")
                st.write(f"Type: {scenario.scenario_type}")
                st.write(f"Description: {scenario.description}")
                if scenario.involved_components:
                    st.write(f"Involved Components: {', '.join(scenario.involved_components)}")
                st.markdown("---")
        else:
            st.info("No physical scenarios identified")

def display_cross_phase_analysis(enhanced_results, analysis_summary):
    """Display cross-phase analysis insights"""
    st.markdown("#### 🔗 Cross-Phase Analysis Insights")
    
    structured_analysis = enhanced_results.get('structured_analysis')
    if not structured_analysis or not structured_analysis.cross_phase_analysis:
        st.warning("No cross-phase analysis data available")
        return
    
    cross_phase = structured_analysis.cross_phase_analysis
    
    # Traceability Links Section
    with st.expander("🔗 Traceability Links", expanded=True):
        if cross_phase.traceability_links:
            st.markdown(f"**Total Links:** {len(cross_phase.traceability_links)}")
            
            # Create traceability visualization
            trace_data = []
            for link in cross_phase.traceability_links:
                trace_data.append({
                    'Source': link.source_element,
                    'Target': link.target_element,
                    'Relationship': link.relationship_type,
                    'Confidence': link.confidence_score,
                    'Source Phase': link.source_phase.value,
                    'Target Phase': link.target_phase.value
                })
            
            if trace_data:
                trace_df = pd.DataFrame(trace_data)
                
                # Display as table
                st.dataframe(trace_df, use_container_width=True)
                
                # Create sankey diagram would be nice here, but simpler for now
                st.markdown("**Traceability Summary:**")
                for link in cross_phase.traceability_links[:5]:  # Show first 5
                    confidence_color = "🟢" if link.confidence_score > 0.7 else "🟡" if link.confidence_score > 0.5 else "🔴"
                    st.markdown(f"{confidence_color} {link.source_element} → {link.target_element} ({link.relationship_type})")
        else:
            st.info("No traceability links identified")
    
    # Gap Analysis Section
    with st.expander("🔍 Gap Analysis", expanded=True):
        if cross_phase.gap_analysis:
            st.markdown(f"**Gaps Identified:** {len(cross_phase.gap_analysis)}")
            
            # Group by severity
            gaps_by_severity = {}
            for gap in cross_phase.gap_analysis:
                severity = gap.severity
                if severity not in gaps_by_severity:
                    gaps_by_severity[severity] = []
                gaps_by_severity[severity].append(gap)
            
            # Display by severity
            severity_colors = {
                'critical': '🔴',
                'major': '🟠', 
                'medium': '🟡',
                'minor': '🟢'
            }
            
            for severity in ['critical', 'major', 'medium', 'minor']:
                if severity in gaps_by_severity:
                    st.markdown(f"**{severity_colors[severity]} {severity.title()} ({len(gaps_by_severity[severity])})**")
                    for gap in gaps_by_severity[severity]:
                        st.markdown(f"• **{gap.gap_type.upper()}**: {gap.description}")
                        if gap.recommendations:
                            for rec in gap.recommendations:
                                st.markdown(f"  💡 {rec}")
        else:
            st.success("✅ No gaps identified - analysis appears complete!")
    
    # Coverage Matrix
    if cross_phase.coverage_matrix:
        with st.expander("📊 Coverage Matrix", expanded=False):
            st.markdown("**Phase-to-Phase Coverage:**")
            
            coverage_data = []
            for source_target, coverage_info in cross_phase.coverage_matrix.items():
                for coverage_type, score in coverage_info.items():
                    coverage_data.append({
                        'Relationship': source_target.replace('_', ' → ').title(),
                        'Coverage Type': coverage_type.replace('_', ' ').title(),
                        'Coverage %': score * 100
                    })
            
            if coverage_data:
                coverage_df = pd.DataFrame(coverage_data)
                fig = px.bar(
                    coverage_df,
                    x='Relationship',
                    y='Coverage %',
                    color='Coverage Type',
                    title="Cross-Phase Coverage Analysis",
                    color_discrete_sequence=['#667eea', '#2c5aa0']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()