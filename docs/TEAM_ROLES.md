# 5-Member Team Roles & Presentation Guide

**Project:** Smart Media Analysis Agent for Educational Content  
**Course:** AI-103 Group Project (Chitkara University)

---

## 👥 Role Breakdown

### Member 1: AI Agent & Orchestration
- **Module:** `backend/agent/` (`agent_service.py`, `prompts.py`)
- **Key Responsibilities:**
  - Implemented tool calling engine: `search_educational_content`, `generate_quiz_mcqs`, `get_content_summary`.
  - Built system prompt guardrails to guarantee factual grounding and prevent hallucination.
  - Implemented citation synthesis linking answers to page numbers and video timestamps.

### Member 2: Multimodal & Media Processing
- **Module:** `backend/processing/` (`document_processor.py`, `media_processor.py`, `chunker.py`)
- **Key Responsibilities:**
  - Built PDF text and page extraction using `PyMuPDF`.
  - Implemented speech segmentation for video/audio lectures with start/end time markers.
  - Designed media-aware semantic chunking with overlap.

### Member 3: RAG & Azure AI Search
- **Module:** `backend/search/` and `backend/rag/` (`azure_search.py`, `rag_engine.py`)
- **Key Responsibilities:**
  - Designed Azure AI Search index schema with vector profiles (HNSW algorithm).
  - Built embedding pipeline using Azure OpenAI `text-embedding-3-small`.
  - Implemented hybrid search combining keyword BM25 + dense vector similarity.

### Member 4: Backend API & Integration
- **Module:** `backend/routes/`, `backend/config/`, `backend/database/`
- **Key Responsibilities:**
  - Developed FastAPI application architecture with async background tasks.
  - Built SQLite database schema with SQLAlchemy ORM.
  - Implemented HTTP 206 Partial Content byte-range media streaming for video player seeking.

### Member 5: Frontend UI / UX
- **Module:** `frontend/src/` (`components/`, `pages/`, `styles/`, `services/`)
- **Key Responsibilities:**
  - Built responsive React application with modern glassmorphism design system.
  - Created synchronized video player with instant timestamp seeking.
  - Developed conversational chat interface with clickable citations and interactive practice quiz runner.
