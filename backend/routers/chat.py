"""Chat router — Context-aware AI Therapist with crisis detection & personalization."""

from fastapi import APIRouter  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import Optional, Dict, Any, List
from services.nlp_service import analyze_sentiment, generate_response, detect_distress, analyze_emotion_from_text  # type: ignore
from services.chat_memory import chat_memory  # type: ignore
from services.smart_alerts import generate_alerts, get_recommendations  # type: ignore
from services.crisis_service import assess_crisis_risk, log_crisis_event  # type: ignore
from services.personalization import build_chat_context  # type: ignore
from services.followup_service import update_last_active, update_streak  # type: ignore

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    therapist_mode: bool = True


class ChatResponse(BaseModel):
    reply: str
    sentiment: Dict[str, Any]
    emotion: Dict[str, Any]
    distress_detected: bool
    alerts: List[Dict[str, Any]]
    context_aware: bool
    crisis: Optional[Dict[str, Any]] = None


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    user_id = req.user_id or "anonymous"

    # ─── 1. Crisis Detection (FIRST — safety is top priority) ───
    crisis = assess_crisis_risk(req.message)
    if crisis["should_intervene"] and crisis["risk_level"] in ("critical", "high"):
        log_crisis_event(user_id, req.message, crisis)
        
        # Store message in memory even during crisis
        chat_memory.add_message(user_id, "user", req.message, {"crisis": True})
        chat_memory.add_message(user_id, "assistant", crisis["safety_response"])

        # Persist to DB
        _persist_messages(user_id, req.message, crisis["safety_response"], "NEGATIVE", "Distressed", True)

        return ChatResponse(
            reply=crisis["safety_response"],
            sentiment={"label": "NEGATIVE", "score": 0.99},
            emotion={"emotion": "Distressed", "category": "crisis", "intensity": "strong"},
            distress_detected=True,
            alerts=[{"type": "crisis", "priority": "critical", "title": "🆘 Crisis Detected",
                     "message": "Emergency resources have been provided."}],
            context_aware=True,
            crisis={"risk_level": crisis["risk_level"], "show_helplines": crisis["show_helplines"],
                     "resources": crisis.get("resources", [])},
        )  # type: ignore

    # ─── 2. NLP Analysis ───
    sentiment = analyze_sentiment(req.message)
    emotion = analyze_emotion_from_text(req.message)
    distress = detect_distress(req.message)

    # ─── 3. Context Building (personalization) ───
    memory_context = chat_memory.get_context_summary(user_id)
    personalization_context = build_chat_context(user_id)
    full_context = f"{personalization_context}\n{memory_context}".strip()
    has_context = bool(full_context)

    # ─── 4. Store user message ───
    chat_memory.add_message(user_id, "user", req.message, {
        "sentiment": sentiment["label"],
        "emotion": emotion["emotion"],
    })

    # ─── 5. Generate response ───
    reply = generate_response(
        req.message,
        sentiment=sentiment,
        context=full_context,
        therapist_mode=req.therapist_mode,
    )

    # ─── 6. Handle moderate crisis ───
    if crisis["should_intervene"] and crisis["risk_level"] == "moderate":
        reply = crisis["safety_response"] + "\n\n---\n\n" + reply
        log_crisis_event(user_id, req.message, crisis)

    # ─── 7. Store assistant response ───
    chat_memory.add_message(user_id, "assistant", reply)

    # ─── 8. Smart alerts ───
    mood_trend = chat_memory.get_mood_trend(user_id)
    alerts = generate_alerts(
        mood_history=[],
        sentiment_trend=mood_trend.get("trend", "unknown"),
        latest_emotion=emotion["emotion"],
        latest_message=req.message,
    )

    # ─── 9. Update activity tracking ───
    update_last_active(user_id)

    # ─── 10. Persist to database ───
    _persist_messages(user_id, req.message, reply, sentiment["label"], emotion["emotion"], req.therapist_mode)

    return ChatResponse(
        reply=reply,
        sentiment=sentiment,
        emotion=emotion,
        distress_detected=distress,
        alerts=alerts,
        context_aware=has_context,
        crisis={"risk_level": crisis["risk_level"], "show_helplines": crisis["show_helplines"],
                 "resources": crisis.get("resources", [])} if crisis["should_intervene"] else None,
    )  # type: ignore


def _persist_messages(user_id: str, user_msg: str, bot_reply: str, sentiment: str, emotion: str, therapist_mode: bool) -> None:
    """Persist chat messages to Supabase."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        if user_id and user_id != "anonymous":
            sb.table("chat_messages").insert(
                {"user_id": user_id, "role": "user", "content": user_msg,
                 "sentiment": sentiment, "emotion": emotion, "therapist_mode": therapist_mode}
            ).execute()
            sb.table("chat_messages").insert(
                {"user_id": user_id, "role": "assistant", "content": bot_reply,
                 "sentiment": None, "therapist_mode": therapist_mode}
            ).execute()
    except Exception:
        pass


@router.get("/history")
async def get_chat_history(user_id: str = "anonymous"):
    """Get recent conversation history."""
    # Try DB first
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("chat_messages")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .limit(40)
            .execute()
        )
        if result.data:
            return {"history": result.data, "source": "database", "message_count": len(result.data)}
    except Exception:
        pass

    # Fallback to in-memory
    history = chat_memory.get_history(user_id, limit=20)
    mood_trend = chat_memory.get_mood_trend(user_id)
    return {"history": history, "mood_trend": mood_trend, "source": "memory", "message_count": len(history)}


@router.delete("/history")
async def clear_chat_history(user_id: str = "anonymous"):
    """Clear conversation history."""
    chat_memory.clear(user_id)
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("chat_messages").delete().eq("user_id", user_id).execute()
    except Exception:
        pass
    return {"status": "ok", "message": "Chat history cleared"}


@router.get("/recommendations")
async def get_chat_recommendations(key: str = "general_wellness"):
    """Get specific recommendation set."""
    return get_recommendations(key)
