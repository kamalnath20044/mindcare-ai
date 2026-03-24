"""Personalization Engine — generates contextual responses using past chat history.

Addresses: "personalized AI interaction" and "continuous mental health support"
by learning from user patterns and providing tailored recommendations.
"""

from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime, timedelta


# ─── Coping Strategies Database ───
COPING_STRATEGIES = {
    "stress": [
        {"title": "Brain Dump Journaling", "description": "Write everything on your mind for 5 minutes without filtering. It helps externalize overwhelm.", "duration": "5 min", "icon": "📝"},
        {"title": "Progressive Muscle Relaxation", "description": "Tense and release each muscle group from toes to head. Releases physical stress.", "duration": "10 min", "icon": "💪"},
        {"title": "Box Breathing", "description": "Breathe in 4 counts, hold 4, out 4, hold 4. Activates your parasympathetic nervous system.", "duration": "3 min", "icon": "🫁"},
        {"title": "Nature Walk", "description": "Take a 15-minute walk outside. Nature exposure reduces cortisol by up to 21%.", "duration": "15 min", "icon": "🌿"},
    ],
    "sad": [
        {"title": "Gratitude List", "description": "Write 3 things you're grateful for. Shifts focus from what's wrong to what's right.", "duration": "5 min", "icon": "🙏"},
        {"title": "Connect with Someone", "description": "Text or call a friend. Social connection is one of the strongest antidepressants.", "duration": "10 min", "icon": "💬"},
        {"title": "Gentle Movement", "description": "5 minutes of stretching or yoga. Movement releases endorphins even in small doses.", "duration": "5 min", "icon": "🧘"},
        {"title": "Comfort Activity", "description": "Do something that brings you comfort — warm tea, a blanket, calming music.", "duration": "Any", "icon": "☕"},
    ],
    "anxious": [
        {"title": "5-4-3-2-1 Grounding", "description": "Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.", "duration": "3 min", "icon": "🌍"},
        {"title": "4-7-8 Breathing", "description": "Inhale 4s, hold 7s, exhale 8s. Calms your nervous system within 3 cycles.", "duration": "3 min", "icon": "🌬️"},
        {"title": "Worry Time Block", "description": "Schedule 15 min to worry, then tell yourself worries must wait until then.", "duration": "15 min", "icon": "⏰"},
        {"title": "Cold Water Reset", "description": "Splash cold water on your face. Triggers the dive reflex and slows heart rate.", "duration": "1 min", "icon": "💧"},
    ],
    "angry": [
        {"title": "Physical Release", "description": "Do 20 jumping jacks or squeeze a stress ball. Physical release diffuses anger safely.", "duration": "2 min", "icon": "🏃"},
        {"title": "Pause and Count", "description": "Count backwards from 10 slowly. Creates space between trigger and response.", "duration": "1 min", "icon": "🔢"},
        {"title": "Write It Out", "description": "Write an angry letter you'll never send. Externalizes the emotion safely.", "duration": "5 min", "icon": "✍️"},
    ],
    "default": [
        {"title": "Mindful Check-In", "description": "Pause for 2 minutes: How does your body feel? What emotions are present?", "duration": "2 min", "icon": "🧠"},
        {"title": "Digital Detox", "description": "Put your phone down for 30 minutes. Screen breaks improve mood and focus.", "duration": "30 min", "icon": "📱"},
        {"title": "Hydration Break", "description": "Drink a glass of water. Dehydration amplifies anxiety and fatigue.", "duration": "1 min", "icon": "💧"},
    ],
}


