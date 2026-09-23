import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.db import SessionLocal, init_db
from backend.agent.agent_service import agent_service
from backend.agent.tools import (
    tool_search_educational_content,
    tool_generate_summary,
    tool_extract_key_concepts,
    tool_generate_mcqs,
    tool_find_video_timestamps,
    tool_explain_in_simple_terms
)

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_lecture_data():
    init_db()
    # Ingest a sample multimodal lecture document
    lecture_text = """Lecture 04: Convolutional Neural Networks and Optimization.
Gradient descent is an iterative first-order optimization algorithm. The learning rate dictates the step size taken in gradient space.
Convolutional layers use spatial filters and kernels to extract visual features from images.
Pooling layers reduce spatial dimensionality while preserving dominant feature activations."""

    res = client.post(
        "/api/upload",
        files={"file": ("Lecture_04_CNN_Optimization.txt", io.BytesIO(lecture_text.encode("utf-8")), "text/plain")}
    )
    assert res.status_code == 202
    doc_id = res.json()["id"]
    return doc_id


def test_tool_1_search_educational_content(setup_lecture_data):
    doc_id = setup_lecture_data
    db = SessionLocal()
    try:
        result = tool_search_educational_content(db, query="What does the learning rate dictate in gradient descent?", document_id=doc_id)
        assert result["has_content"] is True
        assert len(result["retrieved_chunks"]) > 0
        assert len(result["citations"]) > 0
        assert "step size" in result["retrieved_chunks"][0]["content"].lower()
    finally:
        db.close()


def test_tool_2_generate_summary(setup_lecture_data):
    doc_id = setup_lecture_data
    db = SessionLocal()
    try:
        result = tool_generate_summary(db, document_id=doc_id)
        assert result["document_id"] == doc_id
        assert "overview" in result
        assert len(result["key_concepts"]) > 0
        assert len(result["action_items"]) > 0
    finally:
        db.close()


def test_tool_3_extract_key_concepts(setup_lecture_data):
    doc_id = setup_lecture_data
    db = SessionLocal()
    try:
        result = tool_extract_key_concepts(db, document_id=doc_id)
        assert result["document_id"] == doc_id
        assert len(result["key_concepts"]) >= 1
        assert "concept" in result["key_concepts"][0]
        assert "description" in result["key_concepts"][0]
    finally:
        db.close()


def test_tool_4_generate_mcqs(setup_lecture_data):
    doc_id = setup_lecture_data
    db = SessionLocal()
    try:
        result = tool_generate_mcqs(db, document_id=doc_id, num_questions=3, difficulty="medium")
        assert len(result["questions"]) >= 1
        q = result["questions"][0]
        assert len(q["options"]) == 4
        assert 0 <= q["correct_answer_index"] < 4
        assert "explanation" in q
    finally:
        db.close()


def test_tool_5_find_video_timestamps(setup_lecture_data):
    doc_id = setup_lecture_data
    db = SessionLocal()
    try:
        # Tool works across all media (transcripts and timestamped intervals)
        result = tool_find_video_timestamps(db, query="convolutional layers", document_id=doc_id)
        assert "timestamps" in result
        assert result["document_id"] == doc_id
    finally:
        db.close()


def test_tool_6_explain_in_simple_terms(setup_lecture_data):
    doc_id = setup_lecture_data
    db = SessionLocal()
    try:
        result = tool_explain_in_simple_terms(db, topic="gradient descent", document_id=doc_id)
        assert result["is_grounded"] is True
        assert "simple" in result["explanation"].lower() or "intuition" in result["explanation"].lower()
    finally:
        db.close()


def test_agent_intent_routing_and_out_of_scope(setup_lecture_data):
    doc_id = setup_lecture_data
    db = SessionLocal()
    try:
        # Test 1: User says "Summarize this lecture."
        summary_chat = agent_service.chat(db, query="Summarize this lecture.", document_id=doc_id)
        assert "generate_summary" in summary_chat["tools_used"]
        assert summary_chat["is_grounded"] is True

        # Test 2: User says "Explain gradient descent in simple terms"
        simple_chat = agent_service.chat(db, query="Explain gradient descent in simple terms", document_id=doc_id)
        assert "explain_in_simple_terms" in simple_chat["tools_used"]

        # Test 3: User asks completely unrelated query
        unrelated = agent_service.chat(db, query="What is the capital of Antarctica?", document_id=doc_id)
        assert unrelated["is_grounded"] is False or "cannot find" in unrelated["response"].lower()
    finally:
        db.close()
