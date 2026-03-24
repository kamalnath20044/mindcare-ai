"""Analytics Service — generates dashboard insights, mood trends, and usage stats.

Provides the data layer for the analytics dashboard showing mood graphs,
emotion distribution, engagement metrics, and mental health insights.
"""

from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import Counter


def get_dashboard_stats(user_id: str) -> Dict[str, Any]:
    """Get comprehensive dashboard statistics for a user."""
    stats = {
        "total_messages": 0,
        "total_mood_logs": 0,
        "total_emotions_detected": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "total_checkins": 0,
        "days_active": 0,
        "avg_sentiment": "neutral",
        "member_since": None,
    }

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        # Message count
        msgs = sb.table("chat_messages").select("id", count="exact").eq("user_id", user_id).execute()
        stats["total_messages"] = msgs.count or 0

        # Mood log count
        moods = sb.table("mood_entries").select("id", count="exact").eq("user_id", user_id).execute()
        stats["total_mood_logs"] = moods.count or 0

        # Emotion detections count
        emotions = sb.table("emotion_detections").select("id", count="exact").eq("user_id", user_id).execute()
        stats["total_emotions_detected"] = emotions.count or 0

        # Streak data
        streak = sb.table("activity_streaks").select("*").eq("user_id", user_id).execute()
        if streak.data:
            stats["current_streak"] = streak.data[0].get("current_streak", 0)
            stats["longest_streak"] = streak.data[0].get("longest_streak", 0)
            stats["total_checkins"] = streak.data[0].get("total_checkins", 0)

        # Profile info
        profile = sb.table("profiles").select("created_at").eq("id", user_id).execute()
        if profile.data:
            stats["member_since"] = profile.data[0].get("created_at")

        # Average sentiment
        recent_msgs = (
            sb.table("chat_messages")
            .select("sentiment")
            .eq("user_id", user_id)
            .eq("role", "user")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        if recent_msgs.data:
            sentiments = [m["sentiment"] for m in recent_msgs.data if m.get("sentiment")]
            pos = sum(1 for s in sentiments if s == "POSITIVE")
            if sentiments:
                ratio = pos / len(sentiments)
                stats["avg_sentiment"] = "positive" if ratio > 0.6 else "negative" if ratio < 0.4 else "neutral"

    except Exception:
        pass

    return stats


def get_mood_analytics(user_id: str, days: int = 30) -> Dict[str, Any]:
    """Get detailed mood analytics with trends, distribution, and daily breakdown."""
    analytics = {
        "daily_moods": [],
        "distribution": {},
        "trend": "stable",
        "weekly_avg": [],
        "most_common_mood": "neutral",
        "mood_variability": "low",
        "insights": [],
    }

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        result = (
            sb.table("mood_entries")
            .select("*")
            .eq("user_id", user_id)
            .gte("created_at", since)
            .order("created_at", desc=False)
            .execute()
        )

        if not result.data:
            return analytics

        entries = result.data

        # Daily mood data for charts
        for entry in entries:
            analytics["daily_moods"].append({
                "date": entry["created_at"][:10],
                "mood": entry["mood"],
                "note": entry.get("note"),
                "intensity": entry.get("intensity", 3),
            })

        # Distribution
        mood_counts = Counter(e["mood"] for e in entries)
        total = sum(mood_counts.values())
        analytics["distribution"] = {
            mood: {"count": count, "percentage": round(count / total * 100, 1)}
            for mood, count in mood_counts.most_common()
        }
        analytics["most_common_mood"] = mood_counts.most_common(1)[0][0] if mood_counts else "neutral"

        # Mood variability
        unique_moods = len(mood_counts)
        analytics["mood_variability"] = "high" if unique_moods >= 5 else "medium" if unique_moods >= 3 else "low"

        # Trend analysis (compare last 7 days vs previous 7)
        neg_moods = {"sad", "anxious", "angry", "stressed"}
        recent = [e for e in entries if e["created_at"][:10] >= (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")]
        older = [e for e in entries if e["created_at"][:10] < (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")]

        recent_neg = sum(1 for e in recent if e["mood"] in neg_moods) / max(len(recent), 1)
        older_neg = sum(1 for e in older if e["mood"] in neg_moods) / max(len(older), 1)

        if recent_neg < older_neg - 0.15:
            analytics["trend"] = "improving"
        elif recent_neg > older_neg + 0.15:
            analytics["trend"] = "declining"

        # Generate insights
        insights = []
        if analytics["trend"] == "improving":
            insights.append({"type": "positive", "message": "📈 Your mood has been improving this week compared to last week!"})
        elif analytics["trend"] == "declining":
            insights.append({"type": "warning", "message": "📉 Your mood trend has dipped recently. Consider trying some wellness activities."})

        if mood_counts.get("stressed", 0) > total * 0.3:
            insights.append({"type": "alert", "message": "😤 Stress has been a frequent emotion. Try our guided breathing exercises."})
        if mood_counts.get("happy", 0) + mood_counts.get("good", 0) > total * 0.5:
            insights.append({"type": "positive", "message": "😊 More than half your mood logs are positive — great work!"})

        analytics["insights"] = insights

        # Weekly averages (mood values: happy=5, good=4, neutral=3, sad=2, anxious=2, angry=1, stressed=1)
        mood_values = {"happy": 5, "good": 4, "neutral": 3, "sad": 2, "anxious": 2, "angry": 1, "stressed": 1}
        week_data: Dict[str, List[int]] = {}
        for entry in entries:
            week_num = datetime.fromisoformat(entry["created_at"].replace("Z", "")).strftime("%U")
            week_data.setdefault(week_num, []).append(mood_values.get(entry["mood"], 3))
        analytics["weekly_avg"] = [
            {"week": w, "avg": round(sum(vals) / len(vals), 2)} for w, vals in sorted(week_data.items())
        ]

    except Exception:
        pass

    return analytics


def get_emotion_analytics(user_id: str, days: int = 30) -> Dict[str, Any]:
    """Get emotion detection analytics (from webcam + text)."""
    analytics = {"distribution": {}, "timeline": [], "total": 0}

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        result = (
            sb.table("emotion_detections")
            .select("*")
            .eq("user_id", user_id)
            .gte("created_at", since)
            .order("created_at", desc=False)
            .execute()
        )

        if result.data:
            analytics["total"] = len(result.data)
            emotion_counts = Counter(e["emotion"] for e in result.data)
            total = sum(emotion_counts.values())
            analytics["distribution"] = {
                em: {"count": c, "percentage": round(c / total * 100, 1)}
                for em, c in emotion_counts.most_common()
            }
            analytics["timeline"] = [
                {"date": e["created_at"][:10], "emotion": e["emotion"], "confidence": e.get("confidence")}
                for e in result.data[-30:]
            ]

    except Exception:
        pass

    return analytics


def get_chat_analytics(user_id: str) -> Dict[str, Any]:
    """Get chat usage analytics."""
    analytics = {"total_messages": 0, "sentiment_distribution": {}, "daily_activity": [], "therapist_sessions": 0}

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        since = (datetime.utcnow() - timedelta(days=30)).isoformat()
        result = (
            sb.table("chat_messages")
            .select("*")
            .eq("user_id", user_id)
            .gte("created_at", since)
            .order("created_at", desc=False)
            .execute()
        )

        if result.data:
            analytics["total_messages"] = len(result.data)

            # Sentiment distribution (user messages only)
            user_msgs = [m for m in result.data if m["role"] == "user"]
            sentiments = Counter(m.get("sentiment", "unknown") for m in user_msgs)
            analytics["sentiment_distribution"] = dict(sentiments)

            # Daily activity
            day_counts: Dict[str, int] = {}
            for m in result.data:
                day = m["created_at"][:10]
                day_counts[day] = day_counts.get(day, 0) + 1
            analytics["daily_activity"] = [{"date": d, "count": c} for d, c in sorted(day_counts.items())]

            # Therapist sessions
            analytics["therapist_sessions"] = sum(1 for m in result.data if m.get("therapist_mode"))

    except Exception:
        pass

    return analytics
