import pytest
from backend.rag.cleaner import ContentCleaner
from backend.rag.chunker import RAGChunker
from backend.rag.embedder import embedder, AzureEmbedder
from backend.rag.indexer import indexer, AzureRAGIndexer
from backend.rag.retriever import retriever, RAGRetriever
from backend.rag.ingestion import rag_ingestion, RAGIngestionModule
from backend.rag.rag_engine import rag_engine
from backend.rag.sample_data import SAMPLE_LECTURE_PDF, SAMPLE_VIDEO_TRANSCRIPT
from backend.search.azure_search import azure_search_manager


def test_stage_1_content_cleaning():
    """Pipeline Stage 1 & 2: Clean raw extracted text and eliminate OCR/formatting artifacts."""
    raw_ocr = "Opti-\nmization algorithms   use \x00learnable   parameters.\n\n\n\nFormula: f(x) = alpha * grad."
    cleaned = ContentCleaner.clean_text(raw_ocr)
    assert "Optimization algorithms" in cleaned
    assert "\x00" not in cleaned
    assert "\n\n\n" not in cleaned
    assert "f(x) = alpha * grad." in cleaned


def test_stage_2_chunking_with_pdf_metadata():
    """Pipeline Stage 3 & 4: Chunk document while strictly preserving page numbers and topics."""
    page_data = SAMPLE_LECTURE_PDF["pages"][1]  # Page 2: Optimization
    chunks = RAGChunker.chunk_document(
        text=page_data["text"],
        source_filename=SAMPLE_LECTURE_PDF["filename"],
        content_type="pdf",
        page_number=page_data["page_number"],
        max_chars=300,
        overlap=50
    )

    assert len(chunks) >= 1
    c = chunks[0]
    assert c["source_filename"] == "Lecture_05_Deep_Learning_Architectures.pdf"
    assert c["content_type"] == "pdf"
    assert c["page_number"] == 2
    assert "Stochastic Gradient Descent" in c["content"]
    assert c["topic_section"] != ""


def test_stage_3_chunking_with_video_timestamps():
    """Pipeline Stage 3 & 4: Chunk transcripts with timestamp start and end markers."""
    segment = SAMPLE_VIDEO_TRANSCRIPT["segments"][1]  # Self-attention at 120s
    chunks = RAGChunker.chunk_document(
        text=segment["text"],
        source_filename=SAMPLE_VIDEO_TRANSCRIPT["filename"],
        content_type="video",
        timestamp_start=segment["timestamp_start"],
        timestamp_end=segment["timestamp_end"]
    )

    assert len(chunks) >= 1
    c = chunks[0]
    assert c["source_filename"] == "Lecture_06_Transformers_and_Attention.mp4"
    assert c["content_type"] == "video"
    assert c["timestamp_start"] == 120.0
    assert c["timestamp_end"] == 350.0
    assert "Softmax" in c["content"]


def test_stage_4_embedding_generation():
    """Pipeline Stage 5: Dense embedding vector generation (1536 dims)."""
    text = "Convolutional neural networks extract feature maps from image tensors."
    vector = embedder.generate_embedding(text)
    assert vector is not None
    assert len(vector) == 1536
    # Verify unit length normalization
    norm_sq = sum(v * v for v in vector)
    assert pytest.approx(norm_sq, abs=1e-3) == 1.0


def test_stage_5_ingestion_and_indexing():
    """Pipeline Stage 1-6: Dedicated Ingestion Module tests for multi-page PDFs and video transcripts."""
    # Test multi-page PDF ingestion
    pdf_res = rag_ingestion.ingest_pdf_pages(
        document_id="doc_pdf_test_101",
        filename=SAMPLE_LECTURE_PDF["filename"],
        pages=SAMPLE_LECTURE_PDF["pages"]
    )
    assert pdf_res["chunks_count"] >= 3
    assert pdf_res["indexed_count"] >= 3
    assert pdf_res["total_pages"] == 3

    # Test video transcript ingestion
    video_res = rag_ingestion.ingest_transcript_segments(
        document_id="doc_vid_test_102",
        filename=SAMPLE_VIDEO_TRANSCRIPT["filename"],
        segments=SAMPLE_VIDEO_TRANSCRIPT["segments"]
    )
    assert video_res["chunks_count"] >= 3
    assert video_res["indexed_count"] >= 3


def test_stage_6_hybrid_retrieval_and_citations():
    """Pipeline Stage 7 & 8: Retrieval of most relevant chunks and verified citation creation."""
    results = rag_engine.retrieve_context(
        query="What is dropout regularization and how does it prevent overfitting?",
        document_id="doc_pdf_test_101",
        top_k=2
    )
    assert len(results) > 0
    top = results[0]
    assert "dropout" in top["content"].lower()
    assert top["page_number"] == 3

    # Verify citation builder
    citations = rag_engine.build_citations(results)
    assert len(citations) > 0
    assert citations[0].page_number == 3
    assert "Lecture_05" in citations[0].source_filename


def test_stage_7_video_timestamp_retrieval():
    """Pipeline Stage 7 & 8: Retrieve specific video timestamps for multi-head attention."""
    results = rag_engine.retrieve_context(
        query="Multi-Head Attention representation subspaces",
        document_id="doc_vid_test_102",
        top_k=2
    )
    assert len(results) > 0
    top = results[0]
    assert top["timestamp_start"] == 350.0
    assert "Multi-Head Attention" in top["content"]


def test_stage_8_agent_grounded_context_formatting():
    """Pipeline Stage 9: Pass retrieved context to AI Agent with source citations and grounding tags."""
    results = rag_engine.retrieve_context(
        query="Stochastic Gradient Descent mini-batches learning rate",
        document_id="doc_pdf_test_101",
        top_k=2
    )
    formatted_context = rag_engine.format_agent_context(results)
    assert "[Source #1:" in formatted_context
    assert "Page 2" in formatted_context
    assert "Stochastic Gradient Descent" in formatted_context


def test_stage_9_anti_hallucination_on_out_of_scope():
    """Pipeline Stage 9: Reduces hallucination by recognizing out-of-scope queries with low/zero confidence."""
    results = rag_engine.retrieve_context(
        query="Explain quantum chromodynamics and gluon plasma physics in mitochondria",
        document_id="doc_pdf_test_101",
        top_k=2
    )
    # The score should be 0 or empty for completely irrelevant queries
    citations = rag_engine.build_citations(results, min_score=0.2)
    assert len(citations) == 0


def test_full_rag_engine_lifecycle():
    """Full lifecycle test: Clean -> Chunk -> Embed -> Index -> Retrieve -> Format Context."""
    raw_doc = (
        "Module 4: Backpropagation through Time (BPTT).\n\n"
        "BPTT unfolds recurrent neural networks across discrete time steps t = 1 to T.\n"
        "Gradients are propagated backwards through unrolled states to update weights."
    )
    ingest_result = rag_engine.ingest_document(
        document_id="doc_rnn_999",
        filename="Recurrent_Networks.txt",
        text=raw_doc,
        content_type="notes"
    )
    assert ingest_result["chunks_count"] >= 1

    retrieved = rag_engine.retrieve_context(
        query="How does Backpropagation through Time unfold networks?",
        document_id="doc_rnn_999",
        top_k=1
    )
    assert len(retrieved) == 1
    assert "unfolds recurrent neural networks" in retrieved[0]["content"]
    assert retrieved[0]["source_filename"] == "Recurrent_Networks.txt"

