"""
Pydantic Models
Data schemas for API requests and responses
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for Q&A queries"""
    query: str = Field(..., min_length=1, description="User question")
    n_results: int = Field(default=5, ge=1, le=10, description="Number of context chunks to retrieve")


class SourceReference(BaseModel):
    """Source reference for answers"""
    text: str = Field(..., description="Source text chunk")
    page_number: Optional[int] = Field(None, description="Page number in PDF")
    section_header: str = Field(default="", description="Section header")
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity score")


class QueryResponse(BaseModel):
    """Response model for Q&A queries"""
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceReference] = Field(default=[], description="Source references")
    query: str = Field(..., description="Original query")


class VisitNote(BaseModel):
    """Visit note model"""
    patient_name: Optional[str] = Field(None, description="Patient name")
    date: Optional[str] = Field(None, description="Visit date")
    visit_type: Optional[str] = Field(None, description="Type of visit")
    note_text: str = Field(..., min_length=1, description="Full visit note text")


class ComplianceViolation(BaseModel):
    """Individual compliance violation"""
    category: str = Field(..., description="Violation category")
    severity: str = Field(..., description="Severity: critical, major, minor")
    description: str = Field(..., description="Violation description")
    recommendation: str = Field(..., description="How to fix the violation")
    guideline_reference: str = Field(default="", description="CMS guideline reference")


class ComplianceResult(BaseModel):
    """Compliance validation result"""
    status: str = Field(..., description="compliant, non_compliant, or needs_review")
    overall_score: float = Field(..., ge=0, le=100, description="Overall compliance score")
    violations: List[ComplianceViolation] = Field(default=[], description="List of violations")
    strengths: List[str] = Field(default=[], description="Well-documented aspects")
    summary: str = Field(..., description="Overall compliance summary")


class HealthStatus(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    vector_store_count: int = Field(..., description="Number of documents in vector store")
    message: str = Field(default="", description="Additional information")
