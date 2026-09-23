"""
Unified RAG Engine coordinating cleaning, chunking, embedding, indexing, retrieval, and AI agent context feeding.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.rag.cleaner import ContentCleaner
from backend.rag.chunker import RAGChunker
from backend.rag.embedder import embedder
from backend.rag.indexer import indexer
from backend.rag.retriever import retriever
from backend.rag.ingestion import rag_ingestion
from backend.models.schemas import Citation


class RAGEngine:
    """Orchestrates the entire educational RAG lifecycle for the Smart Media Analysis Agent."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Step 1: Cleans raw extracted text from PDFs, notes, or transcripts."""
        return ContentCleaner.clean_text(text)

    @staticmethod
    def chunk_content(
        text: str,
        source_filename: str,
        content_type: str = "document",
        page_number: Optional[int] = None,
        timestamp_start: Optional[float] = None,
        timestamp_end: Optional[float] = None,
        max_chars: int = 750,
        overlap: int = 100
    ) -> List[Dict[str, Any]]:
        """Step 2 & 3: Splits cleaned content into overlapping chunks with preserved metadata."""
        return RAGChunker.chunk_document(
            text=text,
            source_filename=source_filename,
            content_type=content_type,
            page_number=page_number,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
            max_chars=max_chars,
            overlap=overlap
        )

    @staticmethod
    def generate_embedding(text: str) -> Optional[List[float]]:
        """Step 4: Generates dense vector embedding using Azure OpenAI or local fallback."""
        return embedder.generate_embedding(text)

    @staticmethod
    def index_document_chunks(document_id: str, filename: str, chunks: List[Dict[str, Any]]) -> int:
        """Step 5: Uploads vectors and text chunks into Azure AI Search index."""
        return indexer.index_chunks(document_id=document_id, filename=filename, chunks=chunks)

    @staticmethod
    def ingest_document(
        document_id: str,
        filename: str,
        text: str,
        content_type: str = "notes",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Ingestion pipeline entry point for raw documents."""
        return rag_ingestion.ingest_text_document(
            document_id=document_id,
            filename=filename,
            text=text,
            content_type=content_type,
            db=db
        )

    @staticmethod
    def ingest_pdf_pages(
        document_id: str,
        filename: str,
        pages: List[Dict[str, Any]],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Ingestion pipeline entry point for multi-page PDFs."""
        return rag_ingestion.ingest_pdf_pages(
            document_id=document_id,
            filename=filename,
            pages=pages,
            db=db
        )

    @staticmethod
    def ingest_video_transcript(
        document_id: str,
        filename: str,
        segments: List[Dict[str, Any]],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Ingestion pipeline entry point for video transcripts."""
        return rag_ingestion.ingest_transcript_segments(
            document_id=document_id,
            filename=filename,
            segments=segments,
            content_type="video",
            db=db
        )

    @staticmethod
    def retrieve_context(
        query: str,
        document_id: Optional[str] = None,
        db_chunks: Optional[List[Any]] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Step 6: Retrieves top-k most relevant chunks using hybrid search."""
        return retriever.retrieve(
            query=query,
            document_id=document_id,
            db_chunks=db_chunks,
            top_k=top_k
        )

    @staticmethod
    def build_citations(retrieved_chunks: List[Dict[str, Any]], min_score: float = 0.1) -> List[Citation]:
        """Builds structured Citation objects."""
        return retriever.build_citations(retrieved_chunks, min_score=min_score)

    @staticmethod
    def format_agent_context(retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Formats retrieved chunks with metadata for passing to the AI Agent."""
        return retriever.format_context_for_agent(retrieved_chunks)

    @staticmethod
    def _local_hybrid_search(query: str, chunks: List[Any], top_k: int = 4) -> List[Dict[str, Any]]:
        """Direct access to local hybrid ranking."""
        return retriever._rank_local_chunks(query, chunks, top_k)


rag_engine = RAGEngine()

