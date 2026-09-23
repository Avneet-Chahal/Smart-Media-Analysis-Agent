# Responsible AI & Governance Document

**Project**: Smart Media Analysis Agent for Educational Content  
**Course**: AI-103 Group Project, Chitkara University  
**Scope**: Educational AI Assistant & Multimodal Hybrid RAG MVP  

---

## 1. Executive Summary & Purpose

The **Smart Media Analysis Agent** is an educational assistive tool designed to help university students and instructors ingest, index, and query multimodal learning materials (lecture PDFs, audio recordings, and video sessions). 

Because generative AI models and retrieval-augmented systems can produce confident inaccuracies, expose confidential educational content, or mislead students during exam preparation, this document establishes the **Responsible AI (RAI) framework**, operational safeguards, risk mitigations, system limitations, and boundaries of trust for this student MVP.

---

## 2. Responsible AI Core Pillars & Implemented Measures

```
                      ┌─────────────────────────────────────────┐
                      │    RESPONSIBLE AI GOVERNANCE SYSTEM     │
                      └────────────────────┬────────────────────┘
                                           │
         ┌──────────────────┬──────────────┴─────┬──────────────────┐
         │                  │                    │                  │
┌────────▼─────────┐ ┌──────▼──────────┐ ┌───────▼──────────┐ ┌─────▼────────────┐
│ 1. Data Privacy  │ │ 2. Factual      │ │ 3. Transparency  │ │ 4. Human-in-the- │
│    & Security    │ │    Grounding    │ │    & Disclosure  │ │    Loop Oversight│
│ - Sanitized Paths│ │ - Hybrid RAG    │ │ - AI Badges      │ │ - Clickable Page │
│ - Secret Guarding│ │ - Strict Score  │ │ - Disclaimer     │ │   Citations      │
│ - Cascade Delete │ │   Thresholds    │ │ - Tool Tracing   │ │ - Timestamp Seek │
└──────────────────┘ └─────────────────┘ └──────────────────┘ └──────────────────┘
```

### Pillar 1: Privacy & Data Protection
* **Data Isolation**: Uploaded files and extracted text are stored strictly in local workspace storage (`storage/uploads/` and `storage/app.db`).
* **No Third-Party Model Training**: When Azure OpenAI is used, enterprise Azure tenant agreements ensure customer data is not retained for model retraining.
* **Access Containment**: Files are served through controlled endpoints (`/api/media/{id}/stream`) with strict path containment checks preventing directory traversal.

### Pillar 2: Application & Infrastructure Security
* **Input Sanitization**: File names are sanitized with `Path(filename).name` stripping any relative path traversal characters (`../`, `..\\`).
* **Binary Signature Verification**: Uploads are inspected at the byte level before acceptance:
  - PDFs require valid `%PDF-` header signatures.
  - Audio/Video require container format signatures (`RIFF`, `ftyp`, `EBML`).
  - Executable (`.exe`, `.sh`, `.bat`) and unapproved file extensions are rejected immediately (`HTTP 400`).
* **Upload Caps**: Strict file size limit of 50 MB prevents server disk exhaustion or denial-of-service (DoS) attempts.

### Pillar 3: Secret & API Key Protection
* **Zero Hardcoding**: All secrets (`AZURE_OPENAI_API_KEY`, `AZURE_SEARCH_API_KEY`) are managed via environment variables and `.env` files.
* **Repository Exclusion**: `.env` is listed in `.gitignore`.
* **Zero Secret Leakage**: The `/api/health` and error handlers only expose boolean readiness flags (`azure_openai_configured: bool`), never exposing raw credentials or connection strings in logs or API payloads.

### Pillar 4: Hallucination Prevention & Factual Grounding
* **Strict Relevance Thresholding**: The Hybrid RAG ranker requires a minimum relevance score ($\ge 0.35$) and multi-keyword intersection before passing chunks to the AI agent.
* **Zero False Grounding on Out-of-Scope Queries**: If a query is unrelated to the document (e.g., historical trivia, unrelated science), the system outputs `is_grounded: False` with status `NOT_FOUND` and returns an honest refusal rather than fabricating an answer.
* **Low Temperature**: Generation temperature is pinned to `0.2` to prioritize deterministic factual extraction over creative prose.

### Pillar 5: Verifiable Grounded Answers & Citations
* **Granular Attribution**: Every generated answer includes structured citation objects containing:
  - Source document filename (`source_filename`)
  - Exact page number (`page_number`)
  - Media timestamp range (`timestamp_start` to `timestamp_end`)
  - Direct contextual excerpt snippet (`snippet`)
* **Interactive Verification**: Frontend users can click citation chips to jump directly to the relevant PDF page or seek the exact timestamp in the media player.