def get_user_emotion_profile(user_id: str) -> Dict[str, Any]:
    """Build an emotional profile from the user's history.
    
    Queries mood entries and chat sentiment to understand
    the user's emotional patterns over time.
    """
    profile = {
        "dominant_mood": "neutral",
        "mood_counts": {},
        "recent_moods": [],
        "trend": "stable",
        "total_interactions": 0,
        "avg_sentiment_score": 0.5,
    }

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        # Get mood entries from last 30 days
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        moods = (
            sb.table("mood_entries")
            .select("mood, created_at")
            .eq("user_id", user_id)
            .gte("created_at", thirty_days_ago)
            .order("created_at", desc=True)
            .execute()
        )

        if moods.data:
            counts: Dict[str, int] = {}
            for entry in moods.data:
                m = entry["mood"]
                counts[m] = counts.get(m, 0) + 1

            profile["mood_counts"] = counts
            profile["dominant_mood"] = max(counts, key=counts.get) if counts else "neutral"  # type: ignore
            profile["recent_moods"] = [e["mood"] for e in moods.data[:7]]
            profile["total_interactions"] = len(moods.data)

            # Trend: compare first half vs second half
            half = len(moods.data) // 2
            if half > 0:
                neg_moods = {"sad", "anxious", "angry", "stressed"}
                first_neg = sum(1 for e in moods.data[:half] if e["mood"] in neg_moods)
                second_neg = sum(1 for e in moods.data[half:] if e["mood"] in neg_moods)
                if first_neg > second_neg + 1:
                    profile["trend"] = "improving"
                elif second_neg > first_neg + 1:
                    profile["trend"] = "declining"

        # Get chat sentiment data
        chats = (
            sb.table("chat_messages")
            .select("sentiment")
            .eq("user_id", user_id)
            .eq("role", "user")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        if chats.data:
            sentiments = [c["sentiment"] for c in chats.data if c.get("sentiment")]
            pos = sum(1 for s in sentiments if s == "POSITIVE")
            profile["avg_sentiment_score"] = pos / len(sentiments) if sentiments else 0.5

    except Exception:
        pass

    return profile


def get_personalized_recommendations(user_id: str, current_mood: str = "") -> Dict[str, Any]:
    """Generate personalized coping recommendations based on user history."""
    profile = get_user_emotion_profile(user_id)
    mood_key = current_mood or profile["dominant_mood"]

    # Map mood to strategy category
    mood_to_category = {
        "happy": "default", "good": "default", "neutral": "default",
        "sad": "sad", "anxious": "anxious", "angry": "angry",
        "stressed": "stress", "Stressed": "stress", "Sad": "sad",
        "Anxious": "anxious", "Angry": "angry",
    }
    category = mood_to_category.get(mood_key, "default")
    strategies = COPING_STRATEGIES.get(category, COPING_STRATEGIES["default"])

    # Build personalized context message
    context_msg = ""
    if profile["recent_moods"]:
        recent = profile["recent_moods"][:3]
        if len(set(recent)) == 1:
            context_msg = f"You've been feeling {recent[0]} lately. "
        else:
            context_msg = f"Your recent moods have been: {', '.join(recent)}. "

    if profile["trend"] == "improving":
        context_msg += "Great news — your overall trend is improving! "
    elif profile["trend"] == "declining":
        context_msg += "I've noticed your mood has been dipping recently. Let's work on that together. "

    return {
        "strategies": strategies,
        "context_message": context_msg,
        "profile": profile,
        "category": category,
    }


def get_personalized_greeting(user_id: str, user_name: str = "") -> str:
    """Generate a personalized greeting based on user history."""
    profile = get_user_emotion_profile(user_id)
    name = user_name or "there"

    greetings = {
        "improving": f"Welcome back, {name}! 🌟 Your mood has been trending upward — keep going!",
        "declining": f"Hey {name}, glad to see you. 💚 I've noticed things have been a bit tough. I'm here for you.",
        "stable": f"Hi {name}! 👋 Good to see you. How are you feeling today?",
    }

    return greetings.get(profile["trend"], greetings["stable"])


def build_chat_context(user_id: str) -> str:
    """Build a rich context string for the AI to generate better responses.
    
    Retrieves the user's emotional profile and recent chat history
    to inform the AI's conversational approach.
    """
    profile = get_user_emotion_profile(user_id)
    parts = []

    if profile["dominant_mood"] != "neutral":
        parts.append(f"The user's dominant mood recently has been '{profile['dominant_mood']}'.")

    if profile["trend"] == "declining":
        parts.append("Their emotional trend is declining — be extra supportive and suggest professional help if appropriate.")
    elif profile["trend"] == "improving":
        parts.append("Their emotional trend is improving — reinforce positive behaviors.")

    if profile["recent_moods"]:
        parts.append(f"Recent mood logs: {', '.join(profile['recent_moods'][:5])}.")

    return " ".join(parts) if parts else ""
