import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path for all tests
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def test_pdf_processor():
    """Fixture for PDF processor"""
    from backend.document_processor import PDFProcessor
    return PDFProcessor()

@pytest.fixture
def test_client():
    """Fixture for FastAPI test client"""
    from backend.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)