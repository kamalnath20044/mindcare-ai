"""Follow-Up Router — endpoints for check-in system and engagement streaks."""

from fastapi import APIRouter, Query  # type: ignore
from services.followup_service import (  # type: ignore
    generate_followup, get_pending_followups, mark_followup_read,
    update_streak, get_streak, update_last_active,
)

router = APIRouter(prefix="/api/followup", tags=["follow-up"])


@router.get("")
async def get_followups(user_id: str = Query(...)):
    """Get pending follow-up messages for a user."""
    followups = get_pending_followups(user_id)
    generated = generate_followup(user_id)
    return {"followups": followups, "new": generated}


@router.post("/checkin")
async def check_in(user_id: str = Query(...)):
    """Record a user check-in and update streak."""
    update_last_active(user_id)
    streak_data = update_streak(user_id)
    return {"status": "ok", "streak": streak_data}


@router.get("/streak")
async def get_user_streak(user_id: str = Query(...)):
    """Get the user's activity streak."""
    return get_streak(user_id)


@router.put("/read/{followup_id}")
async def read_followup(followup_id: int):
    """Mark a follow-up as read."""
    success = mark_followup_read(followup_id)
    return {"status": "ok" if success else "error"}
