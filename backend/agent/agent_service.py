import re
import os
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from backend.config.settings import settings
from backend.models.db_models import Document, DocumentChunk
from backend.models.schemas import Citation
from backend.agent.prompts import SYSTEM_AGENT_PROMPT
from backend.agent.tools import (
    AGENT_TOOLS_SCHEMA,
    tool_search_educational_content,
    tool_generate_summary,
    tool_extract_key_concepts,
    tool_generate_mcqs,
    tool_find_video_timestamps,
    tool_explain_in_simple_terms,
)


# =========================================================
# Environment
# =========================================================

load_dotenv()


# =========================================================
# Optional legacy Azure OpenAI support
# =========================================================

try:
    from openai import AzureOpenAI

    AZURE_OPENAI_AVAILABLE = True

except ImportError:
    AZURE_OPENAI_AVAILABLE = False


# =========================================================
# Agent Service
# =========================================================

class AgentService:
    """
    AI Agent Orchestrator for the Smart Media Analysis Agent.

    PRIMARY ARCHITECTURE
    --------------------
    React Frontend
        ↓
    FastAPI
        ↓
    Application RAG / Azure AI Search
        ↓
    Selected uploaded document
        ↓
    Retrieved educational context
        ↓
    Microsoft Foundry Agent
        ↓
    GPT-5-mini
        ↓
    Grounded answer + citations

    FALLBACK ARCHITECTURE
    ---------------------
    Existing local RAG / deterministic tools.

    The Foundry Agent is the primary path.
    Existing local functionality is retained as fallback.
    """

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(self):

        # -------------------------------------------------
        # Legacy Azure OpenAI client
        # -------------------------------------------------

        self.client = None

        if (
            settings.is_azure_openai_configured
            and AZURE_OPENAI_AVAILABLE
        ):
            try:

                self.client = AzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                )

                print(
                    "[AgentService] Legacy Azure OpenAI client configured."
                )

            except Exception as e:

                print(
                    "[AgentService] Azure OpenAI Init Warning: "
                    f"{type(e).__name__}: {e}"
                )

        # -------------------------------------------------
        # Microsoft Foundry Agent
        # -------------------------------------------------

        self.foundry_project = None
        self.foundry_openai = None

        foundry_endpoint = os.getenv(
            "FOUNDRY_PROJECT_ENDPOINT"
        )

        foundry_agent_name = os.getenv(
            "FOUNDRY_AGENT_NAME"
        )

        if foundry_endpoint and foundry_agent_name:

            try:

                # Azure CLI / DefaultAzureCredential
                credential = DefaultAzureCredential()

                # Connect to Microsoft Foundry project
                self.foundry_project = AIProjectClient(
                    endpoint=foundry_endpoint,
                    credential=credential,
                    allow_preview=True,
                )

                # Connect directly to the Foundry Agent
                self.foundry_openai = (
                    self.foundry_project.get_openai_client(
                        agent_name=foundry_agent_name
                    )
                )

                print(
                    "[AgentService] Microsoft Foundry Agent connected: "
                    f"{foundry_agent_name}"
                )

            except Exception as e:

                print(
                    "[AgentService] Foundry Init Warning: "
                    f"{type(e).__name__}: {e}"
                )

        else:

            print(
                "[AgentService] Microsoft Foundry configuration not found."
            )

    # =====================================================
    # Main Chat Entry Point
    # =====================================================

    def chat(
        self,
        db: Session,
        query: str,
        document_id: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Main AI Agent entry point.

        PRIMARY:
            Application RAG + Microsoft Foundry Agent

        FALLBACK:
            Existing local RAG/tool system
        """

        query_clean = query.strip()

        # -------------------------------------------------
        # Empty query
        # -------------------------------------------------

        if not query_clean:

            return {
                "response": "Please enter a question or command.",
                "citations": [],
                "tools_used": [],
                "is_grounded": False,
                "grounding_status": "NOT_FOUND",
            }

        # =================================================
        # PRIMARY: Microsoft Foundry + Application RAG
        # =================================================

        if self.foundry_openai:

            try:

                return self._chat_with_foundry(
                    db=db,
                    query=query_clean,
                    document_id=document_id,
                    chat_history=chat_history,
                )

            except Exception as e:

                print(
                    "[AgentService] Foundry Agent failed. "
                    f"Falling back to existing tools: "
                    f"{type(e).__name__}: {e}"
                )

        else:

            print(
                "[AgentService] Foundry client is unavailable. "
                "Using fallback RAG."
            )

        # =================================================
        # FALLBACK: Existing application logic
        # =================================================

        intent, params = self._classify_intent(
            query_clean,
            document_id,
        )

        # -------------------------------------------------
        # Legacy Azure OpenAI tool calling
        # -------------------------------------------------

        if (
            self.client
            and settings.is_azure_openai_configured
        ):

            try:

                return self._chat_with_azure_tools(
                    db=db,
                    query=query_clean,
                    document_id=document_id,
                    chat_history=chat_history,
                )

            except Exception as e:

                print(
                    "[AgentService] Azure tool calling failed. "
                    f"Using local tool dispatcher: {e}"
                )

        # -------------------------------------------------
        # Local deterministic tool dispatcher
        # -------------------------------------------------

        return self._dispatch_local_tool(
            db=db,
            intent=intent,
            params=params,
            raw_query=query_clean,
            document_id=document_id,
        )

    # =====================================================
    # Microsoft Foundry Agent + Application RAG
    # =====================================================

    def _chat_with_foundry(
        self,
        db: Session,
        query: str,
        document_id: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Primary grounded chat path.

        IMPORTANT:
        Retrieval is performed by the application first. The selected
        uploaded document is a hard boundary for the context sent to
        Microsoft Foundry.

        Flow:

            User question
                ↓
            Selected document
                ↓
            Application RAG / Azure AI Search
                ↓
            DB chunk fallback if necessary
                ↓
            Grounded context
                ↓
            Microsoft Foundry Agent
                ↓
            Answer + trusted application citations
        """

        if not self.foundry_openai:
            raise RuntimeError(
                "Microsoft Foundry Agent is not configured."
            )

        print("\n[AgentService] ========================================")
        print("[AgentService] GROUNDED CHAT START")
        print(f"[AgentService] Query: {query}")
        print(f"[AgentService] Document ID: {document_id}")

        # =================================================
        # STEP 1 — Verify selected document
        # =================================================

        selected_document = None

        if document_id:
            selected_document = (
                db.query(Document)
                .filter(Document.id == document_id)
                .first()
            )

            if not selected_document:
                return {
                    "response": (
                        "The selected educational document "
                        "could not be found."
                    ),
                    "citations": [],
                    "tools_used": [],
                    "is_grounded": False,
                    "grounding_status": "NOT_FOUND",
                }

            print(
                "[AgentService] Selected document: "
                f"{selected_document.filename}"
            )

        # =================================================
        # STEP 2 — Build conversation-aware retrieval query
        # =================================================

        retrieval_query = self._build_contextual_retrieval_query(
            query=query,
            chat_history=chat_history,
        )

        print("[AgentService] Retrieval query:")
        print(retrieval_query)

        # =================================================
        # STEP 3 — Retrieve ONLY application context
        # =================================================

        retrieval = self._retrieve_application_context(
            db=db,
            query=retrieval_query,
            document_id=document_id,
            top_k=4,
        )

        retrieved_chunks = retrieval["chunks"]
        citations = retrieval["citations"]
        filename = retrieval["filename"]

        print(
            "[AgentService] Trusted application RAG returned "
            f"{len(retrieved_chunks)} chunk(s)."
        )

        # =================================================
        # STEP 4 — No relevant content
        # =================================================

        if not retrieved_chunks:

            print(
                "[AgentService] No relevant content found."
            )

            return {
                "response": (
                    "I couldn't find this information in "
                    "the uploaded educational material."
                ),
                "citations": [],
                "tools_used": [
                    "search_educational_content"
                ],
                "is_grounded": False,
                "grounding_status": "NOT_FOUND",
            }

        # =================================================
        # STEP 5 — Build context
        # =================================================

        context_parts = []

        for i, chunk in enumerate(
            retrieved_chunks,
            start=1,
        ):
            source_filename = (
                chunk.get("source_filename")
                or filename
                or "Uploaded educational material"
            )

            page_number = chunk.get("page_number")
            timestamp_start = chunk.get("timestamp_start")
            timestamp_end = chunk.get("timestamp_end")

            if page_number is not None:
                reference = f"Page {page_number}"

            elif timestamp_start is not None:
                start_minutes = int(timestamp_start // 60)
                start_seconds = int(timestamp_start % 60)

                if timestamp_end is not None:
                    end_minutes = int(timestamp_end // 60)
                    end_seconds = int(timestamp_end % 60)

                    reference = (
                        f"Timestamp "
                        f"{start_minutes:02d}:{start_seconds:02d}-"
                        f"{end_minutes:02d}:{end_seconds:02d}"
                    )
                else:
                    reference = (
                        f"Timestamp "
                        f"{start_minutes:02d}:{start_seconds:02d}"
                    )
            else:
                reference = "Location unavailable"

            context_parts.append(
                f"""
--- TRUSTED RETRIEVED SOURCE {i} ---
File: {source_filename}
Reference: {reference}

Content:
{chunk.get("content", "")}
"""
            )

        retrieved_context = "\n".join(context_parts)

        # =================================================
        # STEP 6 — Strict grounding prompt
        # =================================================

        selected_name = (
            filename
            or "the uploaded educational material"
        )

        grounded_prompt = f"""
You are the Smart Media Analysis Agent.

You are answering a student's question about one
specific uploaded educational document.

SELECTED DOCUMENT:
{selected_name}

IMPORTANT:
The application has already retrieved the relevant
content from the selected uploaded document.

The section named TRUSTED RETRIEVED CONTEXT below is
your ONLY source of factual information.

STRICT RULES:

1. Answer ONLY from TRUSTED RETRIEVED CONTEXT.

2. Do NOT use your pretrained knowledge.

3. Do NOT use general internet knowledge.

4. Do NOT use information from another document.

5. Do NOT use information from your connected
   knowledge base unless that exact information also
   appears in TRUSTED RETRIEVED CONTEXT.

6. Treat the selected document as the only document
   relevant to this question.

7. If TRUSTED RETRIEVED CONTEXT does not support the
   answer, reply exactly:

"I couldn't find this information in the uploaded
educational material."

8. Do not give a general-knowledge answer when the
   information is missing.

9. Never invent facts, examples, page numbers,
   timestamps, quotations, or sources.

10. Do not add external citations.

11. The application will provide verified citations
    separately.

12. If the answer is supported, mention the selected
    source file naturally.

STUDENT QUESTION:
{query}

TRUSTED RETRIEVED CONTEXT:
{retrieved_context}

Answer the student's question now.
"""

        # =================================================
        # STEP 7 — Conversation context
        # =================================================

        if chat_history:
            recent_history = chat_history[-6:]

            history_text = "\n\n".join(
                [
                    f"{msg.get('role', 'user').upper()}: "
                    f"{msg.get('content', '')}"
                    for msg in recent_history
                ]
            )

            grounded_prompt += f"""

RECENT CONVERSATION:
{history_text}

Conversation history is only for understanding the
current question. Factual claims must still come
ONLY from TRUSTED RETRIEVED CONTEXT.
"""

        # =================================================
        # STEP 8 — Microsoft Foundry
        # =================================================

        print(
            "[AgentService] Sending trusted context "
            "to Microsoft Foundry..."
        )

        response = self.foundry_openai.responses.create(
            input=grounded_prompt
        )

        answer = getattr(
            response,
            "output_text",
            None,
        ) or ""

        answer = answer.strip()

        if not answer:
            answer = (
                "I couldn't generate a response from "
                "the uploaded educational material."
            )

        # Remove Foundry's internal citation markers from
        # visible text. Verified application citations are
        # returned separately.
        answer = re.sub(
            r"【\d+:\d+†[^】]+】",
            "",
            answer,
        ).strip()

        # =================================================
        # STEP 9 — Return trusted application citations
        # =================================================

        print(
            "[AgentService] Foundry response received."
        )
        print(
            f"[AgentService] Returning {len(citations)} "
            "application citation(s)."
        )
        print("[AgentService] GROUNDED CHAT END")
        print("[AgentService] ========================================\n")

        return {
            "response": answer,
            "citations": citations,
            "tools_used": [
                "search_educational_content",
                "microsoft_foundry_agent",
            ],
            "is_grounded": True,
            "grounding_status": "GROUNDED",
        }


    def _build_citations_from_chunks(
        self,
        chunks: List[Dict[str, Any]],
        default_filename: Optional[str] = None,
    ) -> List[Citation]:
        """Build citations from trusted application-RAG chunks."""

        citations: List[Citation] = []
        seen = set()

        for chunk in chunks:
            chunk_id = str(
                chunk.get("chunk_id")
                or chunk.get("id")
                or ""
            )

            source_filename = (
                chunk.get("source_filename")
                or default_filename
                or "Uploaded educational material"
            )

            unique_key = (
                chunk_id,
                source_filename,
                chunk.get("page_number"),
                chunk.get("timestamp_start"),
            )

            if unique_key in seen:
                continue

            seen.add(unique_key)

            media_type = (
                chunk.get("media_type")
                or "pdf"
            )

            if media_type not in {"pdf", "audio", "video"}:
                media_type = "pdf"

            citations.append(
                Citation(
                    chunk_id=chunk_id or f"chunk-{len(citations) + 1}",
                    media_type=media_type,
                    page_number=chunk.get("page_number"),
                    timestamp_start=chunk.get("timestamp_start"),
                    timestamp_end=chunk.get("timestamp_end"),
                    snippet=str(
                        chunk.get("content", "")
                    )[:500],
                    source_filename=source_filename,
                )
            )

        return citations

    def _build_contextual_retrieval_query(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Make retrieval conversation-aware for short follow-up questions.

        Example:
            User: What is the first concept explained?
            Assistant: The first concept is the Moon.
            User: Explain the concept.

        The retrieval query contains the recent conversation plus the
        current question, so Azure AI Search can resolve "the concept"
        to the topic discussed immediately before it.
        """

        query_clean = (query or "").strip()

        if not query_clean or not chat_history:
            return query_clean

        query_lower = query_clean.lower()

        # Conservative list of references that usually indicate a
        # conversational follow-up rather than a brand-new question.
        follow_up_patterns = [
            r"\bit\b",
            r"\bthis\b",
            r"\bthat\b",
            r"\bthese\b",
            r"\bthose\b",
            r"\bthe concept\b",
            r"\bthe topic\b",
            r"\bthe idea\b",
            r"\bthe point\b",
            r"\bthe above\b",
            r"\bthe previous\b",
            r"\bthis concept\b",
            r"\bthis topic\b",
            r"\bexplain it\b",
            r"\bexplain this\b",
            r"\bexplain that\b",
            r"\bwhy is it\b",
            r"\bwhy was it\b",
            r"\bwhy does it\b",
            r"\bwhy did it\b",
            r"\bhow is it\b",
            r"\bhow was it\b",
            r"\bhow does it\b",
            r"\bhow did it\b",
            r"\bwhat about it\b",
            r"\bwhat about this\b",
            r"\bwhat happens after\b",
            r"\bwhat happened after\b",
            r"\bwhat comes after\b",
            r"\bafter that\b",
        ]

        is_follow_up = (
            len(query_lower.split()) <= 18
            and any(
                re.search(pattern, query_lower)
                for pattern in follow_up_patterns
            )
        )

        # A normal standalone question should not be polluted with
        # unrelated conversation history.
        if not is_follow_up:
            return query_clean

        recent_history = chat_history[-6:]
        history_parts = []

        for message in recent_history:
            if not isinstance(message, dict):
                continue

            role = str(
                message.get("role", "user")
            ).strip().upper()

            content = str(
                message.get("content", "")
            ).strip()

            if not content:
                continue

            # Prevent a very long prior answer from making the search
            # query unnecessarily large.
            content = content[:1500]

            history_parts.append(
                f"{role}: {content}"
            )

        if not history_parts:
            return query_clean

        return (
            "Resolve the current follow-up question using "
            "the recent conversation below. Retrieve "
            "educational content relevant to the topic or "
            "entity being referred to.\n\n"
            "RECENT CONVERSATION:\n"
            + "\n".join(history_parts)
            + "\n\n"
            "CURRENT QUESTION:\n"
            + query_clean
        )

    def _retrieve_application_context(
        self,
        db: Session,
        query: str,
        document_id: Optional[str],
        top_k: int = 4,
    ) -> Dict[str, Any]:
        """
        Retrieve context from the application's own uploaded-document RAG.

        The selected document is treated as a hard boundary. If Azure AI
        Search does not return usable chunks, a database chunk fallback is
        used so a newly uploaded PDF can still be tested immediately.
        """

        selected_document = None

        if document_id:
            selected_document = (
                db.query(Document)
                .filter(Document.id == document_id)
                .first()
            )

            if not selected_document:
                return {
                    "chunks": [],
                    "citations": [],
                    "filename": None,
                }

        # -------------------------------------------------
        # First attempt: existing RAG / Azure AI Search
        # -------------------------------------------------

        try:
            search_res = tool_search_educational_content(
                db,
                query=query,
                document_id=document_id,
                top_k=top_k,
            )
        except Exception as e:
            print(
                "[AgentService] Application RAG search failed: "
                f"{type(e).__name__}: {e}"
            )
            search_res = {
                "has_content": False,
                "retrieved_chunks": [],
                "citations": [],
            }

        raw_chunks = search_res.get(
            "retrieved_chunks",
            [],
        ) or []

        # -------------------------------------------------
        # Hard document boundary
        # -------------------------------------------------

        if selected_document:
            selected_filename = selected_document.filename

            filtered_chunks = []

            for chunk in raw_chunks:
                chunk_document_id = chunk.get("document_id")
                chunk_filename = chunk.get("source_filename")

                if chunk_document_id is not None:
                    if str(chunk_document_id) == str(document_id):
                        filtered_chunks.append(chunk)

                elif chunk_filename:
                    if str(chunk_filename) == str(selected_filename):
                        filtered_chunks.append(chunk)

            raw_chunks = filtered_chunks

        # -------------------------------------------------
        # If trusted RAG returned chunks, use them.
        # -------------------------------------------------

        if raw_chunks:
            filename = (
                selected_document.filename
                if selected_document
                else raw_chunks[0].get(
                    "source_filename",
                    "Uploaded educational material",
                )
            )

            citations = self._build_citations_from_chunks(
                raw_chunks[:top_k],
                default_filename=filename,
            )

            return {
                "chunks": raw_chunks[:top_k],
                "citations": citations,
                "filename": filename,
            }

        # -------------------------------------------------
        # Second attempt: direct DB chunk fallback.
        #
        # This is especially useful immediately after a PDF
        # upload if Azure Search indexing is delayed/fails.
        # -------------------------------------------------

        if not selected_document:
            return {
                "chunks": [],
                "citations": [],
                "filename": None,
            }

        db_chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id
            )
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )

        if not db_chunks:
            return {
                "chunks": [],
                "citations": [],
                "filename": selected_document.filename,
            }

        # Simple lexical ranking over the selected PDF only.
        query_words = set(
            re.findall(
                r"\b[a-zA-Z0-9_]{2,}\b",
                query.lower(),
            )
        )

        stop_words = {
            "what", "is", "the", "a", "an", "of", "to",
            "for", "in", "on", "and", "or", "with", "from",
            "this", "that", "tell", "me", "about", "how",
            "why", "which", "where", "when", "does", "do",
            "can", "could", "would", "should", "please",
        }

        meaningful_words = {
            word
            for word in query_words
            if word not in stop_words
        }

        ranked = []

        for db_chunk in db_chunks:
            content = (
                db_chunk.content
                or ""
            )

            content_lower = content.lower()
            content_words = set(
                re.findall(
                    r"\b[a-zA-Z0-9_]{2,}\b",
                    content_lower,
                )
            )

            overlap = len(
                meaningful_words & content_words
            )

            phrase_bonus = (
                3.0
                if (
                    meaningful_words
                    and " ".join(
                        sorted(meaningful_words)
                    ) in content_lower
                )
                else 0.0
            )

            ranked.append(
                (
                    overlap + phrase_bonus,
                    db_chunk,
                )
            )

        ranked.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        # If we have meaningful query terms, require at least
        # one matching term. For very broad queries, return the
        # first chunks of the selected document.
        if meaningful_words:
            matched = [
                item
                for item in ranked
                if item[0] > 0
            ]
        else:
            matched = ranked

        selected_db_chunks = [
            item[1]
            for item in matched[:top_k]
        ]

        if not selected_db_chunks:
            return {
                "chunks": [],
                "citations": [],
                "filename": selected_document.filename,
            }

        converted_chunks = []

        for db_chunk in selected_db_chunks:
            converted_chunks.append(
                {
                    "chunk_id": str(db_chunk.id),
                    "document_id": str(db_chunk.document_id),
                    "content": db_chunk.content or "",
                    "media_type": (
                        db_chunk.media_type
                        or selected_document.media_type
                        or "pdf"
                    ),
                    "page_number": db_chunk.page_number,
                    "timestamp_start": db_chunk.timestamp_start,
                    "timestamp_end": db_chunk.timestamp_end,
                    "source_filename": selected_document.filename,
                }
            )

        citations = self._build_citations_from_chunks(
            converted_chunks,
            default_filename=selected_document.filename,
        )

        print(
            "[AgentService] Using DB chunk fallback for "
            f"{selected_document.filename}: "
            f"{len(converted_chunks)} chunk(s)."
        )

        return {
            "chunks": converted_chunks,
            "citations": citations,
            "filename": selected_document.filename,
        }

    # =====================================================
    # Intent Classification
    # =====================================================

    def _classify_intent(
        self,
        query: str,
        document_id: Optional[str],
    ) -> tuple[str, Dict[str, Any]]:
        """
        Classify student query into a local tool action.

        Used only by the fallback system.
        """

        q_lower = query.lower()

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        if re.search(
            r"\b("
            r"summarize|summary|overview|brief notes|tldr"
            r")\b",
            q_lower,
        ):

            return "summary", {
                "document_id": document_id
            }

        # -------------------------------------------------
        # Key Concepts
        # -------------------------------------------------

        if re.search(
            r"\b("
            r"key concepts|main concepts|important terms|"
            r"definitions|core topics|key takeaways"
            r")\b",
            q_lower,
        ):

            return "key_concepts", {
                "document_id": document_id
            }

        # -------------------------------------------------
        # MCQ / Quiz
        # -------------------------------------------------

        if re.search(
            r"\b("
            r"mcq|quiz|multiple choice|practice questions|"
            r"test me|exam questions"
            r")\b",
            q_lower,
        ):

            count_match = re.search(
                r"\b(\d+)\b",
                q_lower,
            )

            num_q = (
                int(count_match.group(1))
                if count_match
                else 5
            )

            return "mcq", {
                "document_id": document_id,
                "num_questions": min(num_q, 10),
                "difficulty": "medium",
            }

        # -------------------------------------------------
        # Simple Explanation
        # -------------------------------------------------

        if re.search(
            r"\b("
            r"explain in simple|simple language|"
            r"simple terms|eli5|explain simply|layman"
            r")\b",
            q_lower,
        ):

            topic = re.sub(
                r"^(explain|what is|tell me about)\s+",
                "",
                query,
                flags=re.IGNORECASE,
            )

            topic = re.sub(
                r"\s+in simple (terms|language|words)$",
                "",
                topic,
                flags=re.IGNORECASE,
            ).strip()

            return "simple_explain", {
                "topic": topic or query,
                "document_id": document_id,
            }

        # -------------------------------------------------
        # Video Timestamp
        # -------------------------------------------------

        if re.search(
            r"\b("
            r"where was|what time|which timestamp|"
            r"when did the professor|where in the video|"
            r"timestamp"
            r")\b",
            q_lower,
        ):

            return "timestamps", {
                "query": query,
                "document_id": document_id,
            }

        # -------------------------------------------------
        # Default factual search
        # -------------------------------------------------

        return "search", {
            "query": query,
            "document_id": document_id,
        }

    # =====================================================
    # Local Tool Dispatcher
    # =====================================================

    def _dispatch_local_tool(
        self,
        db: Session,
        intent: str,
        params: Dict[str, Any],
        raw_query: str,
        document_id: Optional[str],
    ) -> Dict[str, Any]:
        """
        Execute existing local tools.

        This is only the fallback path.
        """

        # -------------------------------------------------
        # Load document if provided
        # -------------------------------------------------

        doc = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
            if document_id
            else None
        )

        # =================================================
        # Summary
        # =================================================

        if intent == "summary" and document_id:

            summary_data = tool_generate_summary(
                db,
                document_id,
            )

            concepts_preview = "\n".join(
                [
                    f"• **{c['concept']}**: "
                    f"{c['description']}"
                    for c in summary_data["key_concepts"][:3]
                ]
            )

            response_text = (
                f"### {summary_data['title']}\n\n"
                f"{summary_data['overview']}\n\n"
                f"**Key Concepts:**\n"
                f"{concepts_preview}"
            )

            return {
                "response": response_text,
                "citations": [],
                "tools_used": [
                    "generate_summary"
                ],
                "is_grounded": True,
                "grounding_status": "GROUNDED",
            }

        # =================================================
        # Key Concepts
        # =================================================

        if intent == "key_concepts" and document_id:

            concepts_data = tool_extract_key_concepts(
                db,
                document_id,
            )

            if concepts_data["key_concepts"]:

                lines = [
                    f"### Key Concepts from "
                    f"{concepts_data['filename']}\n"
                ]

                for c in concepts_data["key_concepts"]:

                    if c.get("time_formatted"):

                        ref = (
                            f" *(at "
                            f"{c['time_formatted']})*"
                        )

                    elif c.get("page"):

                        ref = (
                            f" *(Page "
                            f"{c.get('page')})*"
                        )

                    else:

                        ref = ""

                    lines.append(
                        f"• **{c['concept']}**"
                        f"{ref}: "
                        f"{c['description']}"
                    )

                return {
                    "response": "\n".join(lines),
                    "citations": [],
                    "tools_used": [
                        "extract_key_concepts"
                    ],
                    "is_grounded": True,
                    "grounding_status": "GROUNDED",
                }

        # =================================================
        # MCQs
        # =================================================

        if intent == "mcq" and document_id:

            quiz_data = tool_generate_mcqs(
                db,
                document_id,
                params.get(
                    "num_questions",
                    5,
                ),
                params.get(
                    "difficulty",
                    "medium",
                ),
            )

            lines = [
                f"### Practice MCQs on "
                f"{doc.filename if doc else 'Lecture'}\n"
            ]

            for q in quiz_data["questions"]:

                lines.append(
                    f"**Q{q['id']}. "
                    f"{q['question']}**"
                )

                for opt_idx, opt in enumerate(
                    q["options"]
                ):

                    lines.append(
                        f"   {chr(65 + opt_idx)}. {opt}"
                    )

                lines.append(
                    f"*Correct Answer: Option "
                    f"{chr(65 + q['correct_answer_index'])}*\n"
                )

            return {
                "response": "\n".join(lines),
                "citations": [],
                "tools_used": [
                    "generate_mcqs"
                ],
                "is_grounded": True,
                "grounding_status": "GROUNDED",
            }

        # =================================================
        # Simple Explanation
        # =================================================

        if intent == "simple_explain":

            topic_str = params.get(
                "topic",
                raw_query,
            )

            result = tool_explain_in_simple_terms(
                db,
                topic=topic_str,
                document_id=document_id,
            )

            return {
                "response": result["explanation"],
                "citations": result["citations"],
                "tools_used": [
                    "explain_in_simple_terms",
                    "search_educational_content",
                ],
                "is_grounded": result["is_grounded"],
                "grounding_status": (
                    "GROUNDED"
                    if result["is_grounded"]
                    else "NOT_FOUND"
                ),
            }

        # =================================================
        # Video Timestamps
        # =================================================

        if intent == "timestamps" and document_id:

            ts_result = tool_find_video_timestamps(
                db,
                query=raw_query,
                document_id=document_id,
            )

            if ts_result["timestamps"]:

                lines = [
                    f"### Relevant Video Timestamps "
                    f"for '{raw_query}':\n"
                ]

                for t in ts_result["timestamps"]:

                    lines.append(
                        f"• **Timestamp "
                        f"[{t['timestamp_formatted']}]**: "
                        f"{t['topic_snippet']}"
                    )

                citations = [
                    Citation(
                        chunk_id=(
                            f"ts_{t['timestamp_seconds']}"
                        ),
                        media_type="video",
                        timestamp_start=(
                            t["timestamp_seconds"]
                        ),
                        timestamp_end=(
                            t["timestamp_seconds"] + 30.0
                        ),
                        snippet=t["topic_snippet"],
                        source_filename=(
                            ts_result["filename"]
                        ),
                    )
                    for t in ts_result["timestamps"]
                ]

                return {
                    "response": "\n".join(lines),
                    "citations": citations,
                    "tools_used": [
                        "find_video_timestamps"
                    ],
                    "is_grounded": True,
                    "grounding_status": "GROUNDED",
                }

        # =================================================
        # Factual Local RAG Search
        # =================================================

        search_res = tool_search_educational_content(
            db,
            query=raw_query,
            document_id=document_id,
            top_k=4,
        )

        # -------------------------------------------------
        # Nothing found
        # -------------------------------------------------

        if not search_res["has_content"]:

            return {
                "response": (
                    "I couldn't find this information in "
                    "the uploaded educational material."
                ),
                "citations": [],
                "tools_used": [
                    "search_educational_content"
                ],
                "is_grounded": False,
                "grounding_status": "NOT_FOUND",
            }

        # -------------------------------------------------
        # Top retrieved chunk
        # -------------------------------------------------

        top_chunk = search_res[
            "retrieved_chunks"
        ][0]

        media_name = (
            doc.filename
            if doc
            else top_chunk.get(
                "source_filename",
                "the educational material",
            )
        )

        time_tag = ""

        if top_chunk.get(
            "timestamp_start"
        ) is not None:

            mins = int(
                top_chunk["timestamp_start"] // 60
            )

            secs = int(
                top_chunk["timestamp_start"] % 60
            )

            time_tag = (
                f" at timestamp "
                f"**{mins:02d}:{secs:02d}**"
            )

        elif top_chunk.get(
            "page_number"
        ):

            time_tag = (
                f" on **Page "
                f"{top_chunk['page_number']}**"
            )

        parts = [
            f"Based on **{media_name}**{time_tag}:",
            (
                f'\n> *"{top_chunk["content"][:250]}..."*'
            ),
            "\n**Key Takeaway:**",
            f"• {top_chunk['content']}",
        ]

        # -------------------------------------------------
        # Additional chunks
        # -------------------------------------------------

        if len(
            search_res["retrieved_chunks"]
        ) > 1:

            parts.append(
                "\n**Additional Related Points:**"
            )

            for sc in search_res[
                "retrieved_chunks"
            ][1:3]:

                if sc.get(
                    "timestamp_start"
                ) is not None:

                    sc_tag = (
                        f" [Time "
                        f"{int(sc['timestamp_start'] // 60):02d}:"
                        f"{int(sc['timestamp_start'] % 60):02d}]"
                    )

                elif sc.get(
                    "page_number"
                ):

                    sc_tag = (
                        f" [Page "
                        f"{sc.get('page_number')}]"
                    )

                else:

                    sc_tag = ""

                parts.append(
                    f"• {sc_tag} "
                    f"{sc['content'][:150]}..."
                )

        return {
            "response": "\n".join(parts),
            "citations": search_res["citations"],
            "tools_used": [
                "search_educational_content"
            ],
            "is_grounded": True,
            "grounding_status": "GROUNDED",
        }

    # =====================================================
    # Legacy Azure OpenAI Tool Calling
    # =====================================================

    def _chat_with_azure_tools(
        self,
        db: Session,
        query: str,
        document_id: Optional[str],
        chat_history: Optional[List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        """
        Legacy Azure OpenAI tool-calling system.

        This remains available as a fallback.
        """

        retrieval_query = self._build_contextual_retrieval_query(
            query=query,
            chat_history=chat_history,
        )

        search_res = tool_search_educational_content(
            db,
            query=retrieval_query,
            document_id=document_id,
            top_k=4,
        )

        context_str = ""

        for i, c in enumerate(
            search_res["retrieved_chunks"]
        ):

            if c.get("page_number"):

                ref = (
                    f"[Page {c['page_number']}]"
                )

            elif c.get(
                "timestamp_start"
            ) is not None:

                ref = (
                    f"[Timestamp "
                    f"{int(c.get('timestamp_start', 0) // 60):02d}:"
                    f"{int(c.get('timestamp_start', 0) % 60):02d}]"
                )

            else:

                ref = "[Location unavailable]"

            context_str += (
                f"\n--- Source #{i + 1} {ref} ---\n"
                f"{c['content']}\n"
            )

        # -------------------------------------------------
        # Build messages
        # -------------------------------------------------

        messages = [
            {
                "role": "system",
                "content": SYSTEM_AGENT_PROMPT,
            }
        ]

        if chat_history:

            for msg in chat_history[-6:]:

                messages.append(
                    {
                        "role": msg.get(
                            "role",
                            "user",
                        ),
                        "content": msg.get(
                            "content",
                            "",
                        ),
                    }
                )

        prompt = (
            f"Student Question: {query}\n\n"
            f"Retrieved Educational Context:\n"
            f"{context_str or 'No relevant context found.'}\n\n"
            f"Answer clearly and cite specific page "
            f"numbers or timestamps."
        )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        # -------------------------------------------------
        # Call legacy Azure OpenAI
        # -------------------------------------------------

        res = self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=messages,
            temperature=0.2,
        )

        answer = res.choices[0].message.content

        citations = search_res["citations"]

        return {
            "response": answer,
            "citations": citations,
            "tools_used": [
                "search_educational_content"
            ],
            "is_grounded": bool(citations),
            "grounding_status": (
                "GROUNDED"
                if citations
                else "NOT_FOUND"
            ),
        }

    # =====================================================
    # Summary
    # =====================================================

    def generate_summary(
        self,
        db: Session,
        document_id: str,
    ) -> Dict[str, Any]:

        return tool_generate_summary(
            db,
            document_id,
            self.foundry_openai,
        )

    # =====================================================
    # Quiz
    # =====================================================

    def generate_quiz(
        self,
        db: Session,
        document_id: str,
        num_questions: int = 5,
        difficulty: str = "medium",
    ) -> Dict[str, Any]:

        return tool_generate_mcqs(
            db=db,
            document_id=document_id,
            num_questions=num_questions,
            difficulty=difficulty,
            openai_client=self.foundry_openai,
        )


# =========================================================
# Global Agent Service Instance
# =========================================================

agent_service = AgentService()