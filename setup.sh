#!/bin/bash

# Complete setup script for CMS Compliance Assistant

echo "========================================"
echo "CMS Compliance Assistant - Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Setup environment file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=sk-your-actual-api-key-here"
    echo ""
else
    echo "✓ .env file already exists"
fi

# Check if PDF exists
echo ""
if [ -f "data/raw/Medicare_Benefit_Policy_Manual.pdf" ]; then
    echo "✓ CMS PDF found"
else
    echo "⚠️  Warning: CMS PDF not found at data/raw/Medicare_Benefit_Policy_Manual.pdf"
    echo "   Make sure the PDF is in the correct location before running ingestion"
fi

# Print next steps
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env and add your OpenAI API key"
echo "   nano .env"
echo ""
echo "2. Run document ingestion:"
echo "   python ingest_documents.py"
echo ""
echo "3. Start the server:"
echo "   ./start_dev.sh"
echo "   or: python -m uvicorn backend.app:app --reload"
echo ""
echo "4. Open frontend:"
echo "   open frontend/index.html"
echo ""
echo "Or use the quick start script:"
echo "   ./start_dev.sh"
echo ""
echo "For more information, see:"
echo "   - README.md (detailed documentation)"
echo "   - QUICKSTART.md (quick setup guide)"
echo "   - API_DOCUMENTATION.md (API reference)"
echo "========================================"
