#!/bin/bash
set -e  # Exit on any error

# Quick start script for SECI Search API

echo "=========================================="
echo "SECI Search API - Quick Start"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
if ! source venv/bin/activate; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "Installation complete!"
echo ""
echo "To start the API server:"
echo "  python api.py"
echo ""
echo "Or for production:"
echo "  uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4"
echo ""
echo "To run the example:"
echo "  python examples/perplexity_search.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "=========================================="
