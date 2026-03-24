"""Follow-Up Service — reduces attrition by detecting inactive users,
sending check-in prompts, and maintaining engagement streaks.

Directly addresses: "attrition and loss of follow-up in mental health treatment"
"""

from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime, timedelta, date


# ─── In-memory fallback stores ───
_followup_store: List[Dict[str, Any]] = []
_streak_store: Dict[str, Dict[str, Any]] = {}
_last_active: Dict[str, str] = {}

# ─── Check-in message templates ───
CHECKIN_TEMPLATES = {
    "1_day": "Hey! 👋 We noticed you haven't checked in today. How are you feeling? Even a quick mood log helps track your progress.",
    "2_days": "It's been 2 days since your last visit. We're here for you — would you like to talk about how things have been?",
    "3_days": "We've missed you! 💚 It's been 3 days. Remember, consistent check-ins help us support you better. How are you doing today?",
    "7_days": "It's been a week since we last heard from you. We hope you're doing okay. Your well-being matters — come say hi when you're ready. 🌿",
    "14_days": "It's been 2 weeks. We're still here, and we care about your journey. Even a small check-in can make a big difference. 💙",
}

RECOMMENDATION_TEMPLATES = {
    "stress": "You mentioned feeling stressed recently. Would you like to try a guided breathing exercise? 🧘",
    "sad": "Last time we talked, you were feeling down. I have some mood-lifting activities that might help. Want to try one?",
    "anxious": "Based on your recent mood logs, anxiety has been high. Would you like to try the 5-4-3-2-1 grounding technique?",
    "improving": "Great news — your mood has been trending up! ✨ Keep up the positive momentum. Want to set a wellness goal?",
    "streak": "🔥 You're on a {streak}-day streak! Consistency is key to mental wellness. Keep going!",
}


def update_last_active(user_id: str) -> None:
    """Update the last active timestamp for a user."""
    now = datetime.utcnow().isoformat()
    _last_active[user_id] = now
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("profiles").update({"last_active_at": now}).eq("id", user_id).execute()
    except Exception:
        pass


def update_streak(user_id: str) -> Dict[str, Any]:
    """Update the user's activity streak on daily check-in."""
    today = date.today()

    # Get current streak data
    streak_data = _streak_store.get(user_id, {
        "current_streak": 0, "longest_streak": 0,
        "last_checkin_date": None, "total_checkins": 0,
    })

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = sb.table("activity_streaks").select("*").eq("user_id", user_id).execute()
        if result.data:
            streak_data = result.data[0]
    except Exception:
        pass

    last_date = streak_data.get("last_checkin_date")
    if last_date:
        if isinstance(last_date, str):
            last_date = date.fromisoformat(last_date)
        diff = (today - last_date).days
        if diff == 1:
            streak_data["current_streak"] = streak_data.get("current_streak", 0) + 1
        elif diff > 1:
            streak_data["current_streak"] = 1
        # Same day — no change
    else:
        streak_data["current_streak"] = 1

    streak_data["last_checkin_date"] = today.isoformat()
    streak_data["total_checkins"] = streak_data.get("total_checkins", 0) + 1
    if streak_data["current_streak"] > streak_data.get("longest_streak", 0):
        streak_data["longest_streak"] = streak_data["current_streak"]

    _streak_store[user_id] = streak_data

    # Persist to DB
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        record = {
            "user_id": user_id,
            "current_streak": streak_data["current_streak"],
            "longest_streak": streak_data["longest_streak"],
            "last_checkin_date": streak_data["last_checkin_date"],
            "total_checkins": streak_data["total_checkins"],
            "updated_at": datetime.utcnow().isoformat(),
        }
        sb.table("activity_streaks").upsert(record, on_conflict="user_id").execute()
    except Exception:
        pass

    return streak_data


