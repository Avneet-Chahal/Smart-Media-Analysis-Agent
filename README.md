# Smart Media Analysis Agent for Educational Content
> **AI-103 Group Project | Chitkara University**  
> An AI-powered multimodal educational intelligence platform designed for university students to upload lecture notes, PDFs, audio recordings, and videos, perform grounded RAG analysis with Microsoft Azure AI Services, and interact with a pedagogical AI agent.

---

## 🎯 Project Overview & Core Problem

Students receive learning materials in fragmented, heterogeneous formats: multi-page lecture PDFs, audio recordings, and lengthy video lectures. Finding specific explanations, summarizing complex topics, and preparing for exams is time-consuming.

**The Solution:**
The **Smart Media Analysis Agent** ingests multimodal educational files, extracts structured text and segment timestamps, indexes content into a hybrid vector search engine (Azure AI Search), and connects with an intelligent AI Agent (Microsoft Foundry / Azure OpenAI) capable of:
1. **Multimodal Analysis**: Extracting text, page numbers, and video/audio timestamp markers.
2. **Grounded RAG Q&A**: Answering student queries with strict grounding and verifiable citations.
3. **Interactive Media Seeking**: Clicking citations in chat or notes immediately jumps the video/audio player to the exact second.
4. **Pedagogical Summaries**: Generating executive overviews, key concept badges, and study checklists.
5. **Interactive MCQ Quizzing**: Generating curriculum-aligned practice quizzes with immediate feedback and explanation reveals.

---

## 👥 5-Member Team Workload & Explainability

Each team member has a distinct, explainable role in the architecture:

| Member | Focus Area | Key Contributions |
| :--- | :--- | :--- |
| **Member 1** | **AI Agent & Orchestration** | Implemented agent tool calling (`search_educational_content`, `generate_quiz_mcqs`, `get_content_summary`), system grounding guardrails, citation builder, and anti-hallucination policies in `backend/services/agent_service.py` and `prompts.py`. |
| **Member 2** | **Multimodal & Media Processing** | Built multimodal extraction for PDFs (`PyMuPDF`), audio and video segmentation with start/end timestamps, and intelligent media chunking in `backend/services/media_processor.py`. |
| **Member 3** | **RAG & Azure AI Search** | Architected Azure AI Search vector index, embedding generation (`text-embedding-3-small`), hybrid retrieval (BM25 + Vector Search), and similarity ranking in `backend/services/rag_service.py`. |
| **Member 4** | **Backend API & Integration** | Designed RESTful API endpoints, SQLite persistence ORM, asynchronous background ingestion tasks, HTTP byte-range media streaming, and health checks in `backend/routers/` and `database.py`. |
| **Member 5** | **Frontend UI / UX** | Developed the modern React application, glassmorphism design system, synchronized video player with timestamp seek controls, interactive citation explorer, and gamified MCQ study suite in `frontend/src/`. |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Frontend (React + Vite + Modern CSS)           │
│  - Multimodal Viewer (Video / Audio / PDF)                  │
│  - AI Agent Chat with Clickable Citations                   │
│  - Study Notes & Interactive MCQ Quizzer                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / REST API
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend (Python)                 │
│  - Asynchronous Ingestion & Storage Manager                 │
│  - SQLite Database (Documents, Chunks, Messages, Quizzes)   │
│  - HTTP 206 Partial-Content Media Streaming                 │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
┌──────────────▼──────────────┐┌──────────────▼───────────────┐
│ Multimodal Media Processing ││  Microsoft Azure AI Services │
│ - PDF Page Extractor        ││  - Azure AI Search (Hybrid)  │
│ - Audio/Video Transcriber   ││  - Azure OpenAI / Foundry    │
│ - Timestamped Chunker       ││  - text-embedding-3-small    │
└─────────────────────────────┘└──────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+** & `npm`

### 1. Backend Setup
```bash
# In the project root:
pip install -r requirements.txt

# (Optional) Configure Azure Credentials in .env:
# Copy .env.example to .env and fill in your Azure OpenAI and Azure Search keys.
# If left blank, the platform automatically runs in high-fidelity local mode!

# Start FastAPI server:
python -m uvicorn backend.main:app --reload --port 8000
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Open your browser at `http://localhost:5173`

---

## 🧪 Testing & Quantitative Evaluation

The test suite contains **53 automated tests** covering unit logic, API endpoints, multimodal processors, hybrid search indexing, agent tool routing, and anti-hallucination verification.

```bash
# Run all 53 automated tests:
pytest -v

# Run the 15-case strategic evaluation and accuracy benchmark:
pytest -v -s tests/test_strategy_suite.py

# Run the end-to-end integration workflow test:
pytest -v -s tests/test_e2e.py
```

### Measured Benchmark Accuracy Results

