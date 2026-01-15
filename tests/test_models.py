import pytest
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.models import DocumentResponse, SimilarityRequest
from datetime import datetime

def test_document_response_model():
    """Test document response model"""
    doc = DocumentResponse(
        id="test123",
        title="Test Document",
        description="Test description",
        category="contract",
        uploaded_at=datetime.now(),
        vector_id="vec123"
    )
    
    assert doc.id == "test123"
    assert doc.title == "Test Document"
    assert doc.category == "contract"

def test_similarity_request_model():
    """Test similarity request model"""
    request = SimilarityRequest(
        query_text="test query",
        threshold=0.7,
        top_k=5
    )
    
    assert request.query_text == "test query"
    assert request.threshold == 0.7
    assert request.top_k == 5

def test_similarity_request_validation():
    """Test validation in similarity request"""
    # Should fail with threshold > 1
    with pytest.raises(ValueError):
        SimilarityRequest(
            query_text="test",
            threshold=1.5,  # Invalid
            top_k=5
        )