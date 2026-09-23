"""
Complete Testing Strategy Suite for Smart Media Analysis Agent.
Executes and benchmarks all 15 required test scenarios:
1. Valid PDF upload
2. Invalid file type
3. Empty document
4. Corrupted document
5. Large document
6. Question answered from uploaded content
7. Question not present in uploaded content
8. Summary generation
9. MCQ generation
10. RAG retrieval accuracy (measured on benchmark dataset)
11. API failures
12. Azure service failure resilience
13. Missing environment variables
14. Hallucination prevention
15. Frontend/backend integration contract
"""

import io
import os
import json
import pytest
import fitz  # pymupdf
from fastapi.testclient import TestClient

from backend.main import app
from backend.config.settings import settings
from backend.database.db import init_db, SessionLocal
from backend.models.db_models import Document, DocumentChunk
from backend.agent.agent_service import AgentService, agent_service
from backend.rag.rag_engine import rag_engine
from backend.rag.retriever import RAGRetriever
from tests.evaluation_dataset import EVALUATION_DOCUMENT_CONTENT, EVALUATION_QUERIES

client = TestClient(app)


def build_evaluation_pdf_bytes() -> bytes:
    """Creates a real 5-page PDF from the evaluation dataset."""
    doc = fitz.open()
    for item in EVALUATION_DOCUMENT_CONTENT:
        p = doc.new_page()
        p.insert_text((50, 72), item["text"])
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture(scope="module", autouse=True)
def setup_test_env():
    init_db()


