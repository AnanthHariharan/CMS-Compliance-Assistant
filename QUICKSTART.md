# Quick Start Guide

Get the CMS Compliance Assistant up and running in 10 minutes.

## Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- 2GB free disk space
- Internet connection

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/AnanthHariharan/CMS-Compliance-Assistant.git
cd CMS-Compliance-Assistant
```

### 2. Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will take 2-3 minutes.

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Ingest Documents

Process the CMS PDF and create the vector database:

```bash
python ingest_documents.py
```

This will take 5-10 minutes depending on your internet speed. You'll see:
- PDF extraction progress
- Chunking progress
- Embedding generation (uses OpenAI API)
- Vector store initialization

### 6. Start the Server

```bash
# Recommended: Use the convenience script
./start_dev.sh

# Or run directly
python -m uvicorn backend.app:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 7. Open the Frontend

**Option A: Direct File**
Open `frontend/index.html` in your browser.

**Option B: HTTP Server**
```bash
python -m http.server 3000 --directory frontend
```
Then open http://localhost:3000

## First Use

### Try the Q&A System

1. Click the "Q&A System" tab
2. Enter: "What qualifies a patient as homebound?"
3. Click "Ask Question"
4. View the answer with source references

### Try the Validator

1. Click the "Note Validator" tab
2. Copy the sample note provided
3. Click "Validate Note"
4. Review the compliance report

## Verify Everything Works

### Check API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "vector_store_count": 1234,
  "message": "Service is operational"
}
```

### Run Tests
```bash
pytest tests/ -v
```

Or use the script:
```bash
./run_tests.sh
```

## Common Issues

### "Vector store is empty"
**Solution:** Run `python ingest_documents.py`

### "Cannot connect to API"
**Solution:** Make sure backend is running: `./start_dev.sh` or `python -m uvicorn backend.app:app --reload`

### "OpenAI API error"
**Solution:**
- Check your API key in `.env`
- Verify you have API credits at https://platform.openai.com/usage

### "Module not found" errors
**Solution:**
```bash
source venv/bin/activate  # Activate venv
pip install -r requirements.txt  # Reinstall
```

### Port already in use
**Solution:**
```bash
# Change port in .env
PORT=8001

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```


## Docker Alternative

If you prefer Docker:

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Frontend will be at http://localhost:3000
Backend will be at http://localhost:8000

## Getting Help

1. Check the [README.md](README.md) troubleshooting section
2. Review API documentation at http://localhost:8000/docs
3. Check the [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
4. Create an issue on GitHub

## Quick Commands Reference

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Ingest documents
python ingest_documents.py

# Start server
./start_dev.sh
# or
python -m uvicorn backend.app:app --reload

# Run tests
pytest tests/ -v

# Start frontend server
python -m http.server 3000 --directory frontend

# Docker
docker-compose up -d
docker-compose down
```