"""
Base definitions, data contracts, and validation errors for multimodal processing.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ContentValidationError(Exception):
    """Raised when an uploaded media file fails input validation or integrity checks."""
    pass


class NormalizedMetadata(BaseModel):
    """Normalized metadata structure attached to every extracted content item."""
    page: Optional[int] = Field(default=None, description="1-indexed page or slide number")
    timestamp: Optional[str] = Field(default=None, description="Human readable timestamp e.g. 02:30")
    timestamp_start: Optional[float] = Field(default=None, description="Start time in seconds")
    timestamp_end: Optional[float] = Field(default=None, description="End time in seconds")
    section: Optional[str] = Field(default=None, description="Topic or chapter header")
    duration: Optional[float] = Field(default=None, description="Duration of segment in seconds")
    total_pages: Optional[int] = Field(default=None, description="Total pages in source document")
    speaker: Optional[str] = Field(default=None, description="Speaker identifier if transcribed")


class NormalizedContentItem(BaseModel):
    """
    Standardized atomic content unit from any educational modality (PDF, Audio, Video, Notes).
    Guarantees consistent downstream ingestion into RAG and vector stores.
    """
    source: str = Field(..., description="Source filename or identifier")
    content_type: str = Field(..., description="Modality type: 'pdf', 'audio', 'video', 'document'")
    text: str = Field(..., description="Cleaned, normalized educational content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "content_type": self.content_type,
            "text": self.text,
            "metadata": self.metadata
        }


class MultimodalProcessingResult(BaseModel):
    """Complete structured output from processing an educational media file."""
    source: str
    content_type: str
    success: bool = True
    page_count: Optional[int] = None
    duration_seconds: Optional[float] = None
    full_text: str = ""
    items: List[NormalizedContentItem] = Field(default_factory=list)
    error_message: Optional[str] = None

    def to_rag_chunks(self) -> List[Dict[str, Any]]:
        """Converts normalized items into downstream RAG chunk dictionaries."""
        chunks = []
        for idx, item in enumerate(self.items):
            meta = item.metadata or {}
            chunks.append({
                "chunk_index": idx,
                "content": item.text,
                "content_type": item.content_type,
                "media_type": item.content_type,
                "page_number": meta.get("page"),
                "timestamp_start": meta.get("timestamp_start"),
                "timestamp_end": meta.get("timestamp_end"),
                "topic_section": meta.get("section", f"Segment {idx + 1}"),
                "source_filename": item.source,
                "metadata": meta
            })
        return chunks
