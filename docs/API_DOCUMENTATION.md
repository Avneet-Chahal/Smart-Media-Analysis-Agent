# Smart Media Analysis Agent - REST API Documentation

**Project**: Smart Media Analysis Agent for Educational Content  
**Course**: AI-103 Group Project (Chitkara University)  
**Base Server URL**: `http://localhost:8000` (or `http://localhost:8000/api`)  
**Interactive Swagger UI**: `http://localhost:8000/docs`  
**OpenAPI ReDoc**: `http://localhost:8000/redoc`  

---

## 🚀 Core REST Endpoints

### 1. `POST /upload` (or `POST /api/upload`)
Uploads educational media (PDF slides, lecture recordings, podcasts, or video tutorials), performs input validation, extracts text/speech, indexes chunks into Azure AI Search, and prepares RAG vectors in the background.

- **Request**: `multipart/form-data` with form field `file`
- **Response Status**: `202 Accepted`
- **Response Body**:
```json
{
  "id": "7db0fdc8-f0e6-45fd-80de-ae5bfbaaa4d7",
  "filename": "Lecture_05_Deep_Learning.pdf",
  "media_type": "pdf",
  "file_size": 245890,
  "status": "PROCESSING",
  "duration_seconds": null,
  "page_count": null,
  "summary_text": null,
  "key_concepts": null,
  "action_items": null,
  "created_at": "2026-09-16T13:30:00Z",
  "updated_at": null
}
```

---

### 2. `POST /analyze` (or `POST /api/agent/analyze`)
Triggers end-to-end multimodal analysis of an uploaded document and returns a complete study packet including summary, core concepts, action items, and stream URL.

- **Request Body**:
```json
{
  "document_id": "7db0fdc8-f0e6-45fd-80de-ae5bfbaaa4d7"
}
```
- **Response Body**:
```json
{
  "document_id": "7db0fdc8-f0e6-45fd-80de-ae5bfbaaa4d7",
  "filename": "Lecture_05_Deep_Learning.pdf",
  "media_type": "pdf",
  "status": "READY",
  "page_count": 3,
  "duration_seconds": null,
  "chunks_count": 6,
  "title": "Study Notes: Deep Learning Architectures",
  "overview": "This learning resource covers fundamental principles of Convolutional Neural Networks and Optimization...",
  "key_concepts": [
    {
      "concept": "Convolution Operation",
      "description": "Applies learnable kernels across input tensors to detect spatial hierarchies...",
      "page": 1,
      "timestamp": null
    }
  ],
  "action_items": [
    "Review SGD learning rate equations in Lecture 5",
    "Complete the interactive self-assessment quiz"
  ],
  "file_url": "/api/media/7db0fdc8-f0e6-45fd-80de-ae5bfbaaa4d7/stream"
}
```

---

### 3. `POST /chat` (or `POST /api/agent/chat`)
Engages with the grounded AI educational agent using hybrid RAG. Returns student-tailored explanations anchored in source citations with page numbers or playback timestamps.

- **Request Body**:
```json
{
  "document_id": "7db0fdc8-f0e6-45fd-80de-ae5bfbaaa4d7",
  "query": "How does Dropout prevent overfitting?",
  "chat_history": [
    {"role": "user", "content": "Hello professor"},
    {"role": "assistant", "content": "Hello! How can I assist your study today?"}
  ]
}
```
- **Response Body**:
```json
{
  "response": "Based on **Lecture_05_Deep_Learning.pdf** on **Page 3**:\n\nDropout randomly deactivates neurons during training with probability p...",
  "citations": [
    {
      "chunk_id": "doc_pdf_101_2",
      "media_type": "pdf",
      "page_number": 3,
      "timestamp_start": null,
      "timestamp_end": null,
      "snippet": "Dropout regularization randomly deactivates a subset of neurons with probability p...",
      "source_filename": "Lecture_05_Deep_Learning.pdf"
    }
  ],
  "tools_used": ["search_educational_content"],
  "is_grounded": true,
  "grounding_status": "GROUNDED"
}
```

---

### 4. `POST /summary` (or `POST /api/agent/summary`)
Generates or retrieves structured executive notes, core formulas, and actionable review items.

- **Request Body**:
```json
{
  "document_id": "7db0fdc8-f0e6-45fd-80de-ae5bfbaaa4d7"
}
```
- **Response Body**:
```json
{
  "document_id": "7db0fdc8-f0e6-45fd-80de-ae5bfbaaa4d7",
  "title": "Study Notes: Lecture 05",
  "overview": "Comprehensive overview of deep architectures...",
  "key_concepts": [
    {"concept": "CNNs", "description": "Spatial feature extractors...", "page": 1, "timestamp": null}
  ],
  "action_items": [
    "Review fundamental equations and definitions in Lecture_05",
    "Complete the interactive self-assessment quiz"
  ]
}
```

---

### 5. `POST /generate-mcqs` (or `POST /api/agent/quiz`)
Generates pedagogical Multiple Choice Questions (MCQs) strictly grounded in the document content.

- **Request Body**:
```json
{
  "document_id": "7db0fdc8-f0e6-45fd-80de-ae5bfbaaa4d7",
  "num_questions": 5,
  "difficulty": "medium"
}
```
- **Response Body**:
```json
{
  "quiz_id": "quiz_8f93da12",
  "document_id": "7db0fdc8-f0e6-45fd-80de-ae5bfbaaa4d7",
  "title": "Quiz: Lecture_05_Deep_Learning.pdf",
  "difficulty": "medium",
  "questions": [
    {
      "id": 1,
      "question": "What is the primary role of Dropout regularization during training?",
      "options": [
        "A. Randomly deactivates neurons to prevent co-adaptation and overfitting",
        "B. Multiplies learning rate by a factor of 100",
        "C. Inverts convolutional kernel weights",
        "D. Doubles network parameters"
      ],
      "correct_answer_index": 0,
      "explanation": "Grounded in Lecture_05 Page 3: Dropout prevents models from memorizing noise.",
      "citation": {
        "page": 3,
        "timestamp": null,
        "snippet": "Dropout randomly deactivates..."
      }
    }
  ]
}
```

---

### 6. `GET /health` (or `GET /api/health`)
Checks backend operational status, database connectivity, and Azure AI readiness.

- **Response Body**:
```json
{
  "status": "HEALTHY",
  "azure_openai_configured": true,
  "azure_search_configured": true,
  "database_connected": true,
  "environment": "development",
  "uptime_message": "Smart Media Analysis Agent Platform is operational."
}
```

---

## 🛡️ Error Handling & Status Codes

All errors return a standard structured JSON error envelope:
```json
{
  "status": "error",
  "code": 400,
  "message": "File 'corrupt.pdf' is not a valid PDF file (missing %PDF header).",
  "details": null
}
```

| HTTP Code | Condition |
|:---|:---|
| `200 OK` | Request succeeded |
| `202 Accepted` | Media uploaded; background processing started |
| `400 Bad Request` | Content validation error, empty query, or corrupted container |
| `404 Not Found` | Requested document or resource ID does not exist |
| `422 Unprocessable`| Pydantic schema validation error |
| `500 Server Error` | Unhandled backend exception |
