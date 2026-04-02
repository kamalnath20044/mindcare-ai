"""Session Summary Service — generates and stores AI session summaries.

After each chat session, generates a concise summary capturing key topics,
emotional state, techniques used, and risk level. Summaries are injected
into the next conversation for continuity.
"""

from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime, timedelta


def generate_session_summary(
    user_id: str,
    messages: List[Dict[str, Any]],
    session_start: str = "",
    session_end: str = "",
) -> Dict[str, Any]:
    """Generate a summary from a list of chat messages.
    
    Uses keyword analysis to extract topics, emotions, and techniques.
    Optionally uses GPT for more nuanced summaries when available.
    """
    if not messages:
        return {"summary": "No messages in this session.", "key_topics": [], "dominant_emotion": "neutral"}

    user_messages = [m for m in messages if m.get("role") == "user"]
    bot_messages = [m for m in messages if m.get("role") in ("assistant", "ai")]

    # Extract topics from user messages
    all_user_text = " ".join(m.get("content", "")[:200] for m in user_messages).lower()
    topics = _extract_topics(all_user_text)

    # Determine dominant emotion
    emotions = [m.get("metadata", {}).get("emotion", "") or m.get("emotion", "") for m in messages if m.get("metadata") or m.get("emotion")]
    dominant_emotion = _get_dominant(emotions) if emotions else "neutral"

    # Determine sentiment trend
    sentiments = [m.get("metadata", {}).get("sentiment", "") or m.get("sentiment", "") for m in messages if m.get("metadata") or m.get("sentiment")]
    sentiment_trend = _analyze_sentiment_trend(sentiments)

    # Extract techniques mentioned
    all_bot_text = " ".join(m.get("content", "")[:300] for m in bot_messages).lower()
    techniques = _extract_techniques(all_bot_text)

    # Try GPT-based summary
    summary_text = _generate_gpt_summary(user_messages, topics, dominant_emotion)
    if not summary_text:
        summary_text = _generate_fallback_summary(user_messages, topics, dominant_emotion, sentiment_trend)

    # Detect risk level
    risk_level = "none"
    for msg in user_messages:
        content = msg.get("content", "").lower()
        if any(kw in content for kw in ["suicide", "kill myself", "want to die", "end my life"]):
            risk_level = "critical"
            break
        elif any(kw in content for kw in ["hopeless", "worthless", "can't go on", "no point"]):
            risk_level = "high"

    now = datetime.utcnow().isoformat()
    summary_record = {
        "user_id": user_id,
        "session_start": session_start or now,
        "session_end": session_end or now,
        "message_count": len(messages),
        "summary": summary_text,
        "key_topics": topics,
        "dominant_emotion": dominant_emotion,
        "sentiment_trend": sentiment_trend,
        "techniques_used": techniques,
        "risk_level": risk_level,
    }

    # Persist to database
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("session_summaries").insert(summary_record).execute()
    except Exception:
        pass

    return summary_record


