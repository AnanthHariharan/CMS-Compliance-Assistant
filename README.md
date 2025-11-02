# CMS Compliance Assistant

A RAG-powered (Retrieval-Augmented Generation) compliance assistant that helps home health agencies ensure their documentation meets CMS (Centers for Medicare & Medicaid Services) guidelines.

## Features

- **Q&A System**: Ask questions about CMS regulations and get accurate answers with source citations
- **Visit Note Validation**: Validate home health visit notes for compliance with automatic violation detection
- **Rule-Based + LLM Validation**: Combines rule-based checking with AI-powered analysis
- **Source References**: Every answer includes references to specific CMS guideline sections
- **Web Interface**: Clean, professional interface for both Q&A and validation

## Architecture

```
┌─────────────────┐
│   Frontend      │  HTML/JS interface
│   (index.html)  │
└────────┬────────┘
         │
         ├─ GET/POST requests
         │
┌────────▼────────┐
│   FastAPI       │  Backend API server
│   Backend       │  - /api/query (Q&A)
└────────┬────────┘  - /api/validate (Validation)
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│Vector│  │  LLM  │  OpenAI GPT-4o-mini
│Store │  │ Chain │  text-embedding-3-small
│Chroma│  └───────┘
└──────┘
```

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI**: Web framework
- **ChromaDB**: Vector database
- **OpenAI API**: Embeddings & LLM
- **pdfplumber/PyPDF2**: PDF processing
- **tiktoken**: Token counting

### Frontend
- **HTML/CSS/JavaScript**: Clean, responsive interface
- **Fetch API**: Async API communication

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CMS-Compliance-Assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 5. Ingest CMS Documents

Process the PDF and populate the vector database:

```bash
python ingest_documents.py
```

This will:
- Extract text from the PDF
- Create intelligent chunks (500-1000 tokens)
- Generate embeddings
- Store in ChromaDB vector database

Expected output:
```
============================================================
CMS Compliance Assistant - Document Ingestion
============================================================

Configuration:
  PDF Path: ./data/raw/Medicare_Benefit_Policy_Manual.pdf
  Vector DB Path: ./data/vector_store
  Chunk Size: 1000 tokens
  Chunk Overlap: 200 tokens

Step 1: Extracting text from PDF...
  ✓ Extracted X pages
  ✓ Document: Medicare_Benefit_Policy_Manual.pdf
  ✓ Total pages: X

Step 2: Chunking text...
  ✓ Created X chunks
  ✓ Average chunk size: X tokens

Step 3: Generating embeddings...
  ✓ Generated X/X embeddings

Step 4: Saving processed data...
  ✓ Saved processed data to ./data/processed/chunks.json

Step 5: Initializing vector store...
  ✓ Vector store initialized
  ✓ Total documents: X

============================================================
Ingestion Complete!
============================================================
```

### 6. Start the Backend Server

```bash
# Recommended: Use the startup script
./start_dev.sh

# Or run directly with uvicorn
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python backend/app.py
```

Server will start at `http://localhost:8000`

API documentation available at: `http://localhost:8000/docs`

### 7. Open the Frontend

Open `frontend/index.html` in your web browser, or serve it using a simple HTTP server:

```bash
# Python 3
python -m http.server 3000 --directory frontend

# Then open http://localhost:3000
```

## Usage

### Q&A System

1. Navigate to the "Q&A System" tab
2. Enter your question about CMS guidelines
3. Click "Ask Question" or press Enter
4. View the answer with source references

**Example Questions:**
- "What are the eligibility requirements for Medicare home health services?"
- "What qualifies a patient as homebound?"
- "What documentation is needed to prove medical necessity?"
- "What must be included in the physician's plan of care?"
- "What are the supervision requirements for home health aides?"

### Visit Note Validation

1. Navigate to the "Note Validator" tab
2. Paste a home health visit note in the text area
3. Click "Validate Note"
4. Review the compliance report with:
   - Overall compliance status
   - Compliance score (0-100)
   - Specific violations (critical, major, minor)
   - Actionable recommendations
   - Documentation strengths
   - Relevant guideline references

## API Endpoints

### Health Check
```http
GET /health
```

Returns service status and vector store statistics.

