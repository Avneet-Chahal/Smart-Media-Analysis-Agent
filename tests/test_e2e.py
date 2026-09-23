"""
End-to-End Integration Test for Smart Media Analysis Agent
Simulates the complete user and system workflow:
1. User opens frontend / checks health
2. User uploads multi-page educational PDF lecture
3. Backend receives and validates the file
4. Content processor extracts text per page
5. Content is cleaned and chunked preserving page & section metadata
6. Chunks and embeddings are indexed in Azure AI Search / Indexer
7. User asks a factual question
8. Hybrid RAG retrieves relevant chunks
9. AI Agent receives question and retrieved context
10. Agent generates grounded answer with citations
11. Response format verification (response, citations, tools_used, grounding_status)
12. Generate executive summary, key concepts, and action checklist
13. Generate curriculum-aligned practice MCQs with explanations
14. Anti-hallucination test: Out-of-scope query produces no hallucination
"""

import io
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database.db import init_db, SessionLocal
from backend.models.db_models import Document, DocumentChunk

client = TestClient(app)


def setup_module():
    init_db()


def create_sample_educational_pdf_bytes() -> bytes:
    """Generates real multi-page binary PDF content for testing."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open()
        
        # Page 1: CNN Architecture
        p1 = doc.new_page()
        p1.insert_text(
            (50, 72),
            "Chapter 1: Convolutional Neural Networks (CNNs).\n"
            "Convolutional Neural Networks utilize learnable kernels to extract spatial feature maps from images.\n"
            "Pooling layers reduce spatial dimensionality while preserving dominant feature activations."
        )
        
        # Page 2: Optimization and SGD
        p2 = doc.new_page()
        p2.insert_text(
            (50, 72),
            "Chapter 2: Optimization and Gradient Descent.\n"
            "Stochastic Gradient Descent (SGD) computes parameter updates on mini-batches rather than the entire dataset.\n"
            "The learning rate alpha controls the step size taken along the negative gradient vector.\n"
            "Momentum accelerates gradient updates in directions of persistent gradient vectors."
        )
        
        # Page 3: Regularization & Overfitting
        p3 = doc.new_page()
        p3.insert_text(
            (50, 72),
            "Chapter 3: Regularization and Overfitting Prevention.\n"
            "Overfitting occurs when a neural network memorizes training set noise rather than generalizing.\n"
            "Dropout regularization randomly deactivates a fraction p of hidden units during forward passes.\n"
            "Weight decay (L2 Regularization) penalizes large weight coefficients by adding an L2 penalty term to loss."
        )
        
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes
    except ImportError:
        # Minimal valid PDF binary fallback
        return (
            b"%PDF-1.4\n"
            b"Chapter 1: Convolutional Neural Networks (CNNs).\n"
            b"Chapter 2: Optimization and Gradient Descent with learning rate alpha.\n"
            b"Chapter 3: Regularization and Overfitting with Dropout randomly deactivating neurons."
        )


def test_complete_end_to_end_educational_workflow():
    """
    Executes and validates the full 14-step integration workflow.
    """
    # ------------------------------------------------------------------------
    # STEP 1: System Health Verification
    # ------------------------------------------------------------------------
    health_res = client.get("/api/health")
    assert health_res.status_code == 200
    assert health_res.json()["database_connected"] is True

    # ------------------------------------------------------------------------
    # STEP 2-6: Upload PDF Lecture, Extract, Chunk, Embed & Index
    # ------------------------------------------------------------------------
    pdf_bytes = create_sample_educational_pdf_bytes()
    filename = "Lecture_05_Deep_Learning_Optimization.pdf"

    upload_res = client.post(
        "/api/upload",
        files={"file": (filename, io.BytesIO(pdf_bytes), "application/pdf")}
    )
    assert upload_res.status_code in [200, 202]
    upload_data = upload_res.json()
    doc_id = upload_data["id"]
    assert upload_data["filename"] == filename
    assert upload_data["media_type"] == "pdf"

    # Verify that background processing indexed document chunks
    chunks_res = client.get(f"/api/documents/{doc_id}/chunks")
    assert chunks_res.status_code == 200
    chunks = chunks_res.json()
    assert len(chunks) >= 3

    # Check that metadata (page number, topic section) was strictly preserved
    page_numbers = [c["page_number"] for c in chunks if c["page_number"] is not None]
    assert 1 in page_numbers
    assert 2 in page_numbers
    assert 3 in page_numbers

    # ------------------------------------------------------------------------
    # STEP 7-11: User Question -> Hybrid RAG Retrieval -> Grounded AI Response
    # ------------------------------------------------------------------------
    # Query 1: Regularization & Overfitting
    chat_res1 = client.post("/api/agent/chat", json={
        "document_id": doc_id,
        "query": "What is Dropout regularization and how does it prevent overfitting?",
        "chat_history": []
    })
    assert chat_res1.status_code == 200
    chat_data1 = chat_res1.json()

    # Verify grounded answer
    assert chat_data1["is_grounded"] is True
    assert chat_data1["grounding_status"] == "GROUNDED"
    assert "dropout" in chat_data1["response"].lower()
    assert "search_educational_content" in chat_data1["tools_used"]

    # Verify source citations with Page 3 reference
    assert len(chat_data1["citations"]) >= 1
    citation1 = chat_data1["citations"][0]
    assert citation1["page_number"] == 3
    assert "Lecture_05" in citation1["source_filename"]
    assert "regularization" in citation1["snippet"].lower() or "overfitting" in citation1["snippet"].lower()


    # Query 2: Optimization and SGD
    chat_res2 = client.post("/api/agent/chat", json={
        "document_id": doc_id,
        "query": "Explain how learning rate alpha and momentum affect Gradient Descent",
        "chat_history": [
            {"role": "user", "content": "What is Dropout?"},
            {"role": "assistant", "content": chat_data1["response"]}
        ]
    })
    assert chat_res2.status_code == 200
    chat_data2 = chat_res2.json()
    assert chat_data2["is_grounded"] is True
    assert "learning rate" in chat_data2["response"].lower() or "sgd" in chat_data2["response"].lower()
    assert chat_data2["citations"][0]["page_number"] == 2

    # ------------------------------------------------------------------------
    # STEP 12: Generate Study Summary & Key Concepts
    # ------------------------------------------------------------------------
    summary_res = client.post("/api/agent/summary", json={"document_id": doc_id})
    assert summary_res.status_code == 200
    summary_data = summary_res.json()

    assert "title" in summary_data
    assert len(summary_data["overview"]) > 20
    assert len(summary_data["key_concepts"]) >= 3
    assert len(summary_data["action_items"]) >= 1

    # Also test POST /analyze endpoint
    analyze_res = client.post("/analyze", json={"document_id": doc_id})
    assert analyze_res.status_code == 200
    analyze_data = analyze_res.json()
    assert analyze_data["document_id"] == doc_id
    assert analyze_data["chunks_count"] >= 3
    assert len(analyze_data["key_concepts"]) >= 3

    # ------------------------------------------------------------------------
    # STEP 13: Generate Grounded Practice MCQs
    # ------------------------------------------------------------------------
    quiz_res = client.post("/api/generate-mcqs", json={
        "document_id": doc_id,
        "num_questions": 3,
        "difficulty": "medium"
    })
    assert quiz_res.status_code == 200
    quiz_data = quiz_res.json()

    assert "quiz_id" in quiz_data
    assert len(quiz_data["questions"]) == 3
    q1 = quiz_data["questions"][0]
    assert len(q1["options"]) == 4
    assert 0 <= q1["correct_answer_index"] < 4
    assert "explanation" in q1
    assert q1["citation"] is not None

    # ------------------------------------------------------------------------
    # STEP 14: Anti-Hallucination Verification on Out-of-Scope Query
    # ------------------------------------------------------------------------
    out_of_scope_query = "What is the capital of Antarctica and how does chlorophyll absorb light during photosynthesis?"
    unrelated_res = client.post("/api/agent/chat", json={
        "document_id": doc_id,
        "query": out_of_scope_query,
        "chat_history": []
    })
    assert unrelated_res.status_code == 200
    unrelated_data = unrelated_res.json()

    # STRICT ASSERTIONS: System MUST NOT hallucinate
    assert unrelated_data["is_grounded"] is False
    assert unrelated_data["grounding_status"] == "NOT_FOUND"
    assert len(unrelated_data["citations"]) == 0
    assert "cannot find" in unrelated_data["response"].lower() or "not find" in unrelated_data["response"].lower()


def test_root_endpoints_workflow():
    """
    Validates that root endpoints (/upload, /chat, /summary, /generate-mcqs, /health)
    execute the exact same end-to-end educational workflow reliably.
    """
    # 1. Health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] in ["HEALTHY", "healthy"]

    # 2. Upload
    pdf_bytes = create_sample_educational_pdf_bytes()
    filename = "Root_Test_Lecture.pdf"
    res_upload = client.post(
        "/upload",
        files={"file": (filename, io.BytesIO(pdf_bytes), "application/pdf")}
    )
    assert res_upload.status_code in [200, 202]
    doc_id = res_upload.json()["id"]

    # 3. Chat (Grounded)
    res_chat = client.post("/chat", json={
        "document_id": doc_id,
        "query": "What are Convolutional Neural Networks and how do kernels work?",
        "chat_history": []
    })
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    assert chat_data["is_grounded"] is True
    assert len(chat_data["citations"]) >= 1
    assert chat_data["citations"][0]["page_number"] == 1

    # 4. Summary
    res_summary = client.post("/summary", json={"document_id": doc_id})
    assert res_summary.status_code == 200
    assert len(res_summary.json()["key_concepts"]) >= 1

    # 5. MCQs
    res_mcqs = client.post("/generate-mcqs", json={"document_id": doc_id, "num_questions": 2})
    assert res_mcqs.status_code == 200
    assert len(res_mcqs.json()["questions"]) == 2

    # 6. Anti-Hallucination on ungrounded query
    res_hallucination = client.post("/chat", json={
        "document_id": doc_id,
        "query": "Who won the FIFA world cup in 1998 in France?",
        "chat_history": []
    })
    assert res_hallucination.status_code == 200
    hallucination_data = res_hallucination.json()
    assert hallucination_data["is_grounded"] is False
    assert len(hallucination_data["citations"]) == 0

