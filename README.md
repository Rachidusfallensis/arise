# 🏗️ SAFE MBSE RAG System

A **Retrieval-Augmented Generation (RAG) System** for generating methodologically compliant requirements using **ARCADIA methodology** semantic grounding. This system implements Phase 1 of a comprehensive framework for AI-driven requirements engineering in Model-Based Systems Engineering (MBSE).

## 🎯 Overview

The SAFE MBSE RAG System transforms stakeholder inputs and project documentation into structured, methodologically compliant requirements following the ARCADIA methodology. It bridges the gap between informal project descriptions and formal requirements specification.

### Key Features

- 🧠 **AI-Powered Requirements Generation**: Uses LLM with RAG for intelligent requirements extraction
- 🏗️ **ARCADIA Methodology Grounding**: Semantically grounded in proven systems engineering methodology
- 📊 **Multi-Phase Support**: Covers all 5 ARCADIA phases (OA, SA, LA, PA, EPBS)
- 🔍 **Quality Assessment**: Comprehensive evaluation of generated requirements
- 🎨 **Modern Web Interface**: Streamlit-based UI for easy interaction
- 📈 **Analytics Dashboard**: Real-time monitoring and performance metrics
- 🔄 **Digital Twin Integration**: Capella model integration for validation

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Input Sources                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ Technical Docs  │ Project Docs    │ Stakeholder Inputs          │
│ (standards,     │ (briefs, user   │ (requirements gathering,    │
│  regulations)   │  stories, specs)│  interviews)                │
└─────────────────┴─────────────────┴─────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RAG Knowledge Retrieval                      │
│  ┌──────────────┐     ┌─────────────┐     ┌─────────────────┐  │
│  │   Analyze    │────▶│    Plan     │────▶│   Engineers     │  │
│  │  Document    │     │Requirements │     │   Validation    │  │
│  │  Analysis    │     │ Generation  │     │                 │  │
│  └──────────────┘     └─────────────┘     └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                Requirements Specifications                      │
│  • Functional Requirements                                      │
│  • Non-functional Requirements                                 │
│  • Traceability Matrix                                         │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
safe-mbse-rag/
├── src/                          # Core system components
│   ├── core/                     # Main RAG system
│   │   ├── rag_system.py        # Primary RAG implementation
│   │   ├── document_processor.py # Document analysis
│   │   └── requirements_generator.py # Requirements generation
│   ├── services/                 # Business logic services
│   │   ├── evaluation_service.py # Quality assessment
│   │   ├── requirements_service.py # Requirements management
│   │   └── validation_service.py # Validation logic
│   └── utils/                    # Utility functions
├── ui/                          # Streamlit web interface
│   └── app.py                   # Main UI application
├── config/                      # Configuration files
│   ├── config.py               # General configuration
│   ├── arcadia_config.py       # ARCADIA methodology config
│   └── requirements_templates.py # Templates
├── data/                        # Data and examples
│   ├── examples/               # Sample projects
│   ├── templates/              # Document templates
│   └── vectordb/               # Vector database storage
├── tests/                       # Test suite
├── docs/                        # Documentation
└── scripts/                     # Utility scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip package manager
- OpenAI API key (for LLM functionality)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd safe-mbse-rag
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python run_app.py
   ```

The application will launch at `http://localhost:8501`

## 💡 Usage

### 1. Generate Requirements

1. **Upload or paste** your project proposal/documentation
2. **Select target ARCADIA phase** (or all phases)
3. **Choose requirement types** (functional, non-functional, stakeholder)
4. **Configure generation parameters**
5. **Click "Generate Requirements"**

### 2. Review and Export

- Review generated requirements organized by ARCADIA phase
- Assess quality metrics and compliance scores
- Export to JSON, Markdown, or other formats
- Validate against CYDERCO standards

### 3. Quality Assessment

- View comprehensive quality metrics:
  - **Completeness**: Requirement field coverage
  - **Consistency**: Format and priority standardization
  - **Traceability**: ARCADIA phase mapping
  - **Testability**: Verification method presence
  - **Clarity**: Language precision and structure

### 4. Analytics Dashboard

- Monitor system performance and usage
- View requirements generation trends
- Analyze ARCADIA phase distribution
- Track quality improvements over time

## 🔧 Configuration

### ARCADIA Methodology

The system supports all 5 ARCADIA phases:

- **OA (Operational Analysis)**: Stakeholder needs and operational scenarios
- **SA (System Analysis)**: System-level requirements and functions
- **LA (Logical Architecture)**: Logical components and interfaces
- **PA (Physical Architecture)**: Physical implementation
- **EPBS (End Product Breakdown Structure)**: Product hierarchy

### Quality Thresholds

Default quality thresholds can be configured in `config/config.py`:

```python
QUALITY_THRESHOLDS = {
    "completeness": 0.8,
    "consistency": 0.85,
    "traceability": 0.75,
    "testability": 0.7,
    "clarity": 0.8
}
```

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest tests/

# Specific test modules
pytest tests/test_rag_system.py
pytest tests/test_evaluation_service.py

# With coverage
pytest --cov=src tests/
```

## 📊 Evaluation Metrics

The system provides comprehensive evaluation across multiple dimensions:

### Requirements Quality
- **Completeness**: Required fields presence
- **Consistency**: Format standardization
- **Traceability**: Phase/stakeholder mapping
- **Testability**: Verification methods
- **Clarity**: Language precision

### ARCADIA Compliance
- Phase coverage assessment
- Methodology adherence scoring
- Best practice recommendations

### Performance Metrics
- Generation speed and accuracy
- User satisfaction scores
- System reliability metrics

## 🔬 Research Context

This implementation represents **Phase 1** of a comprehensive framework for AI-assisted requirements engineering:

- **Phase 1**: Requirements generation from stakeholder inputs (Current)
- **Phase 2**: Interactive refinement and validation
- **Phase 3**: Integration with digital twins and continuous monitoring

The system contributes to advancing the state-of-the-art in:
- AI-assisted requirements engineering
- MBSE methodology automation
- Quality assessment in systems engineering

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- ARCADIA methodology by Thales
- Research contributions from the MBSE community
- Open-source libraries and frameworks used

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation in `docs/`

---

**Built with ❤️ for the MBSE community**
