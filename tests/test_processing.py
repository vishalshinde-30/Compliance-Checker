import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.document_processor import PDFProcessor

def test_pdf_processor_init():
    """Test PDF processor initialization"""
    processor = PDFProcessor()
    assert processor is not None
    assert hasattr(processor, 'text_splitter')

def test_identify_cause():
    """Test cause identification from text"""
    processor = PDFProcessor()
    
    # Test cases
    test_data = [
        ("breach of contract agreement", "Contract Breach"),
        ("data privacy gdpr regulations", "Privacy Violation"),
        ("copyright and trademark issues", "IP Infringement"),
        ("fraudulent misrepresentation", "Fraud"),
        ("payment invoice due date", "Payment Terms"),
        ("normal business agreement", "General Compliance"),
    ]
    
    for text, expected in test_data:
        result = processor.identify_cause(text)
        assert result == expected, f"Failed for: {text}"

def test_empty_text():
    """Test with empty text"""
    processor = PDFProcessor()
    result = processor.identify_cause("")
    assert result == "General Compliance"