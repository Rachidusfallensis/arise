import os
from typing import Dict, List, Any

# Ollama Configuration
OLLAMA_BASE_URL = "http://llm-eva.univ-pau.fr:11434"
DEFAULT_MODEL = "gemma3:27b"
EMBEDDING_MODEL = "nomic-embed-text:latest"

# Vector Database Configuration
VECTORDB_PATH = "./data/vectordb"
COLLECTION_NAME = "safe_mbse_requirements"

# Document Processing
SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.xml', '.json', '.aird', '.capella', '.md']
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Streamlit Configuration
PAGE_TITLE = "SAFE MBSE Requirements Generator"
PAGE_ICON = "🏗️"

# Requirements Generation Settings
REQUIREMENTS_OUTPUT_FORMATS = ["JSON", "DOORS", "ReqIF", "Excel", "Markdown"]
DEFAULT_OUTPUT_FORMAT = "JSON"

# Evaluation Settings
CYDERCO_BENCHMARK_PATH = "./data/examples/cyderco_analysis.md"
EVALUATION_METRICS = [
    "requirement_accuracy",
    "cyderco_coverage",
    "arcadia_compliance",
    "stakeholder_satisfaction"
]

# AI Model Configuration
AI_MODELS = {
    "requirements_generation": {
        "model": "gemma3:27b",
        "temperature": 0.3,
        "max_tokens": 2000
    },
    "validation": {
        "model": "gemma3:12b", 
        "temperature": 0.1,
        "max_tokens": 1000
    },
    "evaluation": {
        "model": "llama3:instruct",
        "temperature": 0.2,
        "max_tokens": 1500
    }
}