def get_session_summaries(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent session summaries for a user."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("session_summaries")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data
    except Exception:
        return []


def get_last_session_context(user_id: str) -> str:
    """Get the last session summary as context for the next conversation."""
    summaries = get_session_summaries(user_id, limit=2)
    if not summaries:
        return ""

    parts = []
    for i, s in enumerate(summaries):
        label = "Last session" if i == 0 else "Previous session"
        parts.append(
            f"{label}: {s.get('summary', 'N/A')} "
            f"(Mood: {s.get('dominant_emotion', 'N/A')}, "
            f"Trend: {s.get('sentiment_trend', 'N/A')}, "
            f"Topics: {', '.join(s.get('key_topics', [])[:3])})"
        )

    return "\n".join(parts)


# ─── Internal Helpers ───

TOPIC_KEYWORDS = {
    "work": ["work", "job", "career", "boss", "office", "deadline", "colleague", "promotion"],
    "relationships": ["relationship", "partner", "girlfriend", "boyfriend", "wife", "husband", "family", "friend", "dating"],
    "sleep": ["sleep", "insomnia", "tired", "exhausted", "rest", "nightmare"],
    "academic": ["school", "college", "university", "exam", "grade", "study", "homework", "class"],
    "health": ["health", "sick", "pain", "illness", "doctor", "medication", "medicine"],
    "finances": ["money", "debt", "financial", "bills", "broke", "afford", "salary"],
    "self-esteem": ["confidence", "self-esteem", "worthless", "ugly", "failure", "imposter"],
    "grief": ["loss", "death", "died", "grief", "mourning", "miss", "passed away"],
    "loneliness": ["lonely", "alone", "isolated", "disconnected", "no friends"],
    "trauma": ["trauma", "abuse", "assault", "ptsd", "flashback"],
}

TECHNIQUE_KEYWORDS = {
    "deep breathing": ["breathing", "breathe", "inhale", "exhale", "4-7-8", "box breathing"],
    "grounding": ["grounding", "5-4-3-2-1", "anchor", "present moment"],
    "cognitive restructuring": ["reframe", "restructuring", "thought record", "cognitive distortion", "evidence"],
    "behavioral activation": ["behavioral activation", "small step", "activity", "action"],
    "mindfulness": ["mindfulness", "mindful", "meditation", "body scan"],
    "gratitude": ["grateful", "gratitude", "thankful", "appreciate"],
    "journaling": ["journal", "write down", "writing", "log"],
}


def _extract_topics(text: str) -> List[str]:
    """Extract discussion topics from text."""
    found = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            found.append(topic)
    return found[:5]


def _extract_techniques(text: str) -> List[str]:
    """Extract CBT techniques mentioned in bot responses."""
    found = []
    for technique, keywords in TECHNIQUE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            found.append(technique)
    return found


def _get_dominant(items: List[str]) -> str:
    """Get the most common item from a list."""
    if not items:
        return "neutral"
    from collections import Counter
    counts = Counter(item.lower() for item in items if item)
    return counts.most_common(1)[0][0] if counts else "neutral"


def _analyze_sentiment_trend(sentiments: List[str]) -> str:
    """Analyze sentiment list for trend."""
    if not sentiments:
        return "unknown"
    pos = sum(1 for s in sentiments if s == "POSITIVE")
    neg = sum(1 for s in sentiments if s == "NEGATIVE")
    total = len(sentiments)
    if total == 0:
        return "unknown"
    if neg / total > 0.6:
        return "declining"
    elif pos / total > 0.6:
        return "improving"
    return "stable"


def _generate_gpt_summary(user_messages: List[Dict], topics: List[str], emotion: str) -> str | None:
    """Try to generate a GPT-based session summary."""
    try:
        from services.gpt_service import is_gpt_available  # type: ignore
        if not is_gpt_available():
            return None

        from config import OPENAI_API_KEY  # type: ignore
        if not OPENAI_API_KEY:
            return None

        from langchain_openai import ChatOpenAI  # type: ignore
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, max_tokens=150, api_key=OPENAI_API_KEY)

        user_text = " | ".join(m.get("content", "")[:100] for m in user_messages[:8])
        prompt = (
            f"Summarize this therapy session in 2-3 sentences. Focus on key themes and emotional state.\n"
            f"Topics discussed: {', '.join(topics) if topics else 'general'}\n"
            f"Dominant emotion: {emotion}\n"
            f"User statements: {user_text}"
        )
        result = llm.invoke(prompt)
        return result.content.strip() if hasattr(result, "content") else None
    except Exception:
        return None


def _generate_fallback_summary(
    user_messages: List[Dict], topics: List[str], emotion: str, sentiment: str
) -> str:
    """Generate a summary without GPT."""
    msg_count = len(user_messages)
    topic_str = ", ".join(topics[:3]) if topics else "general wellness"

    sentiment_desc = {
        "improving": "showed improvement over the course of the session",
        "declining": "expressed increasing distress during the session",
        "stable": "maintained a consistent emotional state",
        "unknown": "discussed various topics",
    }

    return (
        f"Session with {msg_count} user message(s). "
        f"The user discussed {topic_str} and {sentiment_desc.get(sentiment, 'engaged in conversation')}. "
        f"Primary emotion detected: {emotion}."
    )
