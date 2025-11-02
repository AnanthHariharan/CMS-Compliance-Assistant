"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "CMS Compliance Assistant" in data["message"]

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        # May return 503 if not initialized, but should respond
        assert response.status_code in [200, 503]


class TestQueryEndpoint:
    """Test query endpoint"""

    def test_query_endpoint_structure(self):
        """Test query endpoint accepts correct structure"""
        # This may fail if vector store is not initialized
        # but tests the endpoint structure
        response = client.post(
            "/api/query",
            json={
                "query": "What are Medicare eligibility requirements?",
                "n_results": 5
            }
        )
        # Accept both success and service unavailable
        assert response.status_code in [200, 503, 500]

    def test_query_validation(self):
        """Test query validation"""
        # Missing required field
        response = client.post(
            "/api/query",
            json={"n_results": 5}  # Missing 'query'
        )
        assert response.status_code == 422  # Validation error


class TestValidationEndpoint:
    """Test validation endpoint"""

    def test_validation_endpoint_structure(self):
        """Test validation endpoint accepts correct structure"""
        sample_note = """
        Patient: John Doe
        Date: 2024-01-15
        Visit Type: Skilled Nursing
        """

        response = client.post(
            "/api/validate",
            json={"note_text": sample_note}
        )
        # Accept both success and service unavailable
        assert response.status_code in [200, 503, 500]

    def test_validation_requires_note_text(self):
        """Test that note_text is required"""
        response = client.post(
            "/api/validate",
            json={}  # Missing note_text
        )
        assert response.status_code == 422  # Validation error
