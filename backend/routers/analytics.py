"""Analytics Router — dashboard data endpoints."""

from fastapi import APIRouter, Query  # type: ignore
from services.analytics_service import (  # type: ignore
    get_dashboard_stats, get_mood_analytics, get_emotion_analytics, get_chat_analytics,
)
from services.personalization import get_personalized_recommendations, get_personalized_greeting  # type: ignore

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def dashboard_stats(user_id: str = Query(...)):
    """Get comprehensive dashboard statistics."""
    return get_dashboard_stats(user_id)


@router.get("/mood")
async def mood_analytics(user_id: str = Query(...), days: int = Query(default=30)):
    """Get detailed mood analytics with trends and insights."""
    return get_mood_analytics(user_id, days)


@router.get("/emotions")
async def emotion_analytics(user_id: str = Query(...), days: int = Query(default=30)):
    """Get emotion detection analytics."""
    return get_emotion_analytics(user_id, days)


@router.get("/chat")
async def chat_analytics(user_id: str = Query(...)):
    """Get chat usage analytics."""
    return get_chat_analytics(user_id)


@router.get("/recommendations")
async def personalized_recommendations(user_id: str = Query(...), mood: str = Query(default="")):
    """Get AI-personalized coping recommendations."""
    return get_personalized_recommendations(user_id, mood)


@router.get("/greeting")
async def personalized_greeting(user_id: str = Query(...), name: str = Query(default="")):
    """Get a personalized greeting based on user history."""
    return {"greeting": get_personalized_greeting(user_id, name)}
