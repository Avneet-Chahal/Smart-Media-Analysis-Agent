# Technical Architecture & System Specification

**Project:** Smart Media Analysis Agent for Educational Content  
**Course:** AI-103 Group Project (Chitkara University)  
**Core Technologies:** Multimodal AI • AI Agent • Retrieval-Augmented Generation (RAG) • Microsoft Azure AI

---

## 1. System Overview

The platform allows students to upload heterogeneous educational materials (PDF lecture notes, audio recordings, and video lectures) and interact with an AI Agent that answers questions with verifiable page numbers and video timestamps.

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│  - Multimodal Viewer (Video / Audio / PDF)                  │
│  - AI Agent Chat with Interactive Citations                 │
│  - Study Notes & Practice Quiz Suite                        │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API / HTTP 206
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend (Python)                 │
│  - Modular API Routers (Upload, Agent, Quiz, Media)         │
│  - Asynchronous Background Ingestion Pipeline               │
│  - SQLite Local Metadata Store                              │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
┌──────────────▼──────────────┐┌──────────────▼───────────────┐
│ Multimodal Processing Layer ││  Microsoft Azure AI Services │
│ - Document Processor (PDF)  ││  - Azure AI Search (Hybrid)  │
│ - Audio/Video Transcriber   ││  - Azure OpenAI / Foundry    │
│ - Media-Aware Chunker       ││  - text-embedding-3-small    │
└─────────────────────────────┘└──────────────────────────────┘
```

---

## 2. Core Architectural Pillars

### Pillar 1: Multimodal AI
- Handles diverse input formats (PDF, DOCX, TXT, MP3, WAV, MP4, WEBM).
- Extracts structural elements and page numbers from PDFs.
- Segments audio/video into timestamped speech intervals (`timestamp_start`, `timestamp_end`).

### Pillar 2: Retrieval-Augmented Generation (RAG)
- Partitions text into semantic chunks with embedded metadata.
- Generates 1536-dimensional embeddings using `text-embedding-3-small`.
- Queries the Azure AI Search hybrid index (BM25 keyword + HNSW vector search).
- Injects retrieved chunks into the prompt context for factual grounding.

### Pillar 3: AI Agent Orchestration (Microsoft Foundry)
- Operates via structured tool calling (`search_educational_content`, `generate_quiz_mcqs`, `get_content_summary`).
- Enforces strict grounding guardrails against hallucination.
- Emits structured citations enabling the frontend to jump directly to exact video frames.
