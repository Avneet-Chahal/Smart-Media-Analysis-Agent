"""
Ingestion module for the Smart Media Analysis Agent RAG Pipeline.
Receives extracted educational content (PDFs, lecture notes, transcripts, audio/video)
and orchestrates cleaning, chunking, metadata enrichment, embedding, and indexing.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.rag.cleaner import ContentCleaner
from backend.rag.chunker import RAGChunker
from backend.rag.embedder import embedder
from backend.rag.indexer import indexer
from backend.models.db_models import DocumentChunk


class RAGIngestionModule:
    """
    Ingestion Module:
    1. Receives raw or structured educational content from multiple media sources.
    2. Cleans text to eliminate OCR/transcript noise while preserving mathematical expressions.
    3. Splits text into semantic chunks while strictly preserving metadata:
       - source_filename
       - content_type (pdf, video, audio, notes, document)
       - page_number (where available)
       - timestamp_start and timestamp_end (where available)
       - topic_section (auto-extracted header/concept)
    4. Generates dense vector embeddings.
    5. Stores and indexes content in Azure AI Search and database.
    """

    @classmethod
    def ingest_text_document(
        cls,
        document_id: str,
        filename: str,
        text: str,
        content_type: str = "notes",
        db: Optional[Session] = None,
        max_chars: int = 750,
        overlap: int = 100
    ) -> Dict[str, Any]:
        """Ingests a raw text or markdown lecture document."""
        cleaned_text = ContentCleaner.clean_text(text)
        chunks = RAGChunker.chunk_document(
            text=cleaned_text,
            source_filename=filename,
            content_type=content_type,
            max_chars=max_chars,
            overlap=overlap
        )

        indexed_count = indexer.index_chunks(document_id=document_id, filename=filename, chunks=chunks)

        if db:
            cls._save_chunks_to_db(db, document_id, chunks)

        return {
            "document_id": document_id,
            "filename": filename,
            "content_type": content_type,
            "chunks_count": len(chunks),
            "indexed_count": indexed_count,
            "chunks": chunks
        }

    @classmethod
    def ingest_pdf_pages(
        cls,
        document_id: str,
        filename: str,
        pages: List[Dict[str, Any]],
        db: Optional[Session] = None,
        max_chars: int = 750,
        overlap: int = 100
    ) -> Dict[str, Any]:
        """
        Ingests multi-page PDF document content with page-level metadata.
        Each page item: {"page_number": int, "text": str}
        """
        all_chunks: List[Dict[str, Any]] = []
        chunk_offset = 0

        for page in pages:
            page_num = page.get("page_number", 1)
            raw_text = page.get("text", "")
            cleaned = ContentCleaner.clean_text(raw_text)
            if not cleaned:
                continue

            page_chunks = RAGChunker.chunk_document(
                text=cleaned,
                source_filename=filename,
                content_type="pdf",
                page_number=page_num,
                max_chars=max_chars,
                overlap=overlap
            )

            # Re-index chunk_index sequentially across pages
            for c in page_chunks:
                c["chunk_index"] = chunk_offset
                chunk_offset += 1
                all_chunks.append(c)

        indexed_count = indexer.index_chunks(document_id=document_id, filename=filename, chunks=all_chunks)

        if db:
            cls._save_chunks_to_db(db, document_id, all_chunks)

        return {
            "document_id": document_id,
            "filename": filename,
            "content_type": "pdf",
            "total_pages": len(pages),
            "chunks_count": len(all_chunks),
            "indexed_count": indexed_count,
            "chunks": all_chunks
        }

    @classmethod
    def ingest_transcript_segments(
        cls,
        document_id: str,
        filename: str,
        segments: List[Dict[str, Any]],
        content_type: str = "video",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Ingests audio/video transcripts with timestamp metadata.
        Each segment: {"timestamp_start": float, "timestamp_end": float, "text": str}
        """
        all_chunks: List[Dict[str, Any]] = []
        chunk_offset = 0

        for seg in segments:
            raw_text = seg.get("text", "")
            cleaned = ContentCleaner.clean_text(raw_text)
            if not cleaned:
                continue

            seg_chunks = RAGChunker.chunk_document(
                text=cleaned,
                source_filename=filename,
                content_type=content_type,
                timestamp_start=seg.get("timestamp_start"),
                timestamp_end=seg.get("timestamp_end"),
                max_chars=600,
                overlap=50
            )

            for c in seg_chunks:
                c["chunk_index"] = chunk_offset
                chunk_offset += 1
                all_chunks.append(c)

        indexed_count = indexer.index_chunks(document_id=document_id, filename=filename, chunks=all_chunks)

        if db:
            cls._save_chunks_to_db(db, document_id, all_chunks)

        return {
            "document_id": document_id,
            "filename": filename,
            "content_type": content_type,
            "total_segments": len(segments),
            "chunks_count": len(all_chunks),
            "indexed_count": indexed_count,
            "chunks": all_chunks
        }

    @staticmethod
    def _save_chunks_to_db(db: Session, document_id: str, chunks: List[Dict[str, Any]]):
        """Persists extracted chunks to SQLite database."""
        for c in chunks:
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                media_type=c.get("content_type", "document"),
                page_number=c.get("page_number"),
                timestamp_start=c.get("timestamp_start"),
                timestamp_end=c.get("timestamp_end"),
                metadata_json={
                    "source_filename": c.get("source_filename"),
                    "topic_section": c.get("topic_section"),
                    "char_length": c.get("char_length")
                }
            )
            db.add(db_chunk)
        db.commit()


rag_ingestion = RAGIngestionModule()
