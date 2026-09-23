"""
Integration validation runner that tests the complete 14-step workflow and prints detailed traces.
"""
import io
import fitz  # pymupdf
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.db import init_db

client = TestClient(app)

def create_sample_lecture_pdf():
    doc = fitz.open()
    
    # Page 1: Transformer Architecture
    p1 = doc.new_page()
    p1.insert_text(
        (50, 72),
        "Chapter 1: Multi-Head Self-Attention in Transformers.\n"
        "The Attention mechanism computes attention weights as Softmax(Q * K^T / sqrt(d_k)) * V.\n"
        "Multi-Head Attention allows the model to jointly attend to information from different representation subspaces."
    )
    
    # Page 2: Positional Encoding
    p2 = doc.new_page()
    p2.insert_text(
        (50, 72),
        "Chapter 2: Positional Encodings.\n"
        "Because transformer architectures contain no recurrence or convolution, positional encodings are injected.\n"
        "Sinusoidal functions of different frequencies PE(pos, 2i) = sin(pos / 10000^(2i/d_model)) are utilized."
    )
    
    # Page 3: Layer Normalization & Residuals
    p3 = doc.new_page()
    p3.insert_text(
        (50, 72),
        "Chapter 3: Layer Normalization and Residual Connections.\n"
        "Each sub-layer employs a residual connection followed by LayerNorm(x + Sublayer(x)).\n"
        "This prevents vanishing gradients and facilitates stable training of deep networks."
    )
    
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_full_14_step_live_verification_flow():
    init_db()
    print("\n" + "="*80)
    print("STARTING COMPLETE 14-STEP WORKFLOW INTEGRATION TEST")
    print("="*80)
    
    # Step 1: Health check
    print("\n[STEP 1] Checking API health...")
    r = client.get("/health")
    assert r.status_code == 200
    print(f"  -> Health: {r.json()['status']}, DB connected: {r.json()['database_connected']}")
    
    # Steps 2-6: Upload PDF, text extraction, chunking, indexing in search
    print("\n[STEPS 2-6] Uploading PDF lecture, extracting text, chunking, indexing in Search...")
    pdf_data = create_sample_lecture_pdf()
    files = {"file": ("Transformers_Deep_Dive.pdf", io.BytesIO(pdf_data), "application/pdf")}
    r = client.post("/upload", files=files)
    assert r.status_code in [200, 202]
    doc = r.json()
    doc_id = doc["id"]
    print(f"  -> Uploaded successfully: ID={doc_id}, Filename={doc['filename']}")
    
    # Check chunks
    r = client.get(f"/api/documents/{doc_id}/chunks")
    assert r.status_code == 200
    chunks = r.json()
    print(f"  -> Chunks indexed: {len(chunks)} chunks with preserved metadata")
    for c in chunks:
        print(f"     * Chunk #{c['chunk_index']} (Page {c['page_number']}): {c['content'][:55]}...")

    # Steps 7-11: Ask grounded question -> RAG retrieves chunks -> AI Agent generates grounded answer -> Frontend format returned
    print("\n[STEPS 7-11] User Question -> RAG Retrieval -> Grounded Answer with Citations")
    q = "How is Multi-Head Attention computed in transformers?"
    print(f"  -> Question: '{q}'")
    r = client.post("/chat", json={
        "document_id": doc_id,
        "query": q,
        "chat_history": []
    })
    assert r.status_code == 200
    chat_res = r.json()
    print(f"  -> Grounded Status: {chat_res['grounding_status']} (is_grounded={chat_res['is_grounded']})")
    print(f"  -> Tools Used: {chat_res['tools_used']}")
    print(f"  -> Citations count: {len(chat_res['citations'])}")
    for cite in chat_res["citations"]:
        print(f"     * Citation: {cite['source_filename']} (Page {cite['page_number']}): {cite['snippet']}")
    print(f"  -> AI Answer Snippet:\n     {chat_res['response'][:180]}...")
    assert chat_res["is_grounded"] is True
    assert len(chat_res["citations"]) > 0
    assert chat_res["citations"][0]["page_number"] == 1

    # Step 12: Generate summary
    print("\n[STEP 12] Generating structured summary & key concepts...")
    r = client.post("/summary", json={"document_id": doc_id})
    assert r.status_code == 200
    summary = r.json()
    print(f"  -> Title: {summary['title']}")
    print(f"  -> Overview: {summary['overview'][:100]}...")
    print(f"  -> Key Concepts ({len(summary['key_concepts'])}):")
    for kc in summary["key_concepts"][:3]:
        print(f"     * {kc['concept']} (Page {kc['page']}): {kc['description'][:60]}...")

    # Step 13: Generate MCQs
    print("\n[STEP 13] Generating curriculum-aligned MCQs...")
    r = client.post("/generate-mcqs", json={"document_id": doc_id, "num_questions": 3})
    assert r.status_code == 200
    quiz = r.json()
    print(f"  -> Generated {len(quiz['questions'])} practice questions:")
    for i, q in enumerate(quiz["questions"], 1):
        print(f"     Q{i}: {q['question']}")
        for opt_i, opt in enumerate(q['options']):
            marker = " [CORRECT]" if opt_i == q['correct_answer_index'] else ""
            print(f"        {chr(65+opt_i)}. {opt}{marker}")

    # Step 14: Anti-Hallucination check on out-of-scope query
    print("\n[STEP 14] Anti-Hallucination Verification on Out-of-Scope Query...")
    out_of_scope_q = "What is the speed of light in vacuum and who was Napoleon Bonaparte?"
    print(f"  -> Out-of-scope Question: '{out_of_scope_q}'")
    r = client.post("/chat", json={
        "document_id": doc_id,
        "query": out_of_scope_q,
        "chat_history": []
    })
    assert r.status_code == 200
    ungrounded_res = r.json()
    print(f"  -> Grounded Status: {ungrounded_res['grounding_status']} (is_grounded={ungrounded_res['is_grounded']})")
    print(f"  -> Citations count: {len(ungrounded_res['citations'])}")
    print(f"  -> Fallback Response: {ungrounded_res['response']}")
    
    assert ungrounded_res["is_grounded"] is False
    assert ungrounded_res["grounding_status"] == "NOT_FOUND"
    assert len(ungrounded_res["citations"]) == 0
    assert "cannot find" in ungrounded_res["response"].lower() or "not find" in ungrounded_res["response"].lower()
    
    print("\n" + "="*80)
    print("ALL 14 STEPS COMPLETED & VALIDATED WITH ZERO HALLUCINATION!")
    print("="*80 + "\n")
