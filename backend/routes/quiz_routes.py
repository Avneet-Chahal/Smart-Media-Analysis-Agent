from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.db_models import GeneratedQuiz
from backend.models.schemas import QuizRequest, QuizResponse, MCQQuestion
from backend.agent.agent_service import agent_service

router = APIRouter(prefix="/api", tags=["Interactive Practice Quiz"])

@router.post("/generate-mcqs", response_model=QuizResponse, summary="Generate Grounded MCQs", description="Generates multiple-choice practice questions with answer explanations and citations.")
@router.post("/agent/quiz", response_model=QuizResponse, summary="Generate Practice Quiz (Alias)", include_in_schema=False)
def create_quiz(request: QuizRequest, db: Session = Depends(get_db)):
    try:
        data = agent_service.generate_quiz(
            db=db,
            document_id=request.document_id,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        return QuizResponse(
            quiz_id=data["quiz_id"],
            document_id=data["document_id"],
            title=data["title"],
            difficulty=data["difficulty"],
            questions=[MCQQuestion(**q) for q in data["questions"]]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/quiz/{document_id}", response_model=List[QuizResponse], summary="List Past Quizzes", description="Retrieves previous generated quizzes for a document.")
@router.get("/quiz/{document_id}", response_model=List[QuizResponse], include_in_schema=False)
def get_quizzes(document_id: str, db: Session = Depends(get_db)):
    quizzes = db.query(GeneratedQuiz).filter(GeneratedQuiz.document_id == document_id).order_by(GeneratedQuiz.created_at.desc()).all()
    return [
        QuizResponse(
            quiz_id=q.id,
            document_id=q.document_id,
            title=q.title,
            difficulty=q.difficulty,
            questions=[MCQQuestion(**item) for item in q.questions]
        )
        for q in quizzes
    ]

