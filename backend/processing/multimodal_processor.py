"""
Unified Multimodal Processor for Educational Content.
Routes media files (PDFs, notes, audio recordings, video lectures) to specialized processors,
enforces unified input validation, and produces standardized normalized content items for downstream RAG.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from backend.utils.helpers import detect_media_type
from backend.processing.base import (
    NormalizedContentItem,
    MultimodalProcessingResult,
    ContentValidationError
)
from backend.processing.document_processor import DocumentProcessor
from backend.processing.audio_processor import AudioProcessor
from backend.processing.video_processor import VideoProcessor


class MultimodalProcessor:
    """
    Central multimodal processing coordinator.
    Ensures consistent validation, extraction, metadata enrichment, and normalized output.
    """

    @classmethod
    def validate_file(cls, file_path: str, media_type: Optional[str] = None) -> bool:
        """Validates media file format, presence, size, and header integrity."""
        filename = Path(file_path).name
        resolved_type = media_type or detect_media_type(filename)

        if resolved_type == "unknown":
            raise ContentValidationError(
                f"Unsupported file format for '{filename}'. Allowed formats: PDF, DOCX, TXT, MD, MP3, WAV, M4A, MP4, MOV, MKV, WEBM."
            )

        if resolved_type in ["pdf", "document"]:
            return DocumentProcessor.validate_file(file_path, resolved_type)
        elif resolved_type == "audio":
            return AudioProcessor.validate_file(file_path)
        elif resolved_type == "video":
            return VideoProcessor.validate_file(file_path)
        else:
            raise ContentValidationError(f"Unsupported media format for '{filename}'.")

    @classmethod
    def process_file(cls, file_path: str, media_type: Optional[str] = None) -> MultimodalProcessingResult:
        """
        Main entry point for processing any educational media file.
        Returns a standardized MultimodalProcessingResult.
        """
        filename = Path(file_path).name
        resolved_type = media_type or detect_media_type(filename)

        if resolved_type == "pdf" or filename.lower().endswith(".pdf"):
            return DocumentProcessor.process_normalized(file_path, "pdf")

        elif resolved_type == "audio":
            return AudioProcessor.process_normalized(file_path)

        elif resolved_type == "video":
            return VideoProcessor.process_normalized(file_path)

        elif resolved_type in ["document", "notes"] or filename.lower().endswith((".txt", ".md", ".docx")):
            return DocumentProcessor.process_normalized(file_path, "document")

        else:
            return MultimodalProcessingResult(
                source=filename,
                content_type="unsupported",
                success=False,
                error_message=f"Unsupported media format for file '{filename}'."
            )

    @classmethod
    def process_legacy(cls, file_path: str, media_type: Optional[str] = None) -> Dict[str, Any]:
        """Returns standard dictionary payload for legacy route handlers."""
        filename = Path(file_path).name
        resolved_type = media_type or detect_media_type(filename)

        if resolved_type in ["pdf", "document"]:
            return DocumentProcessor.process(file_path, resolved_type)
        elif resolved_type == "audio":
            return AudioProcessor.process(file_path)
        elif resolved_type == "video":
            return VideoProcessor.process(file_path)
        else:
            return DocumentProcessor.process(file_path, "document")


multimodal_processor = MultimodalProcessor()
