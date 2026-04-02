"""Homework Router — CBT homework loop endpoints."""

from fastapi import APIRouter, Query  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import Optional
from services.homework_service import (  # type: ignore
    assign_homework, get_homework, complete_homework,
    skip_homework, get_homework_stats,
)

router = APIRouter(prefix="/api/homework", tags=["homework"])


class AssignRequest(BaseModel):
    user_id: str
    category: Optional[str] = ""
    emotion: Optional[str] = ""
    difficulty: Optional[str] = "easy"


class CompleteRequest(BaseModel):
    homework_id: int
    completion_note: Optional[str] = ""
    rating: Optional[int] = 3


@router.post("/assign")
async def assign(req: AssignRequest):
    """Assign a new homework task."""
    result = assign_homework(req.user_id, req.category or "", req.emotion or "", req.difficulty or "easy")
    return {"status": "ok", "homework": result}


@router.get("")
async def list_homework(user_id: str = Query(...), status: str = Query(default="")):
    """Get homework assignments."""
    return {"homework": get_homework(user_id, status)}


@router.post("/complete")
async def complete(req: CompleteRequest):
    """Mark homework as completed."""
    return complete_homework(req.homework_id, req.completion_note or "", req.rating or 3)


@router.post("/skip/{homework_id}")
async def skip(homework_id: int):
    """Skip a homework assignment."""
    return skip_homework(homework_id)


@router.get("/stats")
async def stats(user_id: str = Query(...)):
    """Get homework completion statistics."""
    return get_homework_stats(user_id)
