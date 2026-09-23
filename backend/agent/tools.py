"""
Structured Tools for the Smart Media Analysis Agent.
Contains tool implementations and JSON function definitions
for Microsoft Foundry / Azure OpenAI.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.models.db_models import (
    Document,
    DocumentChunk,
    GeneratedQuiz,
)
from backend.models.schemas import (
    Citation,
    MCQQuestion,
    KeyConceptItem,
)
from backend.rag.rag_engine import rag_engine
from backend.utils.helpers import format_timestamp


# ============================================================================
# OpenAI / Foundry Tool Function Definitions
# ============================================================================

AGENT_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_educational_content",
            "description": (
                "Searches and retrieves factual chunks from uploaded "
                "lecture notes, PDFs, audio transcripts, or videos "
                "using hybrid RAG."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The search query or factual topic to look up "
                            "in the materials."
                        ),
                    },
                    "document_id": {
                        "type": "string",
                        "description": (
                            "Optional specific document ID to restrict "
                            "the search to."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_summary",
            "description": (
                "Generates a structured pedagogical summary and "
                "executive overview of the lecture content."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": (
                            "The ID of the document to summarize."
                        ),
                    },
                },
                "required": ["document_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_key_concepts",
            "description": (
                "Extracts fundamental pedagogical definitions, "
                "formulas, and concepts from the educational resource."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": (
                            "The ID of the document to extract concepts from."
                        ),
                    },
                },
                "required": ["document_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_mcqs",
            "description": (
                "Generates curriculum-aligned Multiple Choice Questions "
                "(MCQs) with answer keys and explanations grounded "
                "in the material."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": (
                            "The ID of the document to generate "
                            "questions from."
                        ),
                    },
                    "num_questions": {
                        "type": "integer",
                        "description": (
                            "Number of questions to generate (1-10). "
                            "Default is 5."
                        ),
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                        "description": "Difficulty level of the quiz.",
                    },
                },
                "required": ["document_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_video_timestamps",
            "description": (
                "Finds specific timestamps and video playback segments "
                "where a topic is discussed in video or audio recordings."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The concept or spoken phrase to locate "
                            "in the video/audio recording."
                        ),
                    },
                    "document_id": {
                        "type": "string",
                        "description": (
                            "The ID of the video or audio document."
                        ),
                    },
                },
                "required": ["query", "document_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_in_simple_terms",
            "description": (
                "Breaks down complex academic concepts, formulas, "
                "or terminology into simple, intuitive, "
                "student-friendly explanations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": (
                            "The complex concept or equation to simplify."
                        ),
                    },
                    "document_id": {
                        "type": "string",
                        "description": (
                            "Optional document ID to ground the "
                            "explanation in lecture context."
                        ),
                    },
                },
                "required": ["topic"],
            },
        },
    },
]


# ============================================================================
# Tool 1 — Educational Content Search
# ============================================================================

def tool_search_educational_content(
    db: Session,
    query: str,
    document_id: Optional[str] = None,
    top_k: int = 4,
) -> Dict[str, Any]:
    """Search educational content using Hybrid RAG."""

    doc_chunks = []
    document = None

    if document_id:

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document:

            doc_chunks = (
                db.query(DocumentChunk)
                .filter(
                    DocumentChunk.document_id == document_id
                )
                .all()
            )

    else:

        doc_chunks = (
            db.query(DocumentChunk)
            .limit(100)
            .all()
        )

    retrieved = rag_engine.retrieve_context(
        query=query,
        document_id=document_id,
        db_chunks=doc_chunks,
        top_k=top_k,
    )

    has_content = (
        len(retrieved) > 0
        and retrieved[0].get("score", 0.0) >= 0.35
    )

    citations = []

    if has_content:

        for c in retrieved:

            if c.get("score", 0.0) < 0.35:
                continue

            snippet = c.get(
                "content",
                "",
            )

            if len(snippet) > 150:
                snippet = snippet[:150] + "..."

            citations.append(
                Citation(
                    chunk_id=str(
                        c.get(
                            "chunk_id",
                            "c1",
                        )
                    ),
                    media_type=c.get(
                        "media_type",
                        "document",
                    ),
                    page_number=c.get(
                        "page_number"
                    ),
                    timestamp_start=c.get(
                        "timestamp_start"
                    ),
                    timestamp_end=c.get(
                        "timestamp_end"
                    ),
                    snippet=snippet,
                    source_filename=(
                        document.filename
                        if document
                        else c.get(
                            "source_filename",
                            "Lecture Notes",
                        )
                    ),
                )
            )

    return {
        "query": query,
        "document_id": document_id,
        "retrieved_chunks": (
            retrieved
            if has_content
            else []
        ),
        "citations": citations,
        "has_content": has_content,
    }


# ============================================================================
# Tool 2 — AI-Powered Study Notes / Summary
# ============================================================================

def tool_generate_summary(
    db: Session,
    document_id: str,
    openai_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Generate AI-powered structured study notes.

    The notes are generated ONLY from chunks belonging to
    the selected document.
    """

    # ------------------------------------------------------------------------
    # 1. Get selected document
    # ------------------------------------------------------------------------

    doc = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not doc:
        raise ValueError(
            f"Document with ID {document_id} not found."
        )

    # ------------------------------------------------------------------------
    # 2. Get chunks ONLY from selected document
    # ------------------------------------------------------------------------

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id
        )
        .order_by(
            DocumentChunk.chunk_index
        )
        .all()
    )

    if not chunks:

        return {
            "document_id": doc.id,
            "title": f"Study Notes: {doc.filename}",
            "overview": (
                "No processed educational content is available "
                "for this document yet."
            ),
            "key_concepts": [],
            "action_items": [
                "Wait for the document to finish processing "
                "and try again."
            ],
        }

    # ------------------------------------------------------------------------
    # 3. Make sure Foundry client exists
    # ------------------------------------------------------------------------

    if openai_client is None:

        raise RuntimeError(
            "Microsoft Foundry client is not available "
            "for Study Notes generation."
        )

    # ------------------------------------------------------------------------
    # 4. Build grounded context
    # ------------------------------------------------------------------------

    context_parts = []

    # First version: use up to 30 chunks.
    selected_chunks = chunks[:30]

    for index, chunk in enumerate(
        selected_chunks,
        start=1,
    ):

        content = (
            chunk.content or ""
        ).strip()

        if not content:
            continue

        source_info = (
            f"Source Chunk {index}"
        )

        if chunk.page_number is not None:

            source_info += (
                f" | Page {chunk.page_number}"
            )

        if chunk.timestamp_start is not None:

            source_info += (
                f" | Timestamp "
                f"{format_timestamp(chunk.timestamp_start)}"
            )

        if chunk.timestamp_end is not None:

            source_info += (
                f" - "
                f"{format_timestamp(chunk.timestamp_end)}"
            )

        context_parts.append(
            f"[{source_info}]\n{content}"
        )

    grounded_context = (
        "\n\n".join(context_parts)
    )

    if not grounded_context.strip():

        return {
            "document_id": doc.id,
            "title": f"Study Notes: {doc.filename}",
            "overview": (
                "No readable educational content was found "
                "in this document."
            ),
            "key_concepts": [],
            "action_items": [],
        }

    # ------------------------------------------------------------------------
    # 5. Grounded AI prompt
    # ------------------------------------------------------------------------

    prompt = f"""
You are an expert educational study-notes generator.

Create high-quality study notes ONLY from the educational
material supplied below.

DOCUMENT:
{doc.filename}

=========================================================
STRICT GROUNDING RULES
=========================================================

1. Use ONLY the supplied source material.
2. Do NOT use information from other uploaded documents.
3. Do NOT add outside/general knowledge.
4. Do NOT invent definitions, formulas, examples, facts,
   page numbers, or technical details.
5. Preserve important terminology used in the source.
6. Rewrite the material into clear student-friendly notes.
7. Do NOT copy large passages from the source.
8. Organize the material by meaningful topics.
9. Make the notes useful for examination revision.
10. Every key concept must be supported by the source.
11. If something is not supported by the source, omit it.

=========================================================
CREATE
=========================================================

A. EXECUTIVE OVERVIEW

Give a concise but informative overview of what the
document teaches.

B. KEY CONCEPTS

For each important topic include:

- Topic/concept name
- Clear explanation
- Important details from the source
- Page number when available
- Timestamp when available

C. STUDY CHECKLIST

Create useful revision tasks based ONLY on this document.

Examples:

- Revise an important definition.
- Understand an important concept.
- Review a formula explicitly present in the material.
- Compare concepts if the source compares them.

Do not create generic tasks unrelated to this document.

=========================================================
OUTPUT
=========================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "overview": "Concise but informative overview.",

    "key_concepts": [
        {{
            "concept": "Topic name",
            "description": "Student-friendly explanation.",
            "page": 1,
            "timestamp": null
        }}
    ],

    "action_items": [
        "Document-specific revision task",
        "Another document-specific revision task"
    ]
}}

=========================================================
KEY CONCEPT RULES
=========================================================

Generate approximately 5-10 concepts when enough
information is available.

For each concept:

- Use the actual topic name from the document.
- Explain it clearly.
- Include important details from the source.
- Avoid unnecessary repetition.
- Do not create unsupported concepts.

For "page":

Use the page number from the relevant source chunk.

If unavailable, use null.

For "timestamp":

Use the timestamp from the relevant source chunk.

If unavailable, use null.

=========================================================
SOURCE MATERIAL
=========================================================

{grounded_context}

=========================================================

Return ONLY JSON.
"""

    # ------------------------------------------------------------------------
    # 6. Call existing Microsoft Foundry client
    # ------------------------------------------------------------------------

    try:

        response = openai_client.responses.create(
            input=prompt
        )

        raw_output = (
            response.output_text or ""
        ).strip()

        if not raw_output:

            raise ValueError(
                "Foundry returned an empty response."
            )

    except Exception as e:

        print(
            "[StudySummary] Foundry generation failed: "
            f"{type(e).__name__}: {e}"
        )

        raise

    # ------------------------------------------------------------------------
    # 7. Remove Markdown JSON fences if present
    # ------------------------------------------------------------------------

    raw_output = re.sub(
        r"^```json\s*",
        "",
        raw_output,
        flags=re.IGNORECASE,
    )

    raw_output = re.sub(
        r"^```\s*",
        "",
        raw_output,
    )

    raw_output = re.sub(
        r"\s*```$",
        "",
        raw_output,
    ).strip()

    # ------------------------------------------------------------------------
    # 8. Parse JSON
    # ------------------------------------------------------------------------

    try:

        generated = json.loads(
            raw_output
        )

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            raw_output,
            flags=re.DOTALL,
        )

        if not match:

            raise ValueError(
                "Foundry returned invalid JSON "
                "for Study Notes."
            )

        try:

            generated = json.loads(
                match.group(0)
            )

        except json.JSONDecodeError as e:

            raise ValueError(
                "Could not parse Foundry Study Notes JSON."
            ) from e

    # ------------------------------------------------------------------------
    # 9. Validate overview
    # ------------------------------------------------------------------------

    overview = generated.get(
        "overview",
        "",
    )

    if not isinstance(
        overview,
        str,
    ):

        overview = str(
            overview
        )

    overview = overview.strip()

    # ------------------------------------------------------------------------
    # 10. Validate key concepts
    # ------------------------------------------------------------------------

    key_concepts = generated.get(
        "key_concepts",
        [],
    )

    if not isinstance(
        key_concepts,
        list,
    ):

        key_concepts = []

    normalized_concepts = []

    for item in key_concepts:

        if not isinstance(
            item,
            dict,
        ):
            continue

        concept = str(
            item.get(
                "concept",
                "",
            )
        ).strip()

        description = str(
            item.get(
                "description",
                "",
            )
        ).strip()

        if not concept or not description:
            continue

        page = item.get(
            "page"
        )

        timestamp = item.get(
            "timestamp"
        )

        normalized_concepts.append(
            {
                "concept": concept,
                "description": description,
                "page": page,
                "timestamp": timestamp,
            }
        )

    # ------------------------------------------------------------------------
    # 11. Validate action items
    # ------------------------------------------------------------------------

    action_items = generated.get(
        "action_items",
        [],
    )

    if not isinstance(
        action_items,
        list,
    ):

        action_items = []

    normalized_actions = []

    for action in action_items:

        if not isinstance(
            action,
            str,
        ):
            continue

        action = action.strip()

        if action:

            normalized_actions.append(
                action
            )

    # ------------------------------------------------------------------------
    # 12. Fallback overview
    # ------------------------------------------------------------------------

    if not overview:

        overview = (
            f"This document contains educational material "
            f"from {doc.filename}. Review the key concepts "
            f"below for revision."
        )

    # ------------------------------------------------------------------------
    # 13. Save generated notes
    # ------------------------------------------------------------------------

    doc.summary_text = overview
    doc.key_concepts = normalized_concepts
    doc.action_items = normalized_actions

    db.commit()

    # ------------------------------------------------------------------------
    # 14. Return frontend-compatible response
    # ------------------------------------------------------------------------

    return {
        "document_id": doc.id,
        "title": f"Study Notes: {doc.filename}",
        "overview": overview,
        "key_concepts": normalized_concepts,
        "action_items": normalized_actions,
    }