def get_streak(user_id: str) -> Dict[str, Any]:
    """Get the user's current streak data."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = sb.table("activity_streaks").select("*").eq("user_id", user_id).execute()
        if result.data:
            return result.data[0]
    except Exception:
        pass
    return _streak_store.get(user_id, {
        "current_streak": 0, "longest_streak": 0,
        "last_checkin_date": None, "total_checkins": 0,
    })


def generate_followup(user_id: str, last_mood: str = "", mood_trend: str = "") -> Dict[str, Any] | None:
    """Generate a follow-up message based on user inactivity and history.
    
    This is the core anti-attrition mechanism.
    """
    now = datetime.utcnow()

    # Determine days since last activity
    last_active_str = _last_active.get(user_id)
    days_inactive = 0

    if not last_active_str:
        try:
            from services.supabase_client import get_supabase  # type: ignore
            sb = get_supabase()
            result = sb.table("profiles").select("last_active_at").eq("id", user_id).execute()
            if result.data and result.data[0].get("last_active_at"):
                last_active_str = result.data[0]["last_active_at"]
        except Exception:
            pass

    if last_active_str:
        try:
            last_dt = datetime.fromisoformat(last_active_str.replace("Z", "+00:00").replace("+00:00", ""))
            days_inactive = (now - last_dt).days
        except Exception:
            days_inactive = 0

    # Generate appropriate message
    followup: Dict[str, Any] | None = None

    if days_inactive >= 14:
        followup = {"type": "check_in", "priority": "high", "message": CHECKIN_TEMPLATES["14_days"], "days_inactive": days_inactive}
    elif days_inactive >= 7:
        followup = {"type": "check_in", "priority": "high", "message": CHECKIN_TEMPLATES["7_days"], "days_inactive": days_inactive}
    elif days_inactive >= 3:
        followup = {"type": "check_in", "priority": "normal", "message": CHECKIN_TEMPLATES["3_days"], "days_inactive": days_inactive}
    elif days_inactive >= 2:
        followup = {"type": "check_in", "priority": "normal", "message": CHECKIN_TEMPLATES["2_days"], "days_inactive": days_inactive}
    elif days_inactive >= 1:
        followup = {"type": "reminder", "priority": "low", "message": CHECKIN_TEMPLATES["1_day"], "days_inactive": days_inactive}

    # Add personalized recommendation based on last mood
    if last_mood and last_mood in RECOMMENDATION_TEMPLATES:
        rec = {"type": "recommendation", "priority": "normal", "message": RECOMMENDATION_TEMPLATES[last_mood]}
        if followup:
            followup["recommendation"] = rec["message"]
        else:
            followup = rec

    # Streak-based encouragement
    streak = get_streak(user_id)
    if streak.get("current_streak", 0) >= 3 and not followup:
        msg = RECOMMENDATION_TEMPLATES["streak"].format(streak=streak["current_streak"])
        followup = {"type": "streak", "priority": "low", "message": msg, "streak": streak["current_streak"]}

    if followup:
        followup["created_at"] = now.isoformat()
        # Save to DB
        try:
            from services.supabase_client import get_supabase  # type: ignore
            sb = get_supabase()
            sb.table("follow_ups").insert({
                "user_id": user_id,
                "type": followup.get("type", "check_in"),
                "message": followup["message"],
                "priority": followup.get("priority", "normal"),
            }).execute()
        except Exception:
            _followup_store.append({**followup, "user_id": user_id})  # type: ignore

    return followup


def get_pending_followups(user_id: str) -> List[Dict[str, Any]]:
    """Get all unread follow-up messages for a user."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("follow_ups")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "pending")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        return result.data
    except Exception:
        return [f for f in _followup_store if f.get("user_id") == user_id]


def mark_followup_read(followup_id: int) -> bool:
    """Mark a follow-up as read."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("follow_ups").update({
            "status": "read",
            "read_at": datetime.utcnow().isoformat(),
        }).eq("id", followup_id).execute()
        return True
    except Exception:
        return False
