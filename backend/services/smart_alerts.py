"""Smart Alerts & Recommendations Service.

Analyzes user patterns and generates personalized alerts and recommendations
based on mood history, chat sentiment, and emotion detection data.
"""

from __future__ import annotations
from typing import Dict, List, Any
from datetime import datetime


# ---------------------------------------------------------------------------
# Alert Thresholds
# ---------------------------------------------------------------------------
NEGATIVE_STREAK_THRESHOLD = 3   # consecutive negative sentiments
DISTRESS_KEYWORDS = [
    "hopeless", "worthless", "can't cope", "overwhelmed",
    "breaking down", "falling apart", "give up", "no point",
    "exhausted", "burnt out", "burnout", "panic attack",
]


# ---------------------------------------------------------------------------
# Recommendation Database
# ---------------------------------------------------------------------------
RECOMMENDATIONS = {
    "high_stress": {
        "title": "🧘 Stress Management",
        "priority": "high",
        "suggestions": [
            "Try a 5-minute guided breathing exercise",
            "Take a short walk outside to reset your mind",
            "Write down 3 things you're grateful for today",
            "Practice progressive muscle relaxation",
        ],
        "resource": "breathing",
    },
    "persistent_sadness": {
        "title": "💙 Emotional Support",
        "priority": "high",
        "suggestions": [
            "Reach out to someone you trust and talk about your feelings",
            "Consider journaling your thoughts — it helps process emotions",
            "Try a loving-kindness meditation",
            "Remember: it's okay to not be okay. Be gentle with yourself.",
        ],
        "resource": "meditation",
    },
    "anxiety_detected": {
        "title": "🌿 Anxiety Relief",
        "priority": "medium",
        "suggestions": [
            "Try the 5-4-3-2-1 grounding technique",
            "Practice box breathing (4 counts in, hold, out, hold)",
            "Limit caffeine and screen time before bed",
            "Focus only on what you can control right now",
        ],
        "resource": "breathing",
    },
    "improving_mood": {
        "title": "✨ Keep It Going!",
        "priority": "low",
        "suggestions": [
            "Great progress! Continue the activities that make you feel good",
            "Consider setting a small positive goal for tomorrow",
            "Share your positive energy — acts of kindness boost mood",
        ],
        "resource": "motivation",
    },
    "general_wellness": {
        "title": "🌱 Daily Wellness",
        "priority": "low",
        "suggestions": [
            "Maintain a regular sleep schedule",
            "Stay hydrated — drink at least 8 glasses of water",
            "Spend 10 minutes in nature or sunlight today",
            "Practice mindful eating during your next meal",
        ],
        "resource": "relaxation",
    },
}


def generate_alerts(
    mood_history: List[Dict[str, Any]],
    sentiment_trend: str = "unknown",
    latest_emotion: str = "",
    latest_message: str = "",
) -> List[Dict[str, Any]]:
    """Generate personalized alerts based on user data.
    
    Returns a list of alert objects with type, message, priority, and actions.
    """
    alerts: List[Dict[str, Any]] = []

    # Check for distress keywords in latest message
    lower_msg = latest_message.lower()
    for keyword in DISTRESS_KEYWORDS:
        if keyword in lower_msg:
            alerts.append({
                "type": "distress",
                "priority": "critical",
                "title": "🚨 We're Concerned About You",
                "message": "Your message suggests you may be going through a very difficult time. Please know that help is available and you don't have to face this alone.",
                "action": "show_emergency",
            })
            break

    # Analyze mood history
    if mood_history:
        recent_moods = [m.get("mood", "") for m in mood_history[:5]]  # type: ignore
        negative_moods = ["sad", "anxious", "angry", "stressed"]
        negative_count = sum(1 for m in recent_moods if m in negative_moods)

        if negative_count >= 3:
            alerts.append({
                "type": "mood_pattern",
                "priority": "high",
                "title": "📊 Mood Pattern Detected",
                "message": f"We've noticed {negative_count} out of your last {len(recent_moods)} mood entries indicate you're struggling. Here are some resources that might help.",
                "action": "show_recommendations",
                "recommendation_key": "persistent_sadness",
            })

        if any(m == "stressed" for m in recent_moods):
            alerts.append({
                "type": "stress_alert",
                "priority": "medium",
                "title": "😤 Stress Alert",
                "message": "You've been reporting stress. Consider trying our guided breathing exercises.",
                "action": "navigate",
                "target": "/wellness",
            })

    # Sentiment trend alerts
    if sentiment_trend == "declining":
        alerts.append({
            "type": "sentiment_decline",
            "priority": "high",
            "title": "📉 Sentiment Trend",
            "message": "Your recent conversations show a declining emotional trend. Would you like to try some wellness activities?",
            "action": "show_recommendations",
            "recommendation_key": "high_stress",
        })
    elif sentiment_trend == "improving":
        alerts.append({
            "type": "sentiment_improving",
            "priority": "low",
            "title": "📈 You're Doing Great!",
            "message": "Your emotional trend is improving! Keep up the positive momentum.",
            "action": "show_recommendations",
            "recommendation_key": "improving_mood",
        })

    # Emotion-based alerts
    emotion_recommendations = {
        "Sad": "persistent_sadness",
        "Angry": "high_stress",
        "Fear": "anxiety_detected",
    }
    if latest_emotion in emotion_recommendations:
        key = emotion_recommendations[latest_emotion]
        rec = RECOMMENDATIONS[key]
        alerts.append({
            "type": "emotion_recommendation",
            "priority": rec["priority"],
            "title": rec["title"],
            "message": f"Based on your detected emotion ({latest_emotion}), here's a suggestion:",
            "suggestion": rec["suggestions"][0],
            "action": "navigate",
            "target": "/wellness",
        })

    return alerts


def get_recommendations(key: str = "general_wellness") -> Dict[str, Any]:
    """Get a specific recommendation set."""
    return RECOMMENDATIONS.get(key, RECOMMENDATIONS["general_wellness"])
