import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.db import init_db, SessionLocal
from backend.models.db_models import Document, DocumentChunk

client = TestClient(app)


def setup_module():
    init_db()


@pytest.fixture
def sample_test_doc():
    db = SessionLocal()
    doc = Document(
        filename="Lecture_01_Introduction.txt",
        file_path="storage/uploads/Lecture_01_Introduction.txt",
        media_type="document",
        file_size=1024,
        status="READY"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    chunk = DocumentChunk(
        document_id=doc.id,
        chunk_index=0,
        content="Lecture 1 covers fundamental principles of machine learning and loss functions.",
        media_type="document",
        page_number=1,
        metadata_json={"section": "Introduction"}
    )
    db.add(chunk)
    db.commit()

    doc_id = doc.id
    db.close()
    return doc_id


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "Smart Media Analysis Agent" in data["project"]
    assert "upload" in data["endpoints"]


def test_health_endpoints():
    # Test GET /health (root alias)
    res1 = client.get("/health")
    assert res1.status_code == 200
    assert res1.json()["status"] in ["HEALTHY", "DEGRADED"]

    # Test GET /api/health
    res2 = client.get("/api/health")
    assert res2.status_code == 200
    assert res2.json()["database_connected"] is True


def test_upload_endpoint():
    file_content = b"Chapter 1: Neural Networks and Optimization.\nBackpropagation updates weights via gradient descent."
    res = client.post(
        "/upload",
        files={"file": ("test_lecture.txt", io.BytesIO(file_content), "text/plain")}
    )
    assert res.status_code in [200, 202]
    data = res.json()
    assert data["filename"] == "test_lecture.txt"
    assert data["media_type"] == "document"
    assert "id" in data


def test_chat_endpoint(sample_test_doc):
    # Test POST /chat
    res = client.post("/chat", json={
        "document_id": sample_test_doc,
        "query": "What are the fundamental principles covered in Lecture 1?"
    })
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert data["is_grounded"] is True


def test_summary_endpoint(sample_test_doc):
    # Test POST /summary
    res = client.post("/summary", json={"document_id": sample_test_doc})
    assert res.status_code == 200
    data = res.json()
    assert "overview" in data
    assert "key_concepts" in data


def test_analyze_endpoint(sample_test_doc):
    # Test POST /analyze
    res = client.post("/analyze", json={"document_id": sample_test_doc})
    assert res.status_code == 200
    data = res.json()
    assert data["document_id"] == sample_test_doc
    assert data["filename"] == "Lecture_01_Introduction.txt"
    assert "overview" in data
    assert len(data["key_concepts"]) >= 1


def test_generate_mcqs_endpoint(sample_test_doc):
    # Test POST /generate-mcqs
    res = client.post("/generate-mcqs", json={
        "document_id": sample_test_doc,
        "num_questions": 3,
        "difficulty": "medium"
    })
    assert res.status_code == 200
    data = res.json()
    assert "quiz_id" in data
    assert len(data["questions"]) >= 1
    assert "options" in data["questions"][0]


def test_error_handling_and_validation():
    # 1. Empty chat query -> 400
    res_chat = client.post("/chat", json={"query": "   "})
    assert res_chat.status_code == 400

    # 2. Non-existent document -> 404
    res_summary = client.post("/summary", json={"document_id": "non_existent_id_999"})
    assert res_summary.status_code == 404

    # 3. Invalid schema for quiz -> 422
    res_quiz = client.post("/generate-mcqs", json={"document_id": "doc1", "difficulty": "invalid_difficulty"})
    assert res_quiz.status_code == 422
