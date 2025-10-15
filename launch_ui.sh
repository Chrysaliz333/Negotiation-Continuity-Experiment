#!/bin/bash
# Launch Streamlit UI for Negotiation Continuity Experiment

echo "================================================================================"
echo "NEGOTIATION CONTINUITY EXPERIMENT - STREAMLIT UI"
echo "================================================================================"
echo ""

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if FalkorDB container is running
if ! docker ps | grep -q falkordb; then
    echo "⚠️  FalkorDB is not running. Starting it now..."
    docker start falkordb
    sleep 3
fi

# Check if FalkorDB started successfully
if docker ps | grep -q falkordb; then
    echo "✅ FalkorDB is running"
else
    echo "❌ Failed to start FalkorDB"
    exit 1
fi

echo ""
echo "🚀 Launching Streamlit UI..."
echo ""
echo "The UI will open automatically in your browser at:"
echo "   http://localhost:8501"
echo ""
echo "Features:"
echo "  • Natural Language Queries - Ask questions in plain English"
echo "  • Interactive Graph Visualization - See relationships visually"
echo "  • KPI Dashboard - Performance metrics and charts"
echo "  • Real-time Statistics - System stats in sidebar"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================================================"
echo ""

# Activate virtual environment and run Streamlit
source venv/bin/activate && streamlit run app.py