### Pillar 6: Transparency & AI Disclosure
* **Explicit AI Disclosures**: The UI prominently displays badges indicating AI assistance, showing whether responses are powered by the Cloud Azure Foundry or the Local Hybrid Engine.
* **Persistent User Notice**: The chat interface includes a clear disclaimer: *"AI-generated educational assistant. Responses are grounded in uploaded course notes; verify critical exam concepts with original course materials."*
* **Tool Tracing**: API responses and UI chips display `tools_used` (`search_educational_content`, `generate_summary`, `generate_mcqs`, `find_video_timestamps`), clarifying how the system arrived at the result.

### Pillar 7: Graceful Unsupported Information Handling
* **Honest Refusal Paradigm**: When information is absent, the agent refuses transparently: *"I cannot find specific information regarding this in the uploaded educational materials. Please make sure the relevant lecture notes, PDF, or video have been uploaded and processed."*
* **Non-Hallucinatory MCQs**: Practice quiz questions are only synthesized from chunks containing clear conceptual definitions.

### Pillar 8: Robust Error Handling & Fault Isolation
* **Standardized JSON Error Schemas**: All exceptions return structured responses (`{"status": "error", "code": 4xx/5xx, "message": "...", "details": ...}`).
* **Cloud Outage Fallback**: If Azure OpenAI or Azure AI Search is offline or throttled, the agent automatically falls back to local hybrid ranking and deterministic summarizers without crashing.
* **Sanitized Client Errors**: Internal stack traces and database paths are hidden in production responses.

### Pillar 9: Human-in-the-Loop Oversight
* **Student Verification**: Students are encouraged to inspect raw source pages and playback clips rather than blindly accepting summaries.
* **Instructor Review**: Instructors have full oversight to delete corrupted uploads, inspect extracted chunks, and regenerate study notes.

### Pillar 10: File Retention & Data Deletion
* **Complete Cascading Deletion**: Executing `DELETE /api/documents/{id}` immediately deletes:
  - The physical media file from `storage/uploads/`
  - All database records (`Document`, `DocumentChunk`, `ChatMessage`, `GeneratedQuiz`)
  - All cached vector index entries in the search manager
* **No Zombie Files**: Deleting a document leaves zero orphaned chunks or leaked context.

---

## 3. Risks & Mitigations Matrix

| Risk Category | Potential Impact | Severity | Implemented Mitigation |
| :--- | :--- | :---: | :--- |
| **Hallucination on Uncovered Topics** | Student memorizes incorrect formula or non-existent concept. | **High** | Keyword overlap requirement ($\ge 2$ keywords) + similarity threshold ($\ge 0.35$) triggers honest refusal (`is_grounded: False`). |
| **Path Traversal / Malicious Upload** | Attacker overwrites server files or executes unauthorized scripts. | **High** | Strict `Path(filename).name` extraction, extension whitelist, and `%PDF-` / media magic header validation. |
| **Exposing API Keys in Logs/Responses** | Cloud budget exhaustion or compromised Azure subscription. | **High** | Environment-based settings via Pydantic; health endpoints emit only boolean status flags. |
| **Student Over-reliance on AI Notes** | Missing critical nuance or formula steps during university exams. | **Medium** | Interactive page citations and video timestamp seek buttons enable verification against source materials. |
| **Orphaned Student Data** | Old lecture notes persist indefinitely after student deletion. | **Medium** | Synchronous cascade deletion of files on disk, SQLite database rows, and in-memory search indexes. |
| **Cloud Service Outage / Rate Limit** | Application completely unusable during offline study or demo. | **Medium** | Built-in local hybrid retrieval and rule-based summarizers execute when Azure credentials are not set. |

---

## 4. System Limitations (What the AI MVP Is and Is Not)

### What the AI SHOULD Be Trusted To Do:
1. **Locate Key Topics in Uploaded Documents**: Accurately find which page or video timestamp discusses a lecture topic.
2. **Synthesize Extracted Notes**: Produce concise study guides directly derived from the supplied text.
3. **Draft Self-Assessment MCQs**: Generate practice questions based on definitions present in the lecture.
4. **Explain Grounded Concepts**: Rephrase dense lecture paragraphs into step-by-step educational explanations with citations.

### What the AI SHOULD NOT Be Trusted To Do:
1. **Grading & Official Academic Evaluation**: The agent is a study aid, not an automated grading authority.
2. **Substituting Primary Course Textbooks**: The AI does not have broader world knowledge beyond the provided document.
3. **Medical, Legal, or Safety Decisions**: The system is intended strictly for university academic coursework review.
4. **Deciphering Handwritten / Poorly Scanned PDFs**: Low-resolution or hand-drawn sketches without OCR text layers may yield incomplete extraction.

---

## 5. Ongoing Monitoring & Maintenance Checklist

- [x] Run `pytest` automated test suite before any presentation or release.
- [x] Verify `.env` is never committed to Git version control.
- [x] Test out-of-scope queries periodically to confirm anti-hallucination thresholds remain intact.
- [x] Purge temporary files in `storage/uploads/` when cleaning up demonstration datasets.
- [x] Ensure all frontend users see the Responsible AI transparency disclaimers.
