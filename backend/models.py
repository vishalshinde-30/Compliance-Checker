from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class DocumentCategory(str, Enum):
    CONTRACT = "contract"
    POLICY = "policy"
    REGULATION = "regulation"
    CASE_LAW = "case_law"
    OTHER = "other"

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    description: Optional[str] = Field(None, max_length=1000, description="Document description")
    category: DocumentCategory = Field(DocumentCategory.OTHER, description="Document category")

class DocumentCreate(DocumentBase):
    pass  # No file_path here, it comes from upload

class DocumentResponse(DocumentBase):
    id: str
    uploaded_at: datetime
    vector_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class SimilarityRequest(BaseModel):
    query_text: str = Field(..., min_length=10, description="Text to check for compliance")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold (0.0 to 1.0)")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")

class SimilarityResult(BaseModel):
    document_id: str
    document_title: str
    similarity_score: float
    matching_text: str
    cause: str
    
class ComplianceReport(BaseModel):
    query: str
    threshold: float
    total_matches: int
    results_by_cause: dict
    high_risk_causes: List[dict]
    recommendations: List[str]

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    mongo_connected: bool