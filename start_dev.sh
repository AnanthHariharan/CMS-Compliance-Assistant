#!/bin/bash

# Start development environment

echo "================================="
echo "Starting CMS Compliance Assistant"
echo "================================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and add your OpenAI API key"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if vector store exists
if [ ! -d "data/vector_store" ] || [ -z "$(ls -A data/vector_store 2>/dev/null)" ]; then
    echo ""
    echo "Warning: Vector store not found or empty!"
    echo "Please run: python ingest_documents.py"
    echo ""
    read -p "Do you want to run ingestion now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python ingest_documents.py
    else
        echo "Continuing without ingestion..."
    fi
fi

# Start backend
echo ""
echo "Starting backend server on http://localhost:8000..."
echo "API docs will be available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run from project root
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
