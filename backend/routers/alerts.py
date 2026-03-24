"""Smart Alerts router — personalized alerts and recommendations."""

from fastapi import APIRouter, Query  # type: ignore
from typing import Optional
from services.smart_alerts import generate_alerts, get_recommendations, RECOMMENDATIONS  # type: ignore
from services.chat_memory import chat_memory  # type: ignore

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
async def get_alerts(user_id: str = Query(default="anonymous")):
    """Get personalized smart alerts for a user."""
    mood_trend = chat_memory.get_mood_trend(user_id)

    # Try to get mood history from Supabase
    mood_history = []
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = sb.table("mood_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
        mood_history = result.data or []
    except Exception:
        pass

    alerts = generate_alerts(
        mood_history=mood_history,
        sentiment_trend=mood_trend.get("trend", "unknown"),
    )

    return {
        "alerts": alerts,
        "mood_trend": mood_trend,
        "recommendation_count": len(alerts),
    }


@router.get("/recommendations")
async def get_all_recommendations():
    """Get all available recommendation categories."""
    return {"recommendations": RECOMMENDATIONS}


@router.get("/recommendations/{key}")
async def get_recommendation_by_key(key: str):
    """Get recommendations by category key."""
    rec = get_recommendations(key)
    return {"recommendation": rec}
