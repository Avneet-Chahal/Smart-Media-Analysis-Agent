# 🤖 Smart Media Analysis Agent

> **AI-Powered Multimodal Educational Content Intelligence Platform**

Smart Media Analysis Agent is an AI-powered educational platform that helps students **understand, search, summarize, and practice** content from PDFs, audio recordings, and videos.

The system combines **multimodal content processing, speech-to-text, Retrieval-Augmented Generation (RAG), Azure AI Search, and Microsoft Foundry** to provide grounded and context-aware responses from uploaded educational material.

---

## 👥 Team Members

| Name | Roll Number |
|---|---:|
| **Avneet Kaur** | 2410998521 |
| **Jasnoor Kaur** | 2410998539 |
| **Aaryan Verma** | 2410998506 |
| **Mitansh Kaushal** | 2410998551 |
| **Gunit** | 2410998526 |

---

## 📑 Table of Contents

1. [Problem Statement](#-1-problem-statement)
2. [Proposed Solution](#-2-proposed-solution)
3. [Objectives](#-3-objectives)
4. [Key Features](#-4-key-features)
5. [System Architecture](#️-5-system-architecture)
6. [Data Flow](#-6-data-flow)
7. [Technology Stack](#️-7-technology-stack)
8. [AI Services and Their Roles](#️-8-ai-services-and-their-roles)
9. [AI-103 Concepts Applied](#-9-ai-103-concepts-applied)
10. [Project Structure](#-10-project-structure)
11. [Installation and Setup](#️-11-installation-and-setup)
12. [Backend Setup](#-12-backend-setup)
13. [Frontend Setup](#️-13-frontend-setup)
14. [Environment Configuration](#-14-environment-configuration)
15. [Running the Backend](#-15-running-the-backend)
16. [Running the Frontend](#-16-running-the-frontend)
17. [Running the Complete Application](#-17-running-the-complete-application)
18. [Testing](#-18-testing)
19. [Testing Results](#-19-testing-results)
20. [Example Workflow](#-20-example-workflow)
21. [Responsible AI](#-21-responsible-ai)
22. [Known Limitations](#️-22-known-limitations)
23. [Future Improvements](#-23-future-improvements)
24. [Screenshots](#-24-screenshots)
25. [Demo Video](#-25-demo-video)
26. [GitHub Repository](#-26-github-repository)
27. [Third-Party Acknowledgements](#-27-third-party-acknowledgements)
28. [Project Status](#-28-project-status)
29. [Project Deliverables](#-29-project-deliverables)
30. [Conclusion](#-30-conclusion)

---

# 🎯 1. Problem Statement

Students learn from different types of educational resources such as lecture notes, PDFs, audio recordings, and videos.

Finding specific information inside these resources, understanding long lectures, creating study notes, and preparing practice questions manually can be time-consuming.

The **Smart Media Analysis Agent** provides a unified AI-powered workspace where students can upload educational content and interact with it through:

- 💬 AI-powered questions and answers
- 🔎 Content search
- 📝 Study notes
- 🧠 Practice quizzes
- 🎧 Audio and video transcripts
- ⏱️ Timestamp-based navigation
- 💭 Conversation history
- 📚 Source-grounded responses

---

# 💡 2. Proposed Solution

The Smart Media Analysis Agent processes educational content from multiple media formats and converts it into searchable and understandable information.

The system extracts text from documents, transcribes audio and video using speech recognition, creates searchable content chunks, retrieves relevant information, and sends the retrieved context to an AI agent for generating grounded responses.

### 🔄 High-Level Workflow

```text
                    ┌───────────────┐
                    │    Student    │
                    └───────┬───────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Upload Learning     │
                 │ Material            │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Content Type        │
                 │ Detection           │
                 └──────────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌───────────┐ ┌───────────┐ ┌───────────┐
        │    PDF    │ │   Audio   │ │   Video   │
        │   Text    │ │  Speech   │ │ FFmpeg +  │
        │Extraction │ │Transcribe │ │  Speech   │
        └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Content Chunking    │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Searchable          │
                 │ Representation      │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Azure AI Search     │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Relevant Context    │
                 │ Retrieval           │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Microsoft Foundry   │
                 │ AI Agent            │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Grounded AI         │
                 │ Response            │
                 └──────────┬──────────┘
                            ▼
             ┌─────────────────────────────┐
             │ Chat / Notes / Quiz /       │
             │ Citations                   │
             └─────────────────────────────┘
```

---

# 🎯 3. Objectives

The main objectives of the project are:

- Build a multimodal educational AI assistant.
- Allow students to upload PDF, audio, and video learning material.
- Convert audio and video into timestamped transcripts.
- Make educational content searchable.
- Implement Retrieval-Augmented Generation (RAG).
- Provide grounded AI responses based on uploaded content.
- Generate study notes from educational material.
- Generate practice quizzes automatically.
- Support conversation-aware follow-up questions.
- Provide source information for generated responses.
- Demonstrate AI-103 concepts through a working prototype.

---

# ✨ 4. Key Features

## 4.1 📚 Multimodal Content Upload

The platform supports:

- 📄 PDF documents
- 🎧 Audio files
- 🎥 Video files

---

## 4.2 📄 PDF Analysis

```text
Upload PDF
    ↓
Text Extraction
    ↓
Content Cleaning
    ↓
Chunking
    ↓
Searchable Content
    ↓
AI Analysis
```

---

## 4.3 🎧 Audio Analysis

```text
Upload Audio
    ↓
Azure Speech Transcription
    ↓
Timestamped Transcript
    ↓
Content Chunking
    ↓
Searchable Content
    ↓
AI Analysis
```

---

## 4.4 🎥 Video Analysis

```text
Upload Video
    ↓
FFmpeg Audio Extraction
    ↓
Azure Speech Transcription
    ↓
Timestamped Transcript
    ↓
Content Chunking
    ↓
Searchable Content
    ↓
AI Analysis
```

The video transcript contains timestamps that allow users to navigate directly to the corresponding position in the video.

---

## 4.5 🤖 AI Agent Chat

Students can ask questions about their uploaded educational material.

**Example**

> **User:** What is polymorphism?
>
> **AI Agent:** Provides a grounded explanation based on the uploaded educational material.

The agent also supports follow-up questions using conversation history.

**Follow-up Example**

> **User:** What is the first concept explained in the video?
>
> **Agent:** Explains the first concept.
>
> **User:** Can you explain that concept in more detail?
>
> **Agent:** Understands the previous context and provides a relevant explanation.

---

## 4.6 🔎 Retrieval-Augmented Generation

The system uses RAG to retrieve relevant educational content before generating an answer.

```text
User Question
      ↓
Query Processing
      ↓
Azure AI Search
      ↓
Relevant Content Retrieval
      ↓
Context Construction
      ↓
Microsoft Foundry Agent
      ↓
Grounded Response
```

This helps the system answer questions using the uploaded learning material instead of relying only on general model knowledge.

---

## 4.7 📝 Study Notes

The system can generate structured study notes from uploaded educational content.

Study notes can include:

- Important concepts
- Key explanations
- Main points
- Important definitions
- Relevant timestamps
- Source information

---

## 4.8 🧠 Practice Quiz

The system can generate practice questions from uploaded educational material.

The quiz module supports:

- Multiple-choice questions
- Different difficulty levels
- Answer options
- Correct answers
- Educational context

---

## 4.9 💭 Conversation History

The application stores previous conversations so students can review their interactions with the AI agent.

```text
User Question
      ↓
AI Response
      ↓
Conversation Stored
      ↓
History Panel
      ↓
Review Previous Discussion
```

---

## 4.10 📚 Source Grounding

The system keeps AI responses connected to retrieved educational content.

Where available, responses can provide:

- Source filename
- Page number
- Timestamp
- Relevant content snippet

---

# 🏗️ 5. System Architecture

```text
                         ┌──────────────────┐
                         │     Student      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ React Frontend   │
                         │    Vite + JS     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ FastAPI Backend  │
                         │    REST APIs     │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
       │    Media     │   │ RAG Pipeline │   │    Agent     │
       │  Processing  │   │              │   │   Service    │
       └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
              │                  │                  │
              ▼                  ▼                  ▼
       ┌──────────────┐   ┌──────────────┐   ┌───────────────┐
       │ PDF / Audio  │   │ Azure AI     │   │ Microsoft     │
       │ / Video      │   │ Search       │   │ Foundry Agent │
       └──────┬───────┘   └──────┬───────┘   └──────┬────────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │   Grounded AI      │
                       │      Response      │
                       └────────────────────┘
```

---

# 🔄 6. Data Flow

```text
Student Upload
      ↓
Media Detection
      ↓
┌─────────────┬─────────────┬─────────────┐
▼             ▼             ▼
PDF           Audio         Video
Processing    Processing    Processing
▼             ▼             ▼
Text          Speech-to-    FFmpeg
Extraction    Text          Extraction
│             │             │
└─────────────┼─────────────┘
              ▼
      Content Chunking
              ↓
      Azure AI Search
              ↓
      Relevant Context
              ↓
       Foundry Agent
              ↓
        AI Response
```

---

# 🛠️ 7. Technology Stack

| Category | Technologies |
|---|---|
| **Frontend** | React.js, Vite, JavaScript, CSS, Axios |
| **Backend** | Python, FastAPI, REST APIs, Pydantic |
| **AI & Cloud** | Microsoft Foundry, Azure AI Search, Azure Speech, GPT Model |
| **Media Processing** | FFmpeg, PDF Processing, Speech-to-Text, Timestamp Extraction |
| **Database** | SQLite |
| **Development Tools** | Git, GitHub, VS Code / Antigravity, Postman |

---

# ☁️ 8. AI Services and Their Roles

| Service | Role |
|---|---|
| **Microsoft Foundry** | AI Agent and grounded response generation |
| **Azure AI Search** | Educational content retrieval |
| **Azure Speech** | Audio and video transcription |
| **GPT Model** | Natural language understanding and generation |
| **FFmpeg** | Video audio extraction |
| **RAG Pipeline** | Retrieves relevant context before generation |

---

# 🧠 9. AI-103 Concepts Applied

The project demonstrates several concepts covered in AI-103.

### ✨ Generative AI

Used to generate:

- Answers
- Study notes
- Quiz questions
- Educational explanations

### 🎥 Multimodal AI

The system works with:

- Documents
- Audio
- Video

### 🔎 Retrieval-Augmented Generation

Relevant educational content is retrieved before generating responses.

### 🧩 Embeddings and Search

Educational content is converted into searchable representations and retrieved based on user queries.

### 🤖 AI Agents

Microsoft Foundry is used to provide an agent-based interaction layer.

### 📝 Prompt Engineering

Structured prompts are used to control the agent's behavior and grounding requirements.

### 🎙️ Speech-to-Text

Azure Speech converts audio and video speech into text.

### 🔐 Responsible AI

The system focuses on grounded responses, source awareness, security, and human verification.

---

# 📁 10. Project Structure

```text
Smart-Media-Analysis-Agent/
│
├── backend/
│   ├── agent/
│   │   ├── agent_service.py
│   │   ├── prompts.py
│   │   └── tools.py
│   │
│   ├── config/
│   ├── database/
│   ├── models/
│   │
│   ├── processing/
│   │   ├── audio_processor.py
│   │   ├── document_processor.py
│   │   ├── multimodal_processor.py
│   │   └── video_processor.py
│   │
│   ├── rag/
│   ├── routes/
│   ├── search/
│   └── main.py
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── utils/
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   ├── TEAM_ROLES.md
│   └── responsible-ai.md
│
├── tests/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
└── test_foundry_connection.py
```

---

# ⚙️ 11. Installation and Setup

## Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Smart-Media-Analysis-Agent
```

---

# 🐍 12. Backend Setup

Create a Python virtual environment:

```bash
python -m venv backend/venv
```

Activate the environment on Windows:

```powershell
backend\venv\Scripts\Activate.ps1
```

Activate the environment on macOS / Linux:

```bash
source backend/venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

# ⚛️ 13. Frontend Setup

Move into the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

---

# 🔐 14. Environment Configuration

Create a `.env` file in the project root.

Use `.env.example` as the configuration template.

Example:

```env
ENVIRONMENT=development
PORT=8001
HOST=0.0.0.0

FOUNDRY_PROJECT_ENDPOINT=
FOUNDRY_AGENT_NAME=smart-media-agent

AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_SEARCH_INDEX_NAME=

AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=
```

---

# 🚀 15. Running the Backend

From the project root:

```bash
uvicorn backend.main:app --reload --port 8001
```

Backend will run at:

```text
http://127.0.0.1:8001
```

---

# 🌐 16. Running the Frontend

Open another terminal:

```bash
cd frontend
npm run dev
```

Frontend will run at:

```text
http://localhost:5173
```

---

# 🔗 17. Running the Complete Application

**Terminal 1 — Backend**

```text
FastAPI Backend
      ↓
http://127.0.0.1:8001
```

**Terminal 2 — Frontend**

```text
React + Vite Frontend
      ↓
http://localhost:5173
```

Open the frontend URL in the browser to access the application.

---

# 🧪 18. Testing

The prototype was tested across the major application workflows.

### 📄 PDF Testing

```text
Upload PDF
    ↓
PDF Processing
    ↓
Text Extraction
    ↓
Content Retrieval
    ↓
Ask AI Question
    ↓
Grounded Response
```

### 🎧 Audio Testing

```text
Upload Audio
    ↓
Azure Speech
    ↓
Speech Transcription
    ↓
Timestamped Transcript
    ↓
AI Analysis
```

### 🎥 Video Testing

```text
Upload Video
    ↓
FFmpeg Audio Extraction
    ↓
Azure Speech
    ↓
Timestamped Transcript
    ↓
Searchable Content
    ↓
AI Analysis
```

### 🤖 Agent Chat Testing

Tested:

- Direct questions
- Follow-up questions
- Context-aware conversations
- Document-grounded responses
- Source information

### 📝 Study Notes Testing

Tested generation of study notes from uploaded educational material.

### 🧠 Quiz Testing

Tested:

- Quiz generation
- Multiple-choice questions
- Difficulty selection
- Correct answer generation

### 💭 History Testing

Tested:

- Conversation storage
- History retrieval
- Previous conversation display

---

# 📊 19. Testing Results

| Feature | Status |
|---|---|
| 📄 PDF Upload | ✅ Working |
| 📄 PDF Content Analysis | ✅ Working |
| 🎧 Audio Upload | ✅ Working |
| 🎙️ Audio Transcription | ✅ Working |
| ⏱️ Audio Timestamps | ✅ Working |
| 🎥 Video Upload | ✅ Working |
| ⚙️ FFmpeg Processing | ✅ Working |
| 🎙️ Video Transcription | ✅ Working |
| ⏱️ Video Timestamps | ✅ Working |
| 🤖 AI Agent Chat | ✅ Working |
| 💬 Follow-up Questions | ✅ Working |
| 🔎 RAG Retrieval | ✅ Working |
| 📝 Study Notes | ✅ Working |
| 🧠 Quiz Generation | ✅ Working |
| 💭 Conversation History | ✅ Working |
| ☁️ Azure AI Search | ✅ Working |
| 🤖 Microsoft Foundry | ✅ Working |

---

# 🔄 20. Example Workflow

A typical student workflow looks like:

```text
Student Opens Application
          ↓
Uploads Lecture PDF / Audio / Video
          ↓
System Processes Content
          ↓
Content Becomes Searchable
          ↓
Student Asks Question
          ↓
Relevant Content Retrieved
          ↓
Foundry Agent Generates Response
          ↓
Student Receives Grounded Answer
          ↓
Student Generates Notes / Quiz
          ↓
Conversation Saved in History
```

---

# 🔐 21. Responsible AI

The project considers the following responsible AI principles.

### 🎯 Grounding

Responses are generated using retrieved educational content whenever available.

### 🔎 Transparency

The application provides source information for retrieved content where available.

### 🛡️ Reliability

The system is designed to reduce unsupported responses by using retrieval before generation.

### 👤 Human Oversight

AI-generated notes, explanations, and quizzes should be reviewed by students before being treated as authoritative study material.

### 🔒 Security

Secrets and credentials are stored in environment variables and excluded from version control.

### 🗂️ Privacy

Uploaded educational content is processed for the purpose of providing the requested learning functionality.

---

# ⚠️ 22. Known Limitations

- Speech transcription quality depends on audio quality.
- Background noise may affect transcription accuracy.
- Very large media files may require additional processing time.
- AI-generated notes and quizzes may require human verification.
- The current prototype is primarily designed for educational content.
- The current prototype is optimized for demonstration and proof-of-concept usage.

---

# 🚀 23. Future Improvements

Future versions of the Smart Media Analysis Agent can include:

- Support for more document formats
- Multilingual speech transcription
- Speaker identification
- Advanced video frame analysis
- Visual question answering
- Personalized learning recommendations
- Adaptive quizzes
- Learning progress tracking
- Cloud-based media storage
- User authentication and role-based access
- Scalable production deployment
- Advanced monitoring and analytics

---

# 📸 24. Screenshots

The project documentation can include screenshots of:

- 🏠 Landing Page
- 🔐 Sign In / Sign Up
- 📊 Dashboard
- 📤 Upload Learning Material
- 📄 PDF Analysis
- 🎧 Audio Transcription
- 🎥 Video Transcription
- 🤖 AI Agent Chat
- 📝 Study Notes
- 🧠 Practice Quiz
- 💭 Conversation History

Add project screenshots inside `docs/screenshots/`:

```text
docs/screenshots/
├── landing-page.png
├── dashboard.png
├── upload.png
├── pdf-analysis.png
├── audio-transcription.png
├── video-transcription.png
├── ai-chat.png
├── study-notes.png
├── practice-quiz.png
└── conversation-history.png
```

---

# 🎥 25. Demo Video

The project demonstration video covers:

| Duration | Topic |
|---|---|
| 30 sec | Project Introduction |
| 30 sec | Problem Statement |
| 1 min | AI Solution |
| 2 min | Technical Demonstration |
| 1 min | Impact and Future Improvements |

The video demonstrates the working prototype and its major AI capabilities.

---

# 🔗 26. GitHub Repository

The repository contains:

- Backend source code
- Frontend source code
- AI agent implementation
- RAG pipeline
- Media processing
- Tests
- Documentation
- Environment template

---

# 🙏 27. Third-Party Acknowledgements

This project uses the following technologies and services:

- Microsoft Foundry
- Azure AI Search
- Azure Speech
- GPT model services
- Python
- FastAPI
- React
- Vite
- FFmpeg
- SQLite
- Axios

These technologies are used according to their respective documentation, licenses, and service terms.

---

# ✅ 28. Project Status

```text
PROJECT STATUS
────────────────────────────────────────

Prototype / Proof of Concept

PDF Processing             ✅
Audio Processing           ✅
Video Processing           ✅
Speech Transcription       ✅
RAG                        ✅
AI Agent                   ✅
AI Chat                    ✅
Study Notes                ✅
Quiz Generation            ✅
Conversation History       ✅
Testing                    ✅
Documentation              ✅
GitHub Repository          ✅

────────────────────────────────────────
```

---

# 📦 29. Project Deliverables

The project deliverables include:

- Working AI prototype
- GitHub repository
- Project README
- System architecture
- Data flow
- Technology stack
- Testing and results
- Responsible AI documentation
- Known limitations
- Future improvement plan
- Demonstration video

---

# 🎓 30. Conclusion

The Smart Media Analysis Agent demonstrates how modern AI technologies can be combined to create an intelligent educational assistant.

By integrating multimodal content processing, speech transcription, Retrieval-Augmented Generation, Azure AI Search, and Microsoft Foundry, the system transforms static educational material into an interactive learning experience.

```text
Educational Content
        ↓
   AI Processing
        ↓
 Search + Retrieval
        ↓
  Grounded AI Agent
        ↓
Interactive Learning
```

The project provides a foundation for building more personalized, intelligent, and scalable educational AI systems.
