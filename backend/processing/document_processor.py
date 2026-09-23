"""
Document & PDF processing module for educational materials.
Validates file integrity, extracts text per page using PyMuPDF / Azure Content Understanding,
normalizes formatting, and attaches structured page/section metadata.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from backend.processing.base import (
    NormalizedContentItem,
    MultimodalProcessingResult,
    ContentValidationError
)
from backend.rag.cleaner import ContentCleaner
from backend.processing.chunker import SemanticChunker
from backend.config.settings import settings


class DocumentProcessor:
    """Specialized document processor for PDFs, lecture slides, notes, and markdown documents."""

    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

    @classmethod
    def validate_file(cls, file_path: str, media_type: str = "pdf") -> bool:
        """
        Validates input file existence, size limits, and binary header integrity.
        Raises ContentValidationError if the file is missing, empty, oversized, or corrupted.
        """
        if not os.path.exists(file_path):
            raise ContentValidationError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ContentValidationError(f"File '{Path(file_path).name}' is empty (0 bytes).")

        if file_size > cls.MAX_FILE_SIZE_BYTES:
            raise ContentValidationError(
                f"File '{Path(file_path).name}' exceeds maximum allowed size of 50MB (size: {file_size / (1024*1024):.1f}MB)."
            )

        # PDF Header Integrity Check
        if media_type == "pdf" or file_path.lower().endswith(".pdf"):
            with open(file_path, "rb") as f:
                header = f.read(1024)
                if not header.startswith(b"%PDF-"):
                    raise ContentValidationError(f"File '{Path(file_path).name}' is not a valid PDF file (missing %PDF header).")

        return True

    @classmethod
    def process(cls, file_path: str, media_type: str = "pdf") -> Dict[str, Any]:
        """
        Processes PDF or document and returns dictionary compatible with both
        MultimodalProcessingResult and legacy upload route payloads.
        """
        filename = Path(file_path).name
        try:
            cls.validate_file(file_path, media_type)
        except ContentValidationError as ve:
            return cls._create_error_result(filename, media_type, str(ve))
        except Exception as e:
            return cls._create_error_result(filename, media_type, f"Validation failed: {str(e)}")

        if (media_type == "pdf" or filename.lower().endswith(".pdf")) and PYMUPDF_AVAILABLE:
            return cls._process_pdf_pymupdf(file_path, filename)
        else:
            return cls._process_plain_text_document(file_path, filename, media_type)

    @classmethod
    def process_normalized(cls, file_path: str, media_type: str = "pdf") -> MultimodalProcessingResult:
        """Processes document and returns a strongly-typed MultimodalProcessingResult."""
        raw_result = cls.process(file_path, media_type)
        items = []
        for c in raw_result.get("chunks", []):
            meta = c.get("metadata", {})
            items.append(NormalizedContentItem(
                source=raw_result.get("source", Path(file_path).name),
                content_type=raw_result.get("content_type", media_type),
                text=c["content"],
                metadata={
                    "page": c.get("page_number"),
                    "section": meta.get("section", c.get("topic_section", "Document Content")),
                    "total_pages": raw_result.get("page_count", 1),
                    **meta
                }
            ))

        return MultimodalProcessingResult(
            source=Path(file_path).name,
            content_type=media_type,
            success=raw_result.get("success", True),
            page_count=raw_result.get("page_count"),
            duration_seconds=None,
            full_text=raw_result.get("full_text", ""),
            items=items,
            error_message=raw_result.get("error_message")
        )

    @classmethod
    def _process_pdf_pymupdf(cls, file_path: str, filename: str) -> Dict[str, Any]:
        """Extracts text page-by-page from PDF with section detection and cleaning."""
        chunks: List[Dict[str, Any]] = []
        full_text_parts: List[str] = []
        page_count = 0

        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            chunk_idx = 0

            if page_count == 0:
                doc.close()
                return cls._create_error_result(filename, "pdf", "PDF contains 0 pages.")

            for page_num in range(page_count):
                page = doc[page_num]
                raw_text = page.get_text("text") or ""
                cleaned = ContentCleaner.clean_text(raw_text)

                if not cleaned:
                    continue

                full_text_parts.append(f"--- Page {page_num + 1} ---\n{cleaned}")

                # Extract section title from first non-empty line
                first_line = cleaned.split("\n")[0].strip()
                section_title = first_line[:60] if len(first_line) > 3 else f"Page {page_num + 1}"

                # Semantic chunking if a single page has extensive text
                page_chunks = SemanticChunker.chunk_text(cleaned, max_chars=800, overlap=100)
                for p_chunk in page_chunks:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": p_chunk,
                        "media_type": "pdf",
                        "content_type": "pdf",
                        "page_number": page_num + 1,
                        "timestamp_start": None,
                        "timestamp_end": None,
                        "topic_section": section_title,
                        "metadata": {
                            "page": page_num + 1,
                            "section": section_title,
                            "total_pages": page_count,
                            "source_type": "pdf_page"
                        }
                    })
                    chunk_idx += 1

            doc.close()
        except Exception as e:
            return cls._create_error_result(filename, "pdf", f"PDF extraction error: {str(e)}")

        if not chunks:
            # Fallback if PDF was scanned or image-only
            fallback_text = f"Educational PDF document: {filename} (Total pages: {page_count})."
            chunks.append({
                "chunk_index": 0,
                "content": fallback_text,
                "media_type": "pdf",
                "content_type": "pdf",
                "page_number": 1,
                "timestamp_start": None,
                "timestamp_end": None,
                "topic_section": "Document Overview",
                "metadata": {"page": 1, "total_pages": page_count, "note": "Text-free/Scanned PDF fallback"}
            })

        return {
            "source": filename,
            "content_type": "pdf",
            "success": True,
            "page_count": page_count,
            "duration_seconds": None,
            "full_text": "\n\n".join(full_text_parts),
            "chunks": chunks
        }

    @classmethod
    def _process_plain_text_document(cls, file_path: str, filename: str, media_type: str) -> Dict[str, Any]:
        """Processes plain text, markdown, or notes."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
        except Exception as e:
            return cls._create_error_result(filename, media_type, f"Failed to read document: {str(e)}")

        cleaned = ContentCleaner.clean_text(raw_text)
        if not cleaned:
            cleaned = f"Content from {filename}"

        text_chunks = SemanticChunker.chunk_text(cleaned, max_chars=800, overlap=100)
        chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            first_line = chunk_text.split("\n")[0].strip()
            section_title = first_line[:50] if len(first_line) > 3 else f"Section {idx + 1}"
            chunks.append({
                "chunk_index": idx,
                "content": chunk_text,
                "media_type": "document",
                "content_type": "document",
                "page_number": 1,
                "timestamp_start": None,
                "timestamp_end": None,
                "topic_section": section_title,
                "metadata": {
                    "page": 1,
                    "section": section_title,
                    "source": filename
                }
            })

        return {
            "source": filename,
            "content_type": "document",
            "success": True,
            "page_count": 1,
            "duration_seconds": None,
            "full_text": cleaned,
            "chunks": chunks
        }

    @classmethod
    def _create_error_result(cls, filename: str, content_type: str, error_msg: str) -> Dict[str, Any]:
        """Generates a non-crashing fallback error response."""
        return {
            "source": filename,
            "content_type": content_type,
            "success": False,
            "page_count": 0,
            "duration_seconds": None,
            "full_text": "",
            "error_message": error_msg,
            "chunks": [{
                "chunk_index": 0,
                "content": f"[Error Processing {filename}]: {error_msg}",
                "media_type": content_type,
                "content_type": content_type,
                "page_number": 1,
                "timestamp_start": None,
                "timestamp_end": None,
                "topic_section": "Processing Error",
                "metadata": {"error": error_msg}
            }]
        }