# ============================================================================
# Tool 4 — Extract Key Concepts
# ============================================================================

def tool_extract_key_concepts(
    db: Session,
    document_id: str,
) -> Dict[str, Any]:
    """Extract fundamental pedagogical concepts."""

    doc = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not doc:
        raise ValueError(
            f"Document with ID {document_id} not found."
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id
        )
        .all()
    )

    concepts = []

    for idx, chunk in enumerate(
        chunks[:6]
    ):

        content = (
            chunk.content or ""
        ).strip()

        first_line = (
            content.split(".")[0].strip()
            if content
            else f"Core Topic {idx + 1}"
        )

        description = (
            content[:160] + "..."
            if len(content) > 160
            else content
        )

        concepts.append(
            {
                "concept": first_line[:45],
                "description": description,
                "page": chunk.page_number,
                "timestamp": chunk.timestamp_start,
                "time_formatted": (
                    format_timestamp(
                        chunk.timestamp_start
                    )
                    if chunk.timestamp_start is not None
                    else None
                ),
            }
        )

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "total_concepts": len(concepts),
        "key_concepts": concepts,
    }


# ============================================================================
# Tool 3 — Generate MCQs
# ============================================================================

def tool_generate_mcqs(
    db: Session,
    document_id: str,
    num_questions: int = 5,
    difficulty: str = "medium",
    openai_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Generate grounded MCQs using Microsoft Foundry.

    Questions are generated strictly from the selected document's
    extracted chunks. The document filename is never included in
    the question wording.
    """

    # ---------------------------------------------------------
    # Find selected document
    # ---------------------------------------------------------

    doc = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not doc:
        raise ValueError(
            f"Document with ID {document_id} not found."
        )

    # ---------------------------------------------------------
    # Get chunks ONLY from selected document
    # ---------------------------------------------------------

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id
        )
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    if not chunks:
        raise ValueError(
            "No processed educational content was found "
            "for this document."
        )

    # ---------------------------------------------------------
    # Foundry client is required
    # ---------------------------------------------------------

    if openai_client is None:
        raise RuntimeError(
            "Microsoft Foundry client is not available. "
            "Cannot generate AI-powered quiz."
        )

    # ---------------------------------------------------------
    # Prepare grounded context
    # ---------------------------------------------------------

    context_parts = []

    for chunk in chunks[:30]:

        content = (chunk.content or "").strip()

        if not content:
            continue

        content = re.sub(
            r"\s+",
            " ",
            content
        ).strip()

        if len(content) < 30:
            continue

        source_info = (
            f"Page: {chunk.page_number}"
            if chunk.page_number is not None
            else ""
        )

        if chunk.timestamp_start is not None:
            source_info += (
                f" | Timestamp: {chunk.timestamp_start}"
            )

        context_parts.append(
            f"""
SOURCE CHUNK
{source_info}

CONTENT:
{content}
""".strip()
        )

    context = "\n\n---\n\n".join(context_parts)

    if not context.strip():
        raise ValueError(
            "The selected document does not contain enough "
            "usable content to generate a quiz."
        )

    # ---------------------------------------------------------
    # Limit requested questions
    # ---------------------------------------------------------

    try:
        num_questions = int(num_questions)
    except (TypeError, ValueError):
        num_questions = 5

    num_questions = max(
        1,
        min(num_questions, 20)
    )

    difficulty = str(
        difficulty or "medium"
    ).lower().strip()

    if difficulty not in {
        "easy",
        "medium",
        "hard",
    }:
        difficulty = "medium"

    # ---------------------------------------------------------
    # Strict grounded quiz prompt
    # ---------------------------------------------------------

    prompt = f"""
You are an educational assessment generator.

Generate exactly {num_questions} multiple-choice questions
from the educational material provided below.

DIFFICULTY:
{difficulty}

IMPORTANT GROUNDING RULES:

1. Use ONLY the information contained in the provided source
   material.

2. Do NOT use outside knowledge to create facts, answers,
   distractors, explanations, or examples.

3. Do NOT mention the document filename in any question.

4. Do NOT begin questions with:
   - "Based on the PDF..."
   - "According to the document..."
   - "According to [filename]..."
   - "Based on '[filename]'..."

5. Do NOT copy long document headings into questions or options.

6. Do NOT copy raw extraction artifacts such as:
   - =====
   - -----
   - page labels
   - repeated headings
   - formatting noise

7. Rewrite the source material naturally into concise
   educational questions.

8. Each question should test a meaningful concept from the
   material.

9. Questions should be concise enough to read comfortably
   on a quiz screen.

10. Each question must have exactly FOUR options.

11. Exactly ONE option must be correct.

12. The correct answer MUST NOT always be option A.
    Distribute correct answers naturally across A, B, C and D.

13. Distractors must be plausible and related to the same
    subject matter.

14. Do not make distractors absurd or unrelated.

15. Keep the options reasonably similar in length and style.

16. Do not make the correct answer obviously longer than
    the other options.

17. Explanations must briefly explain WHY the correct answer
    is correct using the source material.

18. Do not expose raw source text in explanations.

19. Each question must contain enough context to understand
    it independently.

20. Do not create duplicate or nearly duplicate questions.

QUESTION STYLE:

Prefer natural questions such as:

"What is the primary function of the ALU?"

"Which statement correctly describes addressing modes?"

"What happens when an interrupt is triggered?"

"Which signal separates address and data on multiplexed lines?"

Avoid:

"Based on definitions_all_experiments.pdf, what is..."

"According to the document, what is..."

SOURCE MATERIAL:

{context}

RETURN FORMAT:

Return ONLY valid JSON.

Do not use Markdown.
Do not use ```json.
Do not add any explanation before or after the JSON.

Use exactly this structure:

{{
  "questions": [
    {{
      "id": 1,
      "question": "Concise question",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer_index": 0,
      "explanation": "Brief explanation grounded in the source material.",
      "source_chunk": 0
    }}
  ]
}}

IMPORTANT:

- correct_answer_index must be 0, 1, 2, or 3.
- source_chunk must refer to the SOURCE CHUNK number that
  supports the question.
- Make sure the selected correct answer actually matches
  the source material.
- Do not use the filename anywhere inside the questions,
  options, or explanations.
"""

    # ---------------------------------------------------------
    # Call Microsoft Foundry
    # ---------------------------------------------------------

    response = openai_client.responses.create(
        input=prompt
    )

    raw_output = (
        getattr(response, "output_text", "")
        or ""
    ).strip()

    if not raw_output:
        raise RuntimeError(
            "Microsoft Foundry returned an empty quiz response."
        )

    # ---------------------------------------------------------
    # Clean possible Markdown fences
    # ---------------------------------------------------------

    cleaned_output = raw_output.strip()

    if cleaned_output.startswith("```"):
        cleaned_output = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned_output,
            flags=re.IGNORECASE
        )

        cleaned_output = re.sub(
            r"\s*```$",
            "",
            cleaned_output
        ).strip()

    # ---------------------------------------------------------
    # Parse JSON
    # ---------------------------------------------------------

    try:
        quiz_data = json.loads(
            cleaned_output
        )
    except json.JSONDecodeError:

        # Try extracting the JSON object
        json_match = re.search(
            r"\{.*\}",
            cleaned_output,
            re.DOTALL
        )

        if not json_match:
            raise RuntimeError(
                "Foundry returned an invalid quiz response."
            )

        try:
            quiz_data = json.loads(
                json_match.group(0)
            )
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Could not parse the quiz generated "
                "by Microsoft Foundry."
            ) from exc

    generated_questions = quiz_data.get(
        "questions",
        []
    )

    if not isinstance(
        generated_questions,
        list
    ):
        raise RuntimeError(
            "Foundry quiz response does not contain "
            "a valid questions list."
        )

    # ---------------------------------------------------------
    # Validate and normalize questions
    # ---------------------------------------------------------

    questions = []

    for i, item in enumerate(
        generated_questions[:num_questions]
    ):

        if not isinstance(item, dict):
            continue

        question_text = str(
            item.get("question", "")
        ).strip()

        options = item.get(
            "options",
            []
        )

        explanation = str(
            item.get("explanation", "")
        ).strip()

        correct_index = item.get(
            "correct_answer_index"
        )

        source_chunk_index = item.get(
            "source_chunk",
            0
        )

        # ---------------------------------------------
        # Basic validation
        # ---------------------------------------------

        if not question_text:
            continue

        if not isinstance(
            options,
            list
        ) or len(options) != 4:
            continue

        options = [
            str(option).strip()
            for option in options
        ]

        if any(
            not option
            for option in options
        ):
            continue

        try:
            correct_index = int(
                correct_index
            )
        except (
            TypeError,
            ValueError
        ):
            continue

        if correct_index not in {
            0,
            1,
            2,
            3,
        }:
            continue

        if not explanation:
            explanation = (
                "The answer is supported by "
                "the selected educational material."
            )

        # ---------------------------------------------
        # Remove accidental filename references
        # ---------------------------------------------

        filename_variants = [
            doc.filename,
            Path(doc.filename).stem,
        ]

        for filename_variant in filename_variants:

            if not filename_variant:
                continue

            question_text = question_text.replace(
                filename_variant,
                ""
            ).strip()

            explanation = explanation.replace(
                filename_variant,
                ""
            ).strip()

            options = [
                option.replace(
                    filename_variant,
                    ""
                ).strip()
                for option in options
            ]

        # Remove common unwanted prefixes
        question_text = re.sub(
            r"^(based on|according to)\s+(the\s+)?(document|pdf)[,:]?\s*",
            "",
            question_text,
            flags=re.IGNORECASE
        ).strip()

        # ---------------------------------------------
        # Resolve citation chunk
        # ---------------------------------------------

        try:
            source_chunk_index = int(
                source_chunk_index
            )
        except (
            TypeError,
            ValueError
        ):
            source_chunk_index = 0

        if (
            source_chunk_index < 0
            or source_chunk_index >= len(chunks)
        ):
            source_chunk_index = min(
                i,
                len(chunks) - 1
            )

        source_chunk = chunks[
            source_chunk_index
        ]

        source_content = (
            source_chunk.content or ""
        ).strip()

        # ---------------------------------------------
        # Build frontend-compatible question
        # ---------------------------------------------

        questions.append(
            {
                "id": i + 1,
                "question": question_text,
                "options": options,
                "correct_answer_index": correct_index,
                "explanation": explanation,
                "citation": {
                    "page": source_chunk.page_number,
                    "timestamp": source_chunk.timestamp_start,
                    "snippet": source_content[:180],
                },
            }
        )

    # ---------------------------------------------------------
    # Ensure we actually received usable questions
    # ---------------------------------------------------------

    if not questions:
        raise RuntimeError(
            "Microsoft Foundry did not return any valid "
            "quiz questions. Please try generating the quiz again."
        )

    # ---------------------------------------------------------
    # Save quiz
    # ---------------------------------------------------------

    quiz = GeneratedQuiz(
        document_id=document_id,
        title=f"Quiz: {doc.filename}",
        difficulty=difficulty,
        questions=questions,
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    # ---------------------------------------------------------
    # Return frontend-compatible response
    # ---------------------------------------------------------

    return {
        "quiz_id": quiz.id,
        "document_id": doc.id,
        "title": quiz.title,
        "difficulty": difficulty,
        "questions": questions,
    }


# ============================================================================
# Tool 5 — Find Video / Audio Timestamps
# ============================================================================

def tool_find_video_timestamps(
    db: Session,
    query: str,
    document_id: str,
) -> Dict[str, Any]:
    """Search video/audio timestamps matching a query."""

    doc = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not doc:
        raise ValueError(
            f"Document with ID {document_id} not found."
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id
        )
        .all()
    )

    timestamped_chunks = [
        chunk
        for chunk in chunks
        if chunk.timestamp_start is not None
    ]

    retrieved = rag_engine._local_hybrid_search(
        query,
        timestamped_chunks,
        top_k=3,
    )

    matching_timestamps = []

    for result in retrieved:

        if (
            result.get("score", 0.0) >= 0.1
            and result.get("timestamp_start") is not None
        ):

            content = result.get(
                "content",
                "",
            )

            matching_timestamps.append(
                {
                    "timestamp_seconds": result[
                        "timestamp_start"
                    ],
                    "timestamp_formatted": format_timestamp(
                        result[
                            "timestamp_start"
                        ]
                    ),
                    "topic_snippet": (
                        content[:140] + "..."
                        if len(content) > 140
                        else content
                    ),
                    "score": result.get(
                        "score",
                        0.0,
                    ),
                }
            )

    return {
        "document_id": document_id,
        "filename": doc.filename,
        "query": query,
        "matches_found": len(
            matching_timestamps
        ),
        "timestamps": matching_timestamps,
    }


