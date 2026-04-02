"""Assessment Router — PHQ-9 and GAD-7 endpoints."""

from fastapi import APIRouter, Query, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import List
from services.assessment_service import (  # type: ignore
    save_phq9, save_gad7, get_phq9_history, get_gad7_history,
    get_assessment_trends, get_questions,
)

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


class AssessmentSubmit(BaseModel):
    user_id: str
    answers: List[int]


@router.get("/questions/{assessment_type}")
async def get_assessment_questions(assessment_type: str):
    """Get questions for PHQ-9 or GAD-7."""
    try:
        return get_questions(assessment_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/phq9")
async def submit_phq9(req: AssessmentSubmit):
    """Submit a PHQ-9 assessment."""
    try:
        result = save_phq9(req.user_id, req.answers)
        return {"status": "ok", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/gad7")
async def submit_gad7(req: AssessmentSubmit):
    """Submit a GAD-7 assessment."""
    try:
        result = save_gad7(req.user_id, req.answers)
        return {"status": "ok", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/phq9/history")
async def phq9_history(user_id: str = Query(...), limit: int = Query(default=10)):
    """Get PHQ-9 assessment history."""
    return {"entries": get_phq9_history(user_id, limit)}


@router.get("/gad7/history")
async def gad7_history(user_id: str = Query(...), limit: int = Query(default=10)):
    """Get GAD-7 assessment history."""
    return {"entries": get_gad7_history(user_id, limit)}


@router.get("/trends")
async def assessment_trends(user_id: str = Query(...)):
    """Get combined assessment trends."""
    return get_assessment_trends(user_id)
