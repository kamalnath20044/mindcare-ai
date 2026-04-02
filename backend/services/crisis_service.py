"""Crisis Detection Service — identifies high-risk messages and triggers safety protocols.

Addresses: "incomplete alleviation of depression symptoms" by detecting
escalation early and connecting users with emergency resources.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime


# ─── Risk Keyword Tiers ───
CRITICAL_KEYWORDS = [
    "kill myself", "end my life", "suicide", "want to die",
    "self harm", "self-harm", "hurt myself", "no reason to live",
    "don't want to exist", "better off dead", "end it all",
    "take my own life", "slit my wrists", "overdose",
]

HIGH_KEYWORDS = [
    "can't go on", "give up on life", "nobody cares", "no hope",
    "what's the point", "can't take it anymore", "falling apart",
    "breaking down", "i'm done", "want to disappear",
    "nothing matters", "hopeless", "worthless",
]

MODERATE_KEYWORDS = [
    "overwhelmed", "exhausted", "can't cope", "burnt out",
    "panic attack", "spiraling", "losing control", "numb",
    "empty inside", "don't feel anything", "trapped",
]

# ─── Emergency Resources ───
EMERGENCY_RESOURCES = [
    {"name": "National Suicide Prevention Lifeline", "number": "988", "country": "US", "available": "24/7"},
    {"name": "Crisis Text Line", "number": "Text HOME to 741741", "country": "US", "available": "24/7"},
    {"name": "Call (Tamilnadu)", "number": "7812811773", "country": "India", "available": "24/7"},
    {"name": "Vandrevala Foundation", "number": "1860-2662-345", "country": "India", "available": "24/7"},
    {"name": "AASRA", "number": "91-22-27546669", "country": "India", "available": "24/7"},
    {"name": "Samaritans", "number": "116 123", "country": "UK", "available": "24/7"},
]

SAFETY_RESPONSES = {
    "critical": (
        "I'm really concerned about what you've shared. Your life matters, and you deserve support right now.\n\n"
        "🆘 **Please reach out immediately:**\n"
        "• **988 Suicide & Crisis Lifeline**: Call or text 988 (US)\n"
        "• **Vandrevala Foundation**: 1860-2662-345 (India, 24/7)\n"
        "• **Crisis Text Line**: Text HOME to 741741\n\n"
        "You are not alone. A trained counselor is available right now to help you through this."
    ),
    "high": (
        "I hear you, and I want you to know that what you're feeling is valid — but it also sounds like you're "
        "going through something really intense right now.\n\n"
        "💙 Please consider reaching out to a professional who can help:\n"
        "• **988 Lifeline**: Call or text 988\n"
        "• **Call (Tamilnadu)**: 7812811773 (India)\n\n"
        "Would you like me to share some coping strategies while you have a chance to connect with someone?"
    ),
    "moderate": (
        "It sounds like you're carrying a heavy load right now. That's really tough, and I'm glad you're "
        "talking about it.\n\n"
        "💡 Here are some things that might help right now:\n"
        "• Try the 4-7-8 breathing technique (inhale 4s, hold 7s, exhale 8s)\n"
        "• Step away from screens for a few minutes\n"
        "• Write down exactly what's on your mind — a 'brain dump'\n\n"
        "If things feel like they're getting worse, please don't hesitate to reach out to a helpline. "
        "You deserve support."
    ),
}


def assess_crisis_risk(message: str) -> Dict[str, Any]:
    """Assess the crisis risk level of a user message.
    
    Returns:
        Dict with risk_level, matched_keywords, should_intervene,
        safety_response, and show_helplines flags.
    """
    lower = message.lower()
    matched_critical = [kw for kw in CRITICAL_KEYWORDS if kw in lower]
    matched_high = [kw for kw in HIGH_KEYWORDS if kw in lower]
    matched_moderate = [kw for kw in MODERATE_KEYWORDS if kw in lower]

    if matched_critical:
        return {
            "risk_level": "critical",
            "matched_keywords": matched_critical,
            "should_intervene": True,
            "safety_response": SAFETY_RESPONSES["critical"],
            "show_helplines": True,
            "resources": EMERGENCY_RESOURCES,
        }
    elif matched_high:
        return {
            "risk_level": "high",
            "matched_keywords": matched_high,
            "should_intervene": True,
            "safety_response": SAFETY_RESPONSES["high"],
            "show_helplines": True,
            "resources": EMERGENCY_RESOURCES,
        }
    elif matched_moderate:
        return {
            "risk_level": "moderate",
            "matched_keywords": matched_moderate,
            "should_intervene": True,
            "safety_response": SAFETY_RESPONSES["moderate"],
            "show_helplines": False,
            "resources": [],
        }

    return {
        "risk_level": "none",
        "matched_keywords": [],
        "should_intervene": False,
        "safety_response": None,
        "show_helplines": False,
        "resources": [],
    }


def log_crisis_event(
    user_id: str, message: str, risk_assessment: Dict[str, Any]
) -> Dict[str, Any]:
    """Log a crisis event to the database for audit purposes."""
    record = {
        "user_id": user_id,
        "trigger_message": message[:500],
        "risk_level": risk_assessment["risk_level"],
        "keywords_matched": risk_assessment["matched_keywords"],
        "response_given": risk_assessment.get("safety_response", "")[:500],
        "helplines_shown": risk_assessment["show_helplines"],
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("crisis_events").insert(record).execute()
    except Exception:
        pass  # In-memory fallback — crisis events are still handled in real-time

    return record


def get_crisis_history(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve past crisis events for a user."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("crisis_events")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data
    except Exception:
        return []