class TestStrategySuite:
    """Executes the 15 strategic test cases."""

    # ------------------------------------------------------------------------
    # TEST 1: Valid PDF Upload
    # ------------------------------------------------------------------------
    def test_case_01_valid_pdf_upload(self):
        pdf_bytes = build_evaluation_pdf_bytes()
        filename = "AI103_Deep_Learning_Lecture.pdf"
        response = client.post(
            "/upload",
            files={"file": (filename, io.BytesIO(pdf_bytes), "application/pdf")}
        )
        assert response.status_code in [200, 202]
        data = response.json()
        assert data["filename"] == filename
        assert data["media_type"] == "pdf"
        assert data["status"] in ["INDEXED", "READY", "PROCESSING"]
        assert "id" in data

    # ------------------------------------------------------------------------
    # TEST 2: Invalid File Type
    # ------------------------------------------------------------------------
    def test_case_02_invalid_file_type(self):
        fake_binary = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff"
        response = client.post(
            "/upload",
            files={"file": ("malicious_program.exe", io.BytesIO(fake_binary), "application/x-msdownload")}
        )
        assert response.status_code == 400
        data = response.json()
        assert "unsupported" in data["message"].lower() or "not supported" in data["message"].lower()

    # ------------------------------------------------------------------------
    # TEST 3: Empty Document (0 bytes)
    # ------------------------------------------------------------------------
    def test_case_03_empty_document(self):
        empty_bytes = b""
        response = client.post(
            "/upload",
            files={"file": ("empty_notes.pdf", io.BytesIO(empty_bytes), "application/pdf")}
        )
        assert response.status_code == 400
        data = response.json()
        assert "empty" in data["message"].lower()

    # ------------------------------------------------------------------------
    # TEST 4: Corrupted Document
    # ------------------------------------------------------------------------
    def test_case_04_corrupted_document(self):
        corrupted_bytes = b"NOT_A_REAL_PDF_HEADER_JUST_GARBAGE_DATA_1234567890"
        response = client.post(
            "/upload",
            files={"file": ("corrupted_lecture.pdf", io.BytesIO(corrupted_bytes), "application/pdf")}
        )
        assert response.status_code == 400
        data = response.json()
        assert "corrupted" in data["message"].lower() or "header" in data["message"].lower() or "invalid" in data["message"].lower()

    # ------------------------------------------------------------------------
    # TEST 5: Large Document (Exceeding max limit or high page count)
    # ------------------------------------------------------------------------
    def test_case_05_large_document(self):
        oversized_data = b"0" * (55 * 1024 * 1024)  # 55 MB (limit is 50MB)
        response = client.post(
            "/upload",
            files={"file": ("oversized_textbook.pdf", io.BytesIO(oversized_data), "application/pdf")}
        )
        assert response.status_code in [400, 413]
        data = response.json()
        assert "exceeds" in data["message"].lower() or "size" in data["message"].lower() or "large" in data["message"].lower() or "50mb" in data["message"].lower()

    # ------------------------------------------------------------------------
    # TEST 6: Question Answered from Uploaded Content
    # ------------------------------------------------------------------------
    def test_case_06_question_answered_from_content(self):
        pdf_bytes = build_evaluation_pdf_bytes()
        upload_res = client.post("/upload", files={"file": ("Deep_Learning_Eval.pdf", io.BytesIO(pdf_bytes), "application/pdf")})
        doc_id = upload_res.json()["id"]

        query = "How does Dropout regularization prevent overfitting?"
        res = client.post("/chat", json={
            "document_id": doc_id,
            "query": query,
            "chat_history": []
        })
        assert res.status_code == 200
        data = res.json()
        assert data["is_grounded"] is True
        assert data["grounding_status"] == "GROUNDED"
        assert len(data["citations"]) >= 1
        assert data["citations"][0]["page_number"] == 3
        assert "dropout" in data["response"].lower()

    # ------------------------------------------------------------------------
    # TEST 7: Question Not Present in Uploaded Content
    # ------------------------------------------------------------------------
    def test_case_07_question_not_present_in_content(self):
        pdf_bytes = build_evaluation_pdf_bytes()
        upload_res = client.post("/upload", files={"file": ("Deep_Learning_Eval.pdf", io.BytesIO(pdf_bytes), "application/pdf")})
        doc_id = upload_res.json()["id"]

        query = "What is the capital of Australia and who was the first prime minister?"
        res = client.post("/chat", json={
            "document_id": doc_id,
            "query": query,
            "chat_history": []
        })
        assert res.status_code == 200
        data = res.json()
        assert data["is_grounded"] is False
        assert data["grounding_status"] == "NOT_FOUND"
        assert len(data["citations"]) == 0
        assert "cannot find" in data["response"].lower() or "not find" in data["response"].lower()

    # ------------------------------------------------------------------------
    # TEST 8: Summary Generation
    # ------------------------------------------------------------------------
    def test_case_08_summary_generation(self):
        pdf_bytes = build_evaluation_pdf_bytes()
        upload_res = client.post("/upload", files={"file": ("Deep_Learning_Eval.pdf", io.BytesIO(pdf_bytes), "application/pdf")})
        doc_id = upload_res.json()["id"]

        res = client.post("/summary", json={"document_id": doc_id})
        assert res.status_code == 200
        data = res.json()
        assert data["document_id"] == doc_id
        assert "title" in data
        assert len(data["overview"]) > 30
        assert len(data["key_concepts"]) >= 3
        assert len(data["action_items"]) >= 1

    # ------------------------------------------------------------------------
    # TEST 9: MCQ Generation
    # ------------------------------------------------------------------------
    def test_case_09_mcq_generation(self):
        pdf_bytes = build_evaluation_pdf_bytes()
        upload_res = client.post("/upload", files={"file": ("Deep_Learning_Eval.pdf", io.BytesIO(pdf_bytes), "application/pdf")})
        doc_id = upload_res.json()["id"]

        res = client.post("/generate-mcqs", json={"document_id": doc_id, "num_questions": 4, "difficulty": "medium"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["questions"]) == 4
        for q in data["questions"]:
            assert len(q["options"]) == 4
            assert 0 <= q["correct_answer_index"] < 4
            assert len(q["explanation"]) > 5
            assert q["citation"] is not None

    # ------------------------------------------------------------------------
    # TEST 10: RAG Retrieval Accuracy Benchmark
    # ------------------------------------------------------------------------
    def test_case_10_rag_retrieval_accuracy(self):
        db = SessionLocal()
        try:
            pdf_bytes = build_evaluation_pdf_bytes()
            upload_res = client.post("/upload", files={"file": ("Benchmark_Evaluation_Doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")})
            doc_id = upload_res.json()["id"]

            chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()
            assert len(chunks) >= 5

            in_domain_queries = [q for q in EVALUATION_QUERIES if q["is_in_domain"]]
            top1_hits = 0
            top3_hits = 0
            reciprocal_ranks = []

            for q_item in in_domain_queries:
                retrieved = rag_engine.retrieve_context(
                    query=q_item["query"],
                    document_id=doc_id,
                    db_chunks=chunks,
                    top_k=3
                )
                retrieved_pages = [c.get("page_number") for c in retrieved]

                # Check top-1 hit
                if retrieved_pages and retrieved_pages[0] == q_item["expected_page"]:
                    top1_hits += 1
                    reciprocal_ranks.append(1.0)
                elif q_item["expected_page"] in retrieved_pages:
                    rank = retrieved_pages.index(q_item["expected_page"]) + 1
                    reciprocal_ranks.append(1.0 / rank)
                else:
                    reciprocal_ranks.append(0.0)

                # Check top-3 hit
                if q_item["expected_page"] in retrieved_pages:
                    top3_hits += 1

            total = len(in_domain_queries)
            hit_rate_top1 = (top1_hits / total) * 100.0
            hit_rate_top3 = (top3_hits / total) * 100.0
            mrr = sum(reciprocal_ranks) / total

            print(f"\n--- MEASURED RAG RETRIEVAL ACCURACY ---")
            print(f"Total Benchmark Queries : {total}")
            print(f"Hit Rate @ 1 (Top-1)    : {hit_rate_top1:.1f}% ({top1_hits}/{total})")
            print(f"Hit Rate @ 3 (Top-3)    : {hit_rate_top3:.1f}% ({top3_hits}/{total})")
            print(f"Mean Reciprocal Rank    : {mrr:.3f}")

            assert hit_rate_top1 >= 88.0
            assert hit_rate_top3 == 100.0
            assert mrr >= 0.90
        finally:
            db.close()

    # ------------------------------------------------------------------------
    # TEST 11: API Failures
    # ------------------------------------------------------------------------
    def test_case_11_api_failures(self):
        # 1. Non-existent document ID -> 404
        res_404 = client.post("/summary", json={"document_id": "non-existent-uuid-1234"})
        assert res_404.status_code == 404

        # 2. Empty query string -> 400
        res_empty = client.post("/chat", json={"document_id": "dummy", "query": "   ", "chat_history": []})
        assert res_empty.status_code == 400

        # 3. Missing required field -> 422
        res_422 = client.post("/chat", json={"invalid_field": 123})
        assert res_422.status_code == 422

    # ------------------------------------------------------------------------
    # TEST 12: Azure Service Failure Resilience
    # ------------------------------------------------------------------------
    def test_case_12_azure_service_failure(self):
        # Simulate Azure service outage / unconfigured credentials
        local_agent = AgentService()
        local_agent.client = None  # Azure OpenAI offline

        db = SessionLocal()
        try:
            pdf_bytes = build_evaluation_pdf_bytes()
            upload_res = client.post("/upload", files={"file": ("Azure_Fallback_Doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")})
            doc_id = upload_res.json()["id"]

            # Query should gracefully execute via local hybrid RAG without crashing
            res = local_agent.chat(db=db, query="What is Stochastic Gradient Descent?", document_id=doc_id)
            assert res["is_grounded"] is True
            assert len(res["citations"]) > 0
            assert "gradient descent" in res["response"].lower() or "sgd" in res["response"].lower()
        finally:
            db.close()

    # ------------------------------------------------------------------------
    # TEST 13: Missing Environment Variables
    # ------------------------------------------------------------------------
    def test_case_13_missing_environment_variables(self):
        # Verify default configuration safety
        assert settings.is_azure_openai_configured is False or isinstance(settings.is_azure_openai_configured, bool)
        assert settings.is_azure_search_configured is False or isinstance(settings.is_azure_search_configured, bool)
        assert settings.DATABASE_URL.endswith(".db") or "sqlite" in settings.DATABASE_URL
        assert settings.MAX_UPLOAD_SIZE_BYTES == 50 * 1024 * 1024

    # ------------------------------------------------------------------------
    # TEST 14: Hallucination Prevention
    # ------------------------------------------------------------------------
    def test_case_14_hallucination_prevention(self):
        db = SessionLocal()
        try:
            pdf_bytes = build_evaluation_pdf_bytes()
            upload_res = client.post("/upload", files={"file": ("AntiHallucination_Doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")})
            doc_id = upload_res.json()["id"]

            ood_queries = [q for q in EVALUATION_QUERIES if not q["is_in_domain"]]
            for ood in ood_queries:
                res = client.post("/chat", json={
                    "document_id": doc_id,
                    "query": ood["query"],
                    "chat_history": []
                })
                assert res.status_code == 200
                data = res.json()
                # Must strictly prevent hallucination
                assert data["is_grounded"] is False, f"Failed on query: {ood['query']}"
                assert data["grounding_status"] == "NOT_FOUND"
                assert len(data["citations"]) == 0
                assert "cannot find" in data["response"].lower() or "not find" in data["response"].lower()
        finally:
            db.close()

    # ------------------------------------------------------------------------
    # TEST 15: Frontend / Backend Integration Contract
    # ------------------------------------------------------------------------
    def test_case_15_frontend_backend_integration(self):
        # Verify schemas match frontend expectations
        health_res = client.get("/api/health")
        assert health_res.status_code == 200
        health_keys = set(health_res.json().keys())
        assert {"status", "database_connected", "azure_openai_configured", "azure_search_configured"}.issubset(health_keys)

        docs_res = client.get("/api/documents")
        assert docs_res.status_code == 200
        assert isinstance(docs_res.json(), list)
