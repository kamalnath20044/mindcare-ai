"""Mood tracker router — CRUD for daily mood entries."""

from fastapi import APIRouter, Query  # type: ignore
from pydantic import BaseModel  # type: ignore
from datetime import datetime
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/api/mood", tags=["mood"])

# In-memory fallback when Supabase is not configured
_mood_store: List[Dict[str, Any]] = []


class MoodEntry(BaseModel):
    user_id: str
    mood: str  # e.g. "happy", "sad", "anxious", "angry", "neutral"
    note: Optional[str] = None


@router.post("")
async def log_mood(entry: MoodEntry):
    record = {
        "user_id": entry.user_id,
        "mood": entry.mood,
        "note": entry.note,
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("mood_entries").insert(record).execute()
    except Exception:
        _mood_store.append(record)

    return {"status": "ok", "entry": record}


@router.get("")
async def get_moods(
    user_id: str = Query(...),
    range: str = Query(default="week", pattern="^(week|month|all)$"),
):
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        query = sb.table("mood_entries").select("*").eq("user_id", user_id).order("created_at", desc=True)

        if range == "week":
            query = query.limit(7)
        elif range == "month":
            query = query.limit(30)

        result = query.execute()
        return {"entries": result.data}
    except Exception:
        # Fallback to in-memory
        entries = [e for e in _mood_store if e["user_id"] == user_id]
        if range == "week":
            entries = list(entries[-7:])  # type: ignore
        elif range == "month":
            entries = list(entries[-30:])  # type: ignore
        return {"entries": entries}

