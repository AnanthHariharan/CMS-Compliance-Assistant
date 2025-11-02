# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required. For production, implement API key or OAuth2.

## Endpoints

### 1. Health Check

Check service status and vector store statistics.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "vector_store_count": 1234,
  "message": "Service is operational"
}
```

**Status Codes:**
- `200`: Service healthy
- `503`: Service not initialized

---

### 2. Root

Get API information.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "CMS Compliance Assistant API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### 3. Query CMS Guidelines

Ask questions about CMS regulations and get answers with source citations.

**Endpoint:** `POST /api/query`

**Request Body:**
```json
{
  "query": "What qualifies a patient as homebound?",
  "n_results": 5
}
```

**Parameters:**
- `query` (string, required): The question to ask
- `n_results` (integer, optional): Number of context chunks to retrieve (1-10, default: 5)

**Response:**
```json
{
  "answer": "According to CMS guidelines, a patient is considered homebound when...",
  "sources": [
    {
      "text": "A patient is considered homebound if...",
      "page_number": 42,
      "section_header": "Homebound Definition",
      "similarity_score": 0.92
    }
  ],
  "query": "What qualifies a patient as homebound?"
}
```

**Status Codes:**
- `200`: Success
- `422`: Validation error (invalid request)
- `500`: Server error
- `503`: Service not initialized

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the eligibility requirements?",
    "n_results": 5
  }'
```

---

### 4. Query with Streaming

Same as query endpoint but streams the response.

**Endpoint:** `POST /api/query/stream`

**Request Body:** Same as `/api/query`

**Response:** Streamed text (text/plain)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/query/stream" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are Medicare requirements?"}' \
  --no-buffer
```

---

### 5. Validate Visit Note

Validate a home health visit note for CMS compliance.

**Endpoint:** `POST /api/validate`

**Request Body:**
```json
{
  "note_text": "Patient: John Doe, 78 years old\nDate: 2024-01-15\nVisit Type: Skilled Nursing\n\nAssessment: Patient alert and oriented..."
}
```

**Parameters:**
- `note_text` (string, required): The complete visit note text
- `patient_name` (string, optional): Patient name
- `date` (string, optional): Visit date
- `visit_type` (string, optional): Type of visit

**Response:**
```json
{
  "status": "needs_review",
  "overall_score": 75.0,
  "violations": [
    {
      "category": "homebound_status",
      "severity": "critical",
      "description": "Missing homebound status documentation",
      "recommendation": "Document patient's homebound status...",
      "guideline_reference": "Section 30.1.1 - Homebound Requirement"
    }
  ],
  "strengths": [
    "Clear documentation of vital signs",
    "Detailed intervention description"
  ],
  "summary": "This visit note NEEDS REVIEW (Score: 75.0/100). Found 3 issue(s): 1 critical, 2 minor."
}
```

**Compliance Status Values:**
- `compliant`: Score ≥ 80, no critical violations
- `needs_review`: Score 60-79, or 1-2 major violations
- `non_compliant`: Score < 60, or critical violations present

**Severity Levels:**
- `critical`: Major compliance issue, likely claim denial
- `major`: Important missing element
- `minor`: Documentation improvement

**Status Codes:**
- `200`: Success (validation completed)
- `422`: Validation error (invalid request)
- `500`: Server error
- `503`: Service not initialized

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "note_text": "Patient: John Doe, 78 years old\nDate: 2024-01-15..."
  }'
```

---

### 6. Get Statistics

Get system statistics.

**Endpoint:** `GET /api/stats`

**Response:**
```json
{
  "vector_store": {
    "total_chunks": 1234,
    "collection_name": "cms_guidelines",
    "path": "./data/vector_store"
  },
  "status": "operational"
}
```

**Status Codes:**
- `200`: Success
- `503`: Service not initialized

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:
- `422`: Validation error - request body doesn't match expected schema
- `500`: Internal server error
- `503`: Service unavailable - vector store not initialized

---

## Rate Limiting

Currently no rate limiting implemented. For production:
- Recommended: 100 requests per minute per IP
- Implement API key-based rate limiting

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing
- Schema validation
- Request/response examples
- Authentication (when implemented)

---

## Usage Examples

### Python Example

```python
import requests

# Query example
response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "query": "What are the eligibility requirements?",
        "n_results": 5
    }
)
data = response.json()
print(data["answer"])

# Validation example
response = requests.post(
    "http://localhost:8000/api/validate",
    json={
        "note_text": "Your visit note here..."
    }
)
result = response.json()
print(f"Status: {result['status']}")
print(f"Score: {result['overall_score']}")
```

### JavaScript Example

```javascript
// Query example
const queryResponse = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What are the eligibility requirements?',
    n_results: 5
  })
});
const queryData = await queryResponse.json();
console.log(queryData.answer);

// Validation example
const validateResponse = await fetch('http://localhost:8000/api/validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    note_text: 'Your visit note here...'
  })
});
const validationData = await validateResponse.json();
console.log(`Status: ${validationData.status}`);
console.log(`Score: ${validationData.overall_score}`);
```

---

## Best Practices

1. **Error Handling**: Always check response status codes
2. **Timeouts**: Set reasonable timeouts (3-10 seconds for queries, 5-15 seconds for validation)
3. **Retries**: Implement exponential backoff for retries
4. **Caching**: Cache frequently asked questions to reduce API calls
5. **Input Validation**: Validate input on client side before sending

---

## Support

For issues or questions about the API, please refer to the main README.md or create an issue on GitHub.
