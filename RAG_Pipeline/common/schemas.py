"""
Pydantic schemas for the RAG pipeline ingestion system.

This module defines data models for:
- CaseStudyFrontmatter: YAML metadata from case studies
- FileMetadata: File information and processing metadata
- IngestionResult: Processing outcome with metrics
- DocumentChunk: Individual chunk with embedding
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


# ========== Constants ==========

PROJECT_TYPES = Literal[
    "AI_ML",
    "BI_Analytics",
    "Workflow_Automation",
    "Data_Engineering",
    "Web_Development",
    "Mobile_App",
    "API_Integration",
    "Cloud_Migration",
    "Database_Optimization",
    "ETL_Pipeline",
    "Dashboard",
    "Chatbot",
    "Process_Automation",
    "System_Integration",
    "Data_Migration"
]

SOURCE_TYPES = Literal["google_drive", "local_file", "manual_upload"]


# ========== Pydantic Models ==========

class CaseStudyFrontmatter(BaseModel):
    """Metadata extracted from case study YAML frontmatter."""

    title: str = Field(..., description="Case study title")
    client: str = Field(..., description="Client organization name")
    industry: str = Field(..., description="Industry/sector (e.g., 'Home Services', 'E-commerce')")
    project_type: str = Field(
        ...,
        description="Project category (e.g., 'Workflow_Automation', 'AI_ML')"
    )
    technologies_used: List[str] = Field(
        default_factory=list,
        description="Tech stack used in project"
    )
    key_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Quantifiable outcomes (e.g., {'error_reduction': 90, 'time_saved': 50})"
    )
    function: Optional[str] = Field(
        None,
        description="Business function (e.g., 'Customer Support', 'Analytics')"
    )
    project_status: Optional[str] = Field(
        None,
        description="Current status (e.g., 'Ongoing', 'Completed')"
    )


class FileMetadata(BaseModel):
    """File information for document ingestion."""

    file_id: str = Field(..., description="Unique file identifier (path or GDrive ID)")
    file_url: str = Field(..., description="URL or path to access file")
    file_title: str = Field(..., description="Human-readable file name")
    mime_type: str = Field(..., description="MIME type (e.g., 'text/markdown', 'application/pdf')")
    chunk_count: Optional[int] = Field(None, description="Number of chunks created from file")
    source_type: SOURCE_TYPES = Field(..., description="Source of the file")
    case_study_metadata: Optional[CaseStudyFrontmatter] = Field(
        None,
        description="Extracted YAML frontmatter for case studies"
    )


class IngestionResult(BaseModel):
    """Result of file processing for RAG pipeline."""

    success: bool = Field(..., description="Whether processing completed successfully")
    file_id: str = Field(..., description="File identifier that was processed")
    chunks_inserted: int = Field(0, description="Number of document chunks inserted to database")
    rows_inserted: int = Field(0, description="Number of tabular rows inserted (for CSV/Excel)")
    error_message: Optional[str] = Field(None, description="Error description if success=False")
    processing_time_ms: Optional[int] = Field(None, description="Processing duration in milliseconds")
    frontmatter_extracted: bool = Field(False, description="Whether YAML frontmatter was found and parsed")


class DocumentChunk(BaseModel):
    """Individual document chunk with metadata and embedding."""

    content: str = Field(..., description="Text content of the chunk")
    embedding: List[float] = Field(..., description="Vector embedding (e.g., 1536 dims for OpenAI)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSONB metadata (file_id, chunk_index, frontmatter fields, etc.)"
    )
    chunk_index: int = Field(..., description="Sequential index of this chunk within the document")
