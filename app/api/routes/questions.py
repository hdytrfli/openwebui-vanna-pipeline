from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.models.responses import QuestionListResponse, QuestionHistoryResponse
from app.services.vanna_service import vanna
from app.services.cache_service import get_cache
from app.api.dependencies import requires_cache

router = APIRouter(prefix="/api", tags=["questions"])


@router.get("/generate_questions", response_model=QuestionListResponse)
async def generate_questions():
    """Generate sample questions based on the database schema."""
    try:
        questions = vanna.generate_questions()
        return QuestionListResponse(
            questions=questions, header="Here are some questions you can ask:"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate_followup_questions", response_model=QuestionListResponse)
async def generate_followup_questions(
    cache_data: dict = Depends(requires_cache(["df", "question", "sql"]))
):
    """Generate follow-up questions based on previous query results."""
    try:
        cache = get_cache()
        df = cache_data["df"]
        question = cache_data["question"]
        sql = cache_data["sql"]
        id = cache_data["id"]

        followup_questions = vanna.generate_followup_questions(
            question=question, sql=sql, df=df
        )
        cache.set(id=id, field="followup_questions", value=followup_questions)

        return QuestionListResponse(
            id=id,
            questions=followup_questions,
            header="Here are some followup questions you can ask:",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_question_history", response_model=QuestionHistoryResponse)
async def get_question_history():
    """Get history of all asked questions."""
    try:
        cache = get_cache()
        questions = cache.get_all(field_list=["question"])
        return QuestionHistoryResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
