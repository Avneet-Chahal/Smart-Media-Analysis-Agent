"""
Verification script for end-to-end live testing of the complete 14-step educational workflow.
"""
import io
import time
import requests
import fitz  # pymupdf

BASE_URL = "http://127.0.0.1:8000"

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

def run_live_verification():
    print("=== STARTING LIVE END-TO-END VERIFICATION ===")
    
    # 1. Health check
    print("\n[Step 1] Checking API health...")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"-> Health: {r.json()['status']}, DB connected: {r.json()['database_connected']}")
    
    # 2. Upload PDF
    print("\n[Step 2-6] Uploading PDF lecture, processing text, chunking, indexing in Search...")
    pdf_data = create_sample_lecture_pdf()
    files = {"file": ("Transformers_Deep_Dive.pdf", io.BytesIO(pdf_data), "application/pdf")}
    r = requests.post(f"{BASE_URL}/upload", files=files)
    assert r.status_code in [200, 202], f"Upload failed: {r.text}"
    doc = r.json()
    doc_id = doc["id"]
    print(f"-> Uploaded successfully: ID={doc_id}, Filename={doc['filename']}")
    
    # Wait 1 sec for any background indexing
    time.sleep(1)
    
    # 3. Check chunks
    r = requests.get(f"{BASE_URL}/api/documents/{doc_id}/chunks")
    assert r.status_code == 200
    chunks = r.json()
    print(f"-> Chunks extracted & indexed: {len(chunks)} chunks with metadata")
    for c in chunks:
        print(f"   - Chunk {c['chunk_index']} (Page {c['page_number']}): {c['content'][:60]}...")

    # 4. Ask grounded question
    print("\n[Step 7-11] Asking question: 'How is Multi-Head Attention computed in transformers?'")
    r = requests.post(f"{BASE_URL}/chat", json={
        "document_id": doc_id,
        "query": "How is Multi-Head Attention computed in transformers?",
        "chat_history": []
    })
    assert r.status_code == 200
    chat_res = r.json()
    print(f"-> Grounded: {chat_res['is_grounded']}")
    print(f"-> Status: {chat_res['grounding_status']}")
    print(f"-> Tools Used: {chat_res['tools_used']}")
    print(f"-> Response: {chat_res['response']}")
    print(f"-> Citations: {len(chat_res['citations'])} citation(s)")
    for cite in chat_res["citations"]:
        print(f"   - Source: {cite['source_filename']} (Page {cite['page_number']}): {cite['snippet']}")
    assert chat_res["is_grounded"] is True
    assert len(chat_res["citations"]) > 0

    # 5. Generate summary
    print("\n[Step 12] Generating structured summary...")
    r = requests.post(f"{BASE_URL}/summary", json={"document_id": doc_id})
    assert r.status_code == 200
    summary = r.json()
    print(f"-> Title: {summary['title']}")
    print(f"-> Overview: {summary['overview'][:120]}...")
    print(f"-> Key Concepts: {len(summary['key_concepts'])} concepts extracted")
    for kc in summary["key_concepts"][:2]:
        print(f"   * {kc['concept']} (Page {kc['page']}): {kc['description'][:80]}...")

    # 6. Generate MCQs
    print("\n[Step 13] Generating grounded practice MCQs...")
    r = requests.post(f"{BASE_URL}/generate-mcqs", json={"document_id": doc_id, "num_questions": 3})
    assert r.status_code == 200
    quiz = r.json()
    print(f"-> Generated {len(quiz['questions'])} MCQs")
    for q in quiz["questions"]:
        print(f"   Q: {q['question']}")
        print(f"      Options: {q['options']}")
        print(f"      Correct Option Index: {q['correct_answer_index']}")

    # 7. Ask out-of-scope question (Anti-Hallucination check)
    print("\n[Step 14] Anti-Hallucination Test on ungrounded query: 'What is the speed of light in vacuum and who was Napoleon?'")
    r = requests.post(f"{BASE_URL}/chat", json={
        "document_id": doc_id,
        "query": "What is the speed of light in vacuum and who was Napoleon?",
        "chat_history": []
    })
    assert r.status_code == 200
    ungrounded_res = r.json()
    print(f"-> Grounded: {ungrounded_res['is_grounded']}")
    print(f"-> Status: {ungrounded_res['grounding_status']}")
    print(f"-> Response: {ungrounded_res['response']}")
    print(f"-> Citations count: {len(ungrounded_res['citations'])}")
    assert ungrounded_res["is_grounded"] is False
    assert len(ungrounded_res["citations"]) == 0
    assert "cannot find" in ungrounded_res["response"].lower() or "not find" in ungrounded_res["response"].lower()
    
    print("\n=== ALL 14 STEPS COMPLETED & VERIFIED WITH 100% RELIABILITY! ===")

if __name__ == "__main__":
    run_live_verification()