# ============================================================================
# Tool — Explain in Simple Terms
# ============================================================================

def tool_explain_in_simple_terms(
    db: Session,
    topic: str,
    document_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Explain a complex educational topic simply."""

    search_res = tool_search_educational_content(
        db,
        query=topic,
        document_id=document_id,
        top_k=2,
    )

    if not search_res["has_content"]:

        return {
            "topic": topic,
            "explanation": (
                f"I cannot find information regarding "
                f"'{topic}' in the uploaded educational "
                f"materials. Please ensure the relevant "
                f"lecture is uploaded."
            ),
            "citations": [],
            "is_grounded": False,
        }

    top_chunk = (
        search_res["retrieved_chunks"][0]
    )

    content = top_chunk.get(
        "content",
        "",
    )

    simplified_explanation = (
        f"**Simple Intuition for '{topic}':**\n"
        f"Think of '{topic}' as a core rule explained "
        f"in your lecture: "
        f"*\"{content[:200]}...\"*\n\n"
        f"**Why it matters in simple terms:**\n"
        f"1. **Core Idea:** It breaks down the problem "
        f"step-by-step so the system learns efficiently.\n"
        f"2. **Everyday Analogy:** Imagine adjusting your "
        f"step size when hiking down a hill—large steps "
        f"at first, then tiny precise steps near the bottom."
    )

    return {
        "topic": topic,
        "explanation": simplified_explanation,
        "citations": search_res["citations"],
        "is_grounded": True,
    }