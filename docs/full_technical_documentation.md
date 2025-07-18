## ARISE System Technical Documentation

### 1. Overview
ARISE (ARcadia Intelligent System Engine) is an AI-driven requirements generation system using ARCADIA methodology for Model-Based Systems Engineering (MBSE). It transforms project documents into structured requirements with RAG capabilities, persistence, and analysis tools.

**Key Features:**
- AI-powered requirements generation
- ARCADIA methodology integration (OA, SA, LA, PA)
- Intelligent document management with deduplication
- Project persistence and multi-project support
- Structured analysis with traceability and gap detection
- Quality assessment and evaluation metrics
- Modern Streamlit-based UI

### 2. Technologies Used
- **Frontend:** Streamlit (UI), Plotly (visualizations), Pandas (data handling)
- **Backend:** Python 3.10+, Ollama (LLM integration), ChromaDB (vector storage)
- **AI/ML:** Nomic Embeddings, Llama3/Gemma models for generation
- **Database:** SQLite (persistence), ChromaDB (vectors)
- **Other:** PyPDF2/Docx (document parsing), Logging (monitoring)

### 3. System Architecture
ARISE uses a layered architecture:

1. **Input Layer:** Document upload, text input, examples
2. **Processing Layer:** Unified Document Processor (with deduplication, chunking, embedding)
3. **Core Layer:** Unified RAG System (generation, analysis, validation)
4. **Persistence Layer:** SQLite DB for projects, documents, requirements
5. **Output Layer:** UI dashboards, exports (JSON, CSV, Markdown)

**High-Level Flow:**
- Upload/Select documents → Process & Embed → Generate Requirements/Analysis → Validate & Improve → Display/Export

### 4. Key Processes
#### Document Processing
- Hash-based deduplication
- Content extraction (PDF, DOCX, etc.)
- Chunking & Embedding (Nomic)
- Project linking & persistence

#### Requirements Generation
- Context enrichment (ARCADIA knowledge)
- Phase-specific generation (Operational, System, etc.)
- Types: Functional, Non-functional, Stakeholder
- Priority balancing & validation

#### Structured Analysis
- Phase extractors (Operational, System, Logical, Physical)
- Cross-phase: Traceability, gaps, coverage
- Quality metrics & recommendations

#### Project Management
- Create/Select projects
- Document management per project
- Session logging & history

### 5. Components
- **UnifiedRAGSystem:** Central orchestrator
- **StructuredARCADIAService:** ARCADIA analysis coordination
- **PersistenceService:** DB operations
- **EnhancedRequirementsGenerator:** Balanced generation
- **RequirementsValidationPipeline:** Multi-level validation

For detailed code, see src/core/. 