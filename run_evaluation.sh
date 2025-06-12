#!/bin/bash

# SAFE MBSE RAG System - Quick Evaluation Launcher
# This script runs a comprehensive evaluation of the system

echo "🚀 SAFE MBSE RAG System - Quick Evaluation"
echo "=" * 50

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected. Attempting to activate..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Please create one with: python -m venv venv"
        exit 1
    fi
fi

echo "📊 Starting system evaluation..."
echo ""

# Run the evaluation script
python scripts/evaluate_system.py

echo ""
echo "✅ Evaluation completed!"
echo ""

# Check if evaluation report was generated
if ls evaluation_report_*.json 1> /dev/null 2>&1; then
    latest_report=$(ls -t evaluation_report_*.json | head -n1)
    echo "📄 Latest report: $latest_report"
    
    # Show quick summary
    echo ""
    echo "📋 Quick Summary:"
    echo "----------------"
    python -c "
import json
try:
    with open('$latest_report', 'r') as f:
        data = json.load(f)
    summary = data.get('summary', {})
    print(f'Overall Health: {summary.get(\"overall_health\", \"Unknown\")}')
    
    issues = summary.get('critical_issues', [])
    if issues:
        print(f'Critical Issues: {len(issues)}')
        for issue in issues:
            print(f'  • {issue}')
    else:
        print('Critical Issues: None')
        
    recs = summary.get('recommendations', [])
    if recs:
        print(f'Recommendations: {len(recs)}')
        for rec in recs:
            print(f'  • {rec}')
except Exception as e:
    print(f'Error reading report: {e}')
"
else
    echo "⚠️  No evaluation report found"
fi

echo ""
echo "🎯 For detailed analysis, check the evaluation_report_*.json file"
echo "📈 For continuous monitoring, see evaluation_framework.md" 