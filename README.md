# 🏗️ SAFE MBSE RAG System

**AI-Driven Requirements Generation using ARCADIA Methodology**

A comprehensive **Retrieval-Augmented Generation (RAG) System** that transforms project documents and stakeholder inputs into structured, methodologically compliant requirements using the **ARCADIA methodology**. This system provides intelligent document management, AI-powered requirements generation, and persistent project tracking for Model-Based Systems Engineering (MBSE).

## 🎯 Overview

The SAFE MBSE RAG System bridges the gap between informal project documentation and formal requirements specification. It combines advanced AI capabilities with proven systems engineering methodologies to accelerate and improve the requirements engineering process.

### ✨ Key Features

- 🧠 **AI-Powered Requirements Generation**: LLM-based intelligent requirements extraction and generation
- 🏗️ **ARCADIA Methodology Integration**: Semantically grounded in proven systems engineering methodology
- 📚 **Intelligent Document Management**: Upload, process, and analyze project documents
- 💬 **Document Chat Interface**: Interactive chat with your project documents
- 🗂️ **Project Persistence**: Complete project lifecycle management with data persistence
- 📊 **Multi-Phase ARCADIA Support**: Covers all ARCADIA phases (OA, SA, LA, PA, EPBS)
- 🔍 **Quality Assessment**: Comprehensive evaluation of generated requirements
- 📈 **Project Insights**: Real-time analytics and cross-phase traceability
- 🎨 **Modern Web Interface**: Clean, intuitive Streamlit-based UI
- 🔄 **Requirements Traceability**: Track requirements across ARCADIA phases

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           INPUT LAYER                               │
├─────────────────┬─────────────────┬─────────────────────────────────┤
│   Project Docs  │ Stakeholder     │     Examples &                  │
│   (PDF, DOCX,   │ Requirements    │     Templates                   │
│    TXT, MD)     │                 │                                 │
└─────────────────┴─────────────────┴─────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSING                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Document   │  │   Chunk     │  │  Embedding  │  │   Vector    │ │
│  │  Analysis   │→ │ Extraction  │→ │ Generation  │→ │   Storage   │ │
│  │             │  │             │  │             │  │             │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AI-POWERED ANALYSIS                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   RAG       │  │  ARCADIA    │  │ Requirements│  │   Quality   │ │
│  │ Retrieval   │→ │ Semantic    │→ │ Generation  │→ │ Assessment  │ │
│  │             │  │ Grounding   │  │             │  │             │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OUTPUT & MANAGEMENT                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Structured  │  │   Project   │  │    Export   │  │ Insights &  │ │
│  │Requirements │  │ Persistence │  │   Options   │  │ Analytics   │ │
│  │             │  │             │  │             │  │             │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (tested with Python 3.13)
- **pip** package manager
- **Ollama server** with required models (or compatible LLM API)
- **8GB+ RAM** recommended for optimal performance

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd safe-mbse-rag
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Ollama (if using local models)**
   ```bash
   # Install required models
   ollama pull llama3:instruct
   ollama pull nomic-embed-text:latest
   ollama pull gemma3:12b  # Optional for enhanced features
   ```

5. **Launch the application**
   ```bash
   python run_app.py
   ```

The application will perform system validation and launch at `http://localhost:8501`

## 💡 How to Use

### 1. 📚 Document Management

**Upload and Process Documents:**
1. Navigate to the **"Document Management"** tab
2. Create a new project or select an existing one
3. Upload your project documents (PDF, DOCX, TXT, MD)
4. Wait for processing and document analysis
5. Chat with your documents using the integrated chat interface

**Supported Document Types:**
- Technical specifications (PDF, DOCX)
- Project proposals (TXT, MD)
- Requirements documents
- Stakeholder documentation
- System design documents

### 2. 🏗️ Requirements & Analysis

**Generate Requirements from Documents:**
1. Navigate to the **"Requirements & Analysis"** tab
2. Select which uploaded documents to analyze
3. Configure ARCADIA settings:
   - Target phase (Operational, System, Logical, Physical, or All)
   - Requirement types (Functional, Non-functional, Stakeholder)
   - Analysis options (Structured ARCADIA analysis, Cross-phase analysis)
