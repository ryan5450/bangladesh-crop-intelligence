"""Pydantic schema defining required metadata fields for all knowledge documents."""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class DocumentMetadata(BaseModel):
    """Normalized metadata container conforming to project RAG readiness specifications."""
    document_id: str = Field(..., description="Unique deterministic identifier (source + hash)")
    title: str = Field(..., description="Human-readable title of publication")
    source: str = Field(..., description="Trusted source institution (BRRI, BARI, DAE, BARC, BAMIS, FAO)")
    url: str = Field(..., description="Original publication download URL")
    language: str = Field(..., description="Document language: 'bn', 'en', or 'bn/en'")
    categories: List[str] = Field(default_factory=list, description="Assigned categories from the 24 taxonomy categories")
    related_crops: List[str] = Field(default_factory=list, description="Crops discussed in the document")
    topics: List[str] = Field(default_factory=list, description="Specific agronomic topics covered")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Confidence & text completeness score from 0.0 to 1.0")
    filename: str = Field(..., description="Canonical filename stored on disk")
    pages: int = Field(default=1, ge=1, description="Total pages in document")
    file_size_kb: float = Field(default=0.0, description="File size in kilobytes")
    author: Optional[str] = Field(default=None, description="Authoring division or scientist")
    extracted_at: str = Field(..., description="Timestamp of extraction in ISO 8601 format")

    model_config = ConfigDict(extra="ignore")