| Metric | Target | Measured Result | Status |
| :--- | :---: | :---: | :---: |
| **Top-1 Retrieval Hit Rate** | $\ge 85\%$ | **`100.0%` (9/9)** | **Met** |
| **Top-3 Retrieval Hit Rate** | $\ge 95\%$ | **`100.0%` (9/9)** | **Met** |
| **Mean Reciprocal Rank (MRR)** | $\ge 0.85$ | **`1.000`** | **Met** |
| **Anti-Hallucination Rejection Rate** | $100\%$ | **`100.0%` (3/3)** | **Met** |
| **Invalid File & Binary Header Rejection** | $100\%$ | **`100.0%` (4/4)** | **Met** |
| **Automated Test Suite Success** | $100\%$ | **`53 / 53 Passed (100%)`** | **Met** |

---

## 🤖 AI Services & Model Specifications

| Service / Component | Provider / Tool | Model / Technology | Primary Purpose |
| :--- | :--- | :--- | :--- |
| **Agent Reasoning & Chat** | Azure OpenAI / Microsoft Foundry | `gpt-4o-mini` (Temp: 0.2) | Grounded educational reasoning, tool routing, structured response synthesis. |
| **Dense Vector Embeddings** | Azure OpenAI | `text-embedding-3-small` (1536 dims) | High-accuracy semantic chunk representation. |
| **Hybrid Search & Vector Index** | Azure AI Search | HNSW Index + BM25 Lexical | Fast hybrid retrieval with strict relevance scoring. |
| **PDF Extraction** | PyMuPDF (`pymupdf`) | Binary Parser | Multi-page text extraction and section header identification. |
| **Speech & Audio Processing** | Azure AI Speech & Local Audio Parser | Multi-channel Speech SDK | Timestamped lecture transcription and chapter segmentation. |

---

## 📡 API Reference

All endpoints are documented interactively via OpenAPI / Swagger UI at `/docs`. Both root aliases and `/api/` paths are supported.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/upload` or `/api/upload` | Upload PDF, audio, or video files for synchronous validation and async indexing. |
| `GET` | `/api/documents` | List all uploaded educational materials with indexing status. |
| `GET` | `/api/documents/{id}` | Get document analysis metadata, duration, page count, and summary. |
| `GET` | `/api/documents/{id}/chunks`| Retrieve all timestamped/page-indexed semantic chunks. |
| `DELETE`| `/api/documents/{id}` | Cascade delete document, physical file, database records, and search index. |
| `POST` | `/chat` or `/api/agent/chat` | Query the grounded AI Agent with citations, tool tracking, and anti-hallucination. |
| `POST` | `/summary` or `/api/agent/summary` | Generate executive overview, key concepts, and exam review action items. |
| `POST` | `/generate-mcqs` or `/api/generate-mcqs`| Generate grounded multiple choice practice questions with answer explanations. |
| `GET` | `/api/media/{id}/stream` | Stream video/audio supporting HTTP 206 partial-content range seek. |
| `GET` | `/health` or `/api/health` | System and Azure connectivity status check. |

---

## 🛡️ Responsible AI & Security

A detailed governance document is maintained in [`docs/responsible-ai.md`](docs/responsible-ai.md).

- **No Hardcoded Secrets**: Loaded exclusively via `.env` through Pydantic Settings.
- **Git Protection**: `.env` and uploaded files in `storage/uploads/` are ignored in `.gitignore`.
- **Anti-Hallucination**: Queries with zero document overlap return `is_grounded: false` and a clear refusal.
- **Data Privacy**: Complete cascading deletion (`DELETE /api/documents/{id}`) removes physical files, DB entries, and vector indexes.
- **AI Transparency**: Persistent UI disclaimer informing students to verify critical exam concepts with original course materials.

---

## ⚠️ Known Limitations

1. **Scanned Images without OCR**: Low-resolution handwritten notes or image-only PDFs without an embedded text layer require Azure Document Intelligence OCR.
2. **Offline Fallback Scope**: When running in offline mode (without Azure OpenAI API keys), the agent uses local hybrid keyword-vector matching and deterministic rule-based summarization.
3. **Audio Transcription Dependencies**: Full audio transcription in local mode requires FFmpeg/Whisper or Azure Speech credentials.

---

## 🔮 Future Improvements

1. **Interactive Mind Maps**: Generating interactive concept node graphs from multi-lecture relationships.
2. **Flashcard Export**: One-click export of generated MCQs and key concepts to Anki / Quizlet.
3. **Multi-Document Comparative Search**: Querying across multiple courses or entire semester archives simultaneously.
4. **Voice Agent Interface**: Direct voice Q&A enabling students to listen to explanations while commuting.

---

## 📚 Third-Party Acknowledgements

- **FastAPI** by Tiangolo for the asynchronous REST API framework.
- **PyMuPDF** (`fitz`) for PDF parsing.
- **Azure AI Search & Azure OpenAI SDK** by Microsoft for vector indexing and LLM tool calling.
- **React & Vite** for the frontend UI.
- **Lucide React** for UI icons.

