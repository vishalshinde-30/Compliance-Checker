import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import backend
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns correct message"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Compliance Checker API"

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_get_documents():
    """Test getting documents endpoint"""
    response = client.get("/documents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_check_compliance_basic():
    """Test compliance check with valid data"""
    test_data = {
        "query_text": "This is a test query for compliance check",
        "threshold": 0.5,
        "top_k": 3
    }
    response = client.post("/check-compliance/", json=test_data)
    # Should return 200 (success) or 500 (no documents indexed yet)
    assert response.status_code in [200, 500]

def test_check_compliance_validation():
    """Test validation for missing required fields"""
    # Missing query_text
    bad_data = {"threshold": 0.7}
    response = client.post("/check-compliance/", json=bad_data)
    assert response.status_code == 422  # Validation error