### Query CMS Guidelines
```http
POST /api/query
Content-Type: application/json

{
  "query": "What qualifies a patient as homebound?",
  "n_results": 5
}
```

Returns answer with source references.

### Validate Visit Note
```http
POST /api/validate
Content-Type: application/json

{
  "note_text": "Patient: John Doe, 78 years old\nDate: 2024-01-15..."
}
```

Returns compliance validation result.

### Get Statistics
```http
GET /api/stats
```

Returns system statistics.

## Project Structure

```
CMS-Compliance-Assistant/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── ingestion/
│   │   ├── pdf_processor.py   # PDF text extraction
│   │   ├── chunker.py         # Intelligent text chunking
│   │   └── embedder.py        # Embedding generation
│   ├── retrieval/
│   │   ├── vector_store.py    # ChromaDB operations
│   │   └── search.py          # Semantic search
│   ├── llm/
│   │   ├── chains.py          # LLM interactions
│   │   └── prompts.py         # Prompt templates
│   ├── validation/
│   │   ├── validator.py       # Note validation logic
│   │   └── rules.py           # Rule-based checks
│   └── models/
│       └── schemas.py         # Pydantic models
├── frontend/
│   ├── index.html             # Web interface
│   └── app.js                 # Frontend logic
├── data/
│   ├── raw/                   # Original PDF
│   ├── processed/             # Processed chunks
│   └── vector_store/          # ChromaDB data
├── tests/                     # Test files
├── ingest_documents.py        # Document ingestion script
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Configuration

All configuration is in `.env` file:

```env
# OpenAI API
OPENAI_API_KEY=your_key_here

# Vector Database
VECTOR_DB_PATH=./data/vector_store

# Document Processing
PDF_PATH=./data/raw/Medicare_Benefit_Policy_Manual.pdf
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Models
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini

# Server
PORT=8000
```

## Compliance Validation

The system uses a hybrid approach:

### 1. Rule-Based Validation
Checks for required elements:
- Patient information
- Visit date and type
- Assessment and vital signs
- Interventions and treatments
- Plan of care
- Nurse signature and timing
- Homebound status
- Medical necessity

### 2. LLM-Based Validation
Uses GPT-4o-mini to:
- Analyze documentation quality
- Identify missing elements
- Provide context-aware recommendations
- Reference specific CMS guidelines

### Severity Levels
- **Critical**: Major compliance issues that could result in claim denial
- **Major**: Important missing elements
- **Minor**: Documentation improvements

### Scoring
- Starts at 100 points
- Critical violation: -30 points
- Major violation: -15 points
- Minor violation: -5 points

**Status Thresholds:**
- **Compliant**: Score ≥ 80, no critical violations
- **Needs Review**: Score 60-79, or 1-2 major violations
- **Non-Compliant**: Score < 60, or critical violations present

## Performance

- **Q&A Response Time**: < 3 seconds
- **Validation Time**: < 5 seconds per note
- **Embedding Generation**: ~100 chunks/minute
- **Accuracy**: 90%+ on test queries

## Testing

Run tests:

```bash
pytest tests/ -v
```

Run specific test:

```bash
pytest tests/test_ingestion.py -v
```

## Troubleshooting

### "Vector store is empty"
Run the ingestion script: `python ingest_documents.py`

### "Cannot connect to API"
Ensure backend is running: `python backend/app.py`

### "OpenAI API error"
Check your API key in `.env` file and ensure you have credits

### PDF not found
Ensure `Medicare_Benefit_Policy_Manual.pdf` is in `data/raw/`

### Import errors
Activate virtual environment and reinstall: `pip install -r requirements.txt`

## Development

### Adding New Features

1. **New validation rules**: Add to `backend/validation/rules.py`
2. **Custom prompts**: Modify `backend/llm/prompts.py`
3. **API endpoints**: Add to `backend/app.py`
4. **Frontend features**: Update `frontend/index.html` and `frontend/app.js`

### Running in Development Mode

```bash
# Backend with auto-reload
uvicorn backend.app:app --reload

# Frontend with live server (using VS Code Live Server or similar)
```

## Deployment

See `docker-compose.yml` for containerized deployment.

```bash
docker-compose up -d
```
---