4. Click **"Generate Requirements & Analysis"**
5. Review generated requirements organized by ARCADIA phases

**Alternative Input Methods:**
- **Manual Text Input**: Paste project text directly
- **Example Projects**: Load built-in example projects
- **Quick Upload**: Upload documents directly in the analysis tab

### 3. 📊 Project Insights

**Monitor Your Projects:**
1. Navigate to the **"Project Insights"** tab
2. View project dashboard with key metrics
3. Analyze activity timeline and project health
4. Explore cross-phase traceability visualization
5. Export project data and reports

**Available Insights:**
- Project activity timeline
- Requirements distribution across ARCADIA phases
- Document processing statistics
- Quality metrics and health scores
- Stakeholder management

### 4. ⚙️ Configuration Options

**ARCADIA Phases:**
- **OA (Operational Analysis)**: Stakeholder needs and operational scenarios
- **SA (System Analysis)**: System-level requirements and functions  
- **LA (Logical Architecture)**: Logical components and interfaces
- **PA (Physical Architecture)**: Physical implementation requirements
- **EPBS**: End Product Breakdown Structure

**Requirement Types:**
- **Functional**: What the system must do
- **Non-functional**: How the system must perform
- **Stakeholder**: Who needs what from the system

## 📁 Project Structure

```
safe-mbse-rag/
├── 📱 UI Layer
│   ├── ui/app.py                    # Main Streamlit application
│   ├── ui/components/               # UI components
│   │   ├── project_manager.py     # Project management interface
│   │   ├── requirements_viewer.py # Requirements display
│   │   └── evaluation_dashboard.py # Analytics dashboard
│   └── ui/styles/                  # CSS styling
│
├── 🧠 Core System
│   ├── src/core/                   # Main system components
│   │   ├── rag_system.py          # Primary RAG implementation
│   │   ├── enhanced_persistent_rag_system.py # Enhanced system with persistence
│   │   ├── document_processor.py   # Document analysis
│   │   ├── requirements_generator.py # Requirements generation
│   │   └── structured_arcadia_service.py # ARCADIA methodology integration
│   │
│   ├── src/services/               # Business logic services
│   │   ├── persistence_service.py  # Database and project persistence
│   │   ├── evaluation_service.py   # Quality assessment
│   │   ├── requirements_service.py # Requirements management
│   │   └── validation_service.py   # Validation logic
│   │
│   └── src/utils/                  # Utility functions
│       ├── template_engine.py      # Template processing
│       └── enhanced_requirement_extractor.py # Advanced extraction
│
├── ⚙️ Configuration
│   ├── config/config.py            # General configuration
│   ├── config/arcadia_config.py    # ARCADIA methodology settings
│   └── config/requirements_templates.py # Template definitions
│
├── 📊 Data & Examples
│   ├── data/examples/              # Sample projects
│   ├── data/templates/             # Document templates
│   ├── data/vectordb/              # Vector database storage
│   └── data/safe_mbse.db          # Project persistence database
│
├── 🧪 Testing & Evaluation
│   ├── tests/                      # Test suite
│   ├── scripts/                    # Evaluation and testing scripts
│   └── docs/evaluation_framework.md # Comprehensive evaluation methodology
│
└── 🛠️ Utilities
    ├── demos/                      # Example usage demonstrations
    ├── run_app.py                  # Application launcher with validation
    ├── monitor_logs.py             # Log monitoring utility
    └── requirements.txt            # Python dependencies
```

## 🔧 Configuration

### Environment Setup

The system supports multiple LLM backends:

**Ollama (Recommended - Local)**
```python
# config/config.py
OLLAMA_BASE_URL = "http://localhost:11434"  # or your Ollama server
DEFAULT_MODEL = "llama3:instruct"
EMBEDDING_MODEL = "nomic-embed-text:latest"
```

**Custom LLM API**
```python
# Set environment variables
export LANGCHAIN_API_KEY="your-api-key"
export CUSTOM_LLM_ENDPOINT="your-endpoint"
```

### Quality Thresholds

Customize quality assessment thresholds:

```python
# config/config.py
QUALITY_THRESHOLDS = {
    "completeness": 0.8,
    "consistency": 0.85, 
    "traceability": 0.75,
    "testability": 0.7,
    "clarity": 0.8
}
```

