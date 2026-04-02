"""Chat router — Context-aware AI Therapist with crisis detection, session memory, & homework loop."""

from fastapi import APIRouter  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import Optional, Dict, Any, List
from services.nlp_service import analyze_sentiment, generate_response, detect_distress, analyze_emotion_from_text  # type: ignore
from services.chat_memory import chat_memory  # type: ignore
from services.smart_alerts import generate_alerts, get_recommendations  # type: ignore
from services.crisis_service import assess_crisis_risk, log_crisis_event  # type: ignore
from services.personalization import build_chat_context  # type: ignore
from services.followup_service import update_last_active, update_streak  # type: ignore
from middleware.sanitizer import sanitize_string  # type: ignore

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Track message counts per user for session summary triggers
_session_msg_count: Dict[str, int] = {}
SESSION_SUMMARY_THRESHOLD = 10  # Generate summary every N user messages


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
    homework: Optional[Dict[str, Any]] = None


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    user_id = req.user_id or "anonymous"
    user_message = sanitize_string(req.message)

    # ─── 1. Crisis Detection (FIRST — safety is top priority) ───
    crisis = assess_crisis_risk(user_message)
    if crisis["should_intervene"] and crisis["risk_level"] in ("critical", "high"):
        log_crisis_event(user_id, user_message, crisis)
        
        chat_memory.add_message(user_id, "user", user_message, {"crisis": True})
        chat_memory.add_message(user_id, "assistant", crisis["safety_response"])
        _persist_messages(user_id, user_message, crisis["safety_response"], "NEGATIVE", "Distressed", True)

        # Trigger therapist alert for critical crises
        if crisis["risk_level"] == "critical":
            try:
                from services.therapist_alert_service import send_alert  # type: ignore
                send_alert(user_id, "crisis", "critical", f"Crisis message detected: {user_message[:200]}")
            except Exception:
                pass

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
    sentiment = analyze_sentiment(user_message)
    emotion = analyze_emotion_from_text(user_message)
    distress = detect_distress(user_message)

    # ─── 3. Context Building (personalization + memory + session summaries + homework) ───
    memory_context = chat_memory.get_context_summary(user_id)
    personalization_context = build_chat_context(user_id)

    # Add session summary context
    session_context = ""
    try:
        from services.session_summary_service import get_last_session_context  # type: ignore
        session_context = get_last_session_context(user_id)
    except Exception:
        pass

    # Add homework context
    homework_context = ""
    try:
        from services.homework_service import get_pending_homework_context  # type: ignore
        homework_context = get_pending_homework_context(user_id)
    except Exception:
        pass

    full_context = "\n".join(filter(None, [personalization_context, memory_context, session_context, homework_context])).strip()
    has_context = bool(full_context)

    # ─── 4. Store user message ───
    chat_memory.add_message(user_id, "user", user_message, {
        "sentiment": sentiment["label"],
        "emotion": emotion["emotion"],
    })

    # ─── 5. Generate response ───
    reply = generate_response(
        user_message,
        sentiment=sentiment,
        context=full_context,
        therapist_mode=req.therapist_mode,
    )

    # ─── 6. Handle moderate crisis ───
    if crisis["should_intervene"] and crisis["risk_level"] == "moderate":
        reply = crisis["safety_response"] + "\n\n---\n\n" + reply
        log_crisis_event(user_id, user_message, crisis)

    # ─── 7. Store assistant response ───
    chat_memory.add_message(user_id, "assistant", reply)

    # ─── 8. Smart alerts ───
    mood_trend = chat_memory.get_mood_trend(user_id)
    alerts = generate_alerts(
        mood_history=[],
        sentiment_trend=mood_trend.get("trend", "unknown"),
        latest_emotion=emotion["emotion"],
        latest_message=user_message,
    )

    # ─── 9. Update activity tracking ───
    update_last_active(user_id)

    # ─── 10. Persist to database ───
    _persist_messages(user_id, user_message, reply, sentiment["label"], emotion["emotion"], req.therapist_mode)

    # ─── 11. Session summary + homework trigger ───
    homework_assignment = None
    _session_msg_count[user_id] = _session_msg_count.get(user_id, 0) + 1
    if _session_msg_count[user_id] >= SESSION_SUMMARY_THRESHOLD:
        _session_msg_count[user_id] = 0
        _trigger_session_summary(user_id)
        homework_assignment = _trigger_homework(user_id, emotion["emotion"])

    return ChatResponse(
        reply=reply,
        sentiment=sentiment,
        emotion=emotion,
        distress_detected=distress,
        alerts=alerts,
        context_aware=has_context,
        crisis={"risk_level": crisis["risk_level"], "show_helplines": crisis["show_helplines"],
                 "resources": crisis.get("resources", [])} if crisis["should_intervene"] else None,
        homework=homework_assignment,
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


def _trigger_session_summary(user_id: str) -> None:
    """Generate a session summary from recent messages."""
    try:
        from services.session_summary_service import generate_session_summary  # type: ignore
        history = chat_memory.get_history(user_id, limit=15)
        generate_session_summary(user_id, history)
    except Exception:
        pass


def _trigger_homework(user_id: str, emotion: str) -> Optional[Dict[str, Any]]:
    """Assign homework after a meaningful session."""
    try:
        from services.homework_service import assign_homework  # type: ignore
        return assign_homework(user_id, emotion=emotion)
    except Exception:
        return None


@router.get("/history")
async def get_chat_history(user_id: str = "anonymous"):
    """Get recent conversation history."""
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


@router.get("/sessions")
async def get_session_history(user_id: str = "anonymous", limit: int = 5):
    """Get session summaries for a user."""
    try:
        from services.session_summary_service import get_session_summaries  # type: ignore
        return {"sessions": get_session_summaries(user_id, limit)}
    except Exception:
        return {"sessions": []}
