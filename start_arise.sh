#!/bin/bash
echo "🚀 Starting ARISE System..."
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️ Virtual environment not found - using system Python"
fi

# Check if Ollama server is accessible
echo "🤖 Checking Ollama connectivity..."
python -c "import requests; requests.get('http://llm-eva.univ-pau.fr:11434/api/tags', timeout=5)" 2>/dev/null && echo "✅ Ollama server accessible" || echo "⚠️ Ollama server not accessible"

# Start the application
echo "🌟 Launching ARISE..."
streamlit run ui/app.py --server.port 8501 --server.address localhost