### ARCADIA Configuration

Fine-tune ARCADIA methodology settings:

```python
# config/arcadia_config.py
ARCADIA_PHASES = {
    "operational": {
        "name": "Operational Analysis", 
        "focus": "stakeholder_needs",
        "outputs": ["operational_scenarios", "stakeholder_requirements"]
    },
    # ... other phases
}
```

## 📊 Features Deep Dive

### Intelligent Document Processing

- **Multi-format Support**: PDF, DOCX, TXT, MD, XML, JSON
- **Automatic Text Extraction**: Advanced OCR and parsing
- **Duplicate Detection**: Prevents reprocessing of identical documents
- **Chunking Strategy**: Intelligent text segmentation for optimal RAG performance
- **Metadata Extraction**: Automatic extraction of document metadata

### AI-Powered Requirements Generation

- **Context-Aware Generation**: Uses full document context for accurate requirements
- **ARCADIA Semantic Grounding**: Requirements aligned with methodology phases
- **Multi-Type Support**: Functional, non-functional, and stakeholder requirements
- **Quality Scoring**: Automatic assessment of requirement quality
- **Traceability**: Links requirements back to source documents

### Project Persistence & Management

- **SQLite Database**: Lightweight, file-based project storage
- **Complete Project Lifecycle**: Create, manage, and track projects over time
- **Session Logging**: Track all user activities and system events
- **Cross-Session Continuity**: Work persists across application restarts
- **Export Capabilities**: Multiple export formats for integration

### Advanced Analytics

- **Real-time Metrics**: Live project health and progress indicators
- **Cross-Phase Analysis**: Traceability across ARCADIA phases
- **Activity Timeline**: Visual project activity tracking
- **Quality Trends**: Monitor requirement quality over time
- **Statistical Insights**: Comprehensive project statistics

## 🧪 Testing & Evaluation

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_rag_system.py
pytest tests/test_persistence.py

# Run with coverage
pytest --cov=src tests/
```

### Performance Benchmarks

```bash
# Run system evaluation
python scripts/evaluate_system.py

# Performance analysis
python scripts/performance_analysis.py

# Test Ollama connectivity
python scripts/test_ollama_server.py
```

### Quality Assessment

The system provides multi-dimensional quality evaluation:

- **Requirements Quality**: Completeness, consistency, clarity, testability
- **ARCADIA Compliance**: Methodology adherence and phase alignment
- **System Performance**: Response time, accuracy, reliability
- **User Experience**: Usability metrics and satisfaction scores

## 🔍 Troubleshooting

### Common Issues

**Port 8501 already in use:**
```bash
# Kill existing Streamlit processes
pkill -f streamlit
# Or use a different port
streamlit run ui/app.py --server.port 8502
```

**Ollama connection issues:**
```bash
# Check Ollama status
ollama list
# Restart Ollama service
ollama serve
```

**Memory issues with large documents:**
- Reduce chunk size in configuration
- Process documents individually
- Use enhanced chunking strategies

### Logging & Debugging

```bash
# Monitor real-time logs
python monitor_logs.py

# Check application logs
tail -f logs/requirements_generation.log

# Enable debug mode
export STREAMLIT_LOG_LEVEL=debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run code formatting
black src/ ui/ tests/

# Run linting
flake8 src/ ui/

# Run type checking  
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **ARCADIA Methodology** by Thales
- **MBSE Community** for research and best practices
- **Open Source Libraries**: Streamlit, LangChain, ChromaDB, and others
- **Ollama Project** for local LLM capabilities

## 📞 Support & Documentation

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: Comprehensive guides in the `docs/` directory
- **Examples**: Working demonstrations in the `demos/` directory
- **Evaluation**: Complete evaluation framework in `docs/evaluation_framework.md`

---

**🏗️ Built for the MBSE Community - Accelerating Requirements Engineering with AI**

### Quick Links
- 🚀 [Get Started](#quick-start)
- 💡 [How to Use](#how-to-use)
- 🔧 [Configuration](#configuration)
- 🧪 [Testing](#testing--evaluation)
- 📊 [Project Structure](#project-structure)
