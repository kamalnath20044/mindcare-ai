"""Composite Risk Scoring Service — multi-factor risk assessment.

Combines mood trends, sentiment analysis, PHQ-9 score changes,
session inactivity, and crisis keyword detection into a unified
risk score for each user.

Output: Low / Medium / High / Critical
"""

from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime, timedelta


# ─── Risk Weights ───
WEIGHTS = {
    "mood_trend": 0.20,
    "sentiment": 0.15,
    "phq9_score": 0.25,
    "inactivity": 0.15,
    "crisis_history": 0.15,
    "gad7_score": 0.10,
}


def compute_risk_score(user_id: str) -> Dict[str, Any]:
    """Compute a composite risk score from multiple data sources.
    
    Returns a dict with overall risk level, numeric score (0-100),
    and breakdown of each factor.
    """
    factors: Dict[str, Dict[str, Any]] = {}
    
    # 1. Mood Trend Factor
    factors["mood_trend"] = _assess_mood_factor(user_id)
    
    # 2. Sentiment Factor
    factors["sentiment"] = _assess_sentiment_factor(user_id)
    
    # 3. PHQ-9 Score Factor
    factors["phq9_score"] = _assess_phq9_factor(user_id)
    
    # 4. Inactivity Factor
    factors["inactivity"] = _assess_inactivity_factor(user_id)
    
    # 5. Crisis History Factor
    factors["crisis_history"] = _assess_crisis_factor(user_id)
    
    # 6. GAD-7 Score Factor
    factors["gad7_score"] = _assess_gad7_factor(user_id)
    
    # Compute weighted score (0-100)
    total_score = 0.0
    for key, factor in factors.items():
        weight = WEIGHTS.get(key, 0)
        total_score += factor["score"] * weight
    
    total_score = min(100, max(0, total_score))
    
    # Map score to risk level
    if total_score >= 80:
        risk_level = "critical"
        recommendation = "Immediate clinical intervention recommended. Alert therapist."
    elif total_score >= 60:
        risk_level = "high"
        recommendation = "Close monitoring required. Consider reaching out to the user and their therapist."
    elif total_score >= 35:
        risk_level = "medium"
        recommendation = "Elevated risk indicators. Encourage regular check-ins and assessments."
    else:
        risk_level = "low"
        recommendation = "Within normal range. Continue regular monitoring."
    
    return {
        "user_id": user_id,
        "risk_score": round(total_score, 1),
        "risk_level": risk_level,
        "recommendation": recommendation,
        "factors": factors,
        "computed_at": datetime.utcnow().isoformat(),
    }


def _assess_mood_factor(user_id: str) -> Dict[str, Any]:
    """Assess risk from mood entry trends."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        since = (datetime.utcnow() - timedelta(days=14)).isoformat()
        result = (
            sb.table("mood_entries").select("mood, mood_score")
            .eq("user_id", user_id)
            .gte("created_at", since)
            .order("created_at", desc=True)
            .limit(14)
            .execute()
        )
        if not result.data:
            return {"score": 20, "detail": "No mood data available"}
        
        neg_moods = {"sad", "anxious", "stressed", "angry"}
        neg_count = sum(1 for m in result.data if m.get("mood") in neg_moods)
        ratio = neg_count / len(result.data)
        
        # Also consider mood_score if available
        scores = [m.get("mood_score") for m in result.data if m.get("mood_score")]
        avg_score = sum(scores) / len(scores) if scores else 5
        
        score = ratio * 70 + (1 - avg_score / 10) * 30
        return {
            "score": min(100, max(0, score)),
            "detail": f"{neg_count}/{len(result.data)} negative moods, avg score: {avg_score:.1f}/10",
        }
    except Exception:
        return {"score": 20, "detail": "Unable to assess"}


def _assess_sentiment_factor(user_id: str) -> Dict[str, Any]:
    """Assess risk from chat sentiment trends."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("chat_messages").select("sentiment")
            .eq("user_id", user_id)
            .eq("role", "user")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        if not result.data:
            return {"score": 20, "detail": "No chat data available"}
        
        sentiments = [m.get("sentiment") for m in result.data if m.get("sentiment")]
        neg = sum(1 for s in sentiments if s == "NEGATIVE")
        ratio = neg / len(sentiments) if sentiments else 0
        
        score = ratio * 100
        return {
            "score": min(100, max(0, score)),
            "detail": f"{neg}/{len(sentiments)} negative sentiments",
        }
    except Exception:
        return {"score": 20, "detail": "Unable to assess"}


def _assess_phq9_factor(user_id: str) -> Dict[str, Any]:
    """Assess risk from PHQ-9 scores."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("phq9_entries").select("total_score, severity")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(3)
            .execute()
        )
        if not result.data:
            return {"score": 15, "detail": "No PHQ-9 assessments taken"}
        
        latest = result.data[0]["total_score"]
        severity_scores = {"none": 0, "mild": 25, "moderate": 50, "moderately_severe": 75, "severe": 100}
        score = severity_scores.get(result.data[0]["severity"], 25)
        
        # Check for worsening trend
        if len(result.data) >= 2:
            prev = result.data[1]["total_score"]
            if latest > prev + 5:
                score = min(100, score + 15)  # Worsening bonus
        
        return {
            "score": score,
            "detail": f"Latest PHQ-9: {latest}/27 ({result.data[0]['severity']})",
        }
    except Exception:
        return {"score": 15, "detail": "Unable to assess"}


def _assess_gad7_factor(user_id: str) -> Dict[str, Any]:
    """Assess risk from GAD-7 scores."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("gad7_entries").select("total_score, severity")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return {"score": 15, "detail": "No GAD-7 assessments taken"}
        
        severity_scores = {"none": 0, "mild": 25, "moderate": 60, "severe": 100}
        score = severity_scores.get(result.data[0]["severity"], 25)
        return {
            "score": score,
            "detail": f"Latest GAD-7: {result.data[0]['total_score']}/21 ({result.data[0]['severity']})",
        }
    except Exception:
        return {"score": 15, "detail": "Unable to assess"}


def _assess_inactivity_factor(user_id: str) -> Dict[str, Any]:
    """Assess risk from user inactivity."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("profiles").select("last_active_at")
            .eq("id", user_id)
            .execute()
        )
        if not result.data or not result.data[0].get("last_active_at"):
            return {"score": 40, "detail": "No activity data"}
        
        last_active = result.data[0]["last_active_at"]
        last_dt = datetime.fromisoformat(last_active.replace("Z", "+00:00").replace("+00:00", ""))
        days_inactive = (datetime.utcnow() - last_dt).days
        
        if days_inactive >= 14:
            score = 90
        elif days_inactive >= 7:
            score = 70
        elif days_inactive >= 3:
            score = 40
        elif days_inactive >= 1:
            score = 20
        else:
            score = 5
        
        return {
            "score": score,
            "detail": f"Inactive for {days_inactive} day(s)",
        }
    except Exception:
        return {"score": 20, "detail": "Unable to assess"}


def _assess_crisis_factor(user_id: str) -> Dict[str, Any]:
    """Assess risk from crisis event history."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        since = (datetime.utcnow() - timedelta(days=30)).isoformat()
        result = (
            sb.table("crisis_events").select("risk_level")
            .eq("user_id", user_id)
            .gte("created_at", since)
            .execute()
        )
        if not result.data:
            return {"score": 0, "detail": "No crisis events in last 30 days"}
        
        critical = sum(1 for e in result.data if e.get("risk_level") == "critical")
        high = sum(1 for e in result.data if e.get("risk_level") == "high")
        total = len(result.data)
        
        score = min(100, critical * 40 + high * 20 + total * 5)
        return {
            "score": score,
            "detail": f"{total} crisis event(s) in 30 days ({critical} critical, {high} high)",
        }
    except Exception:
        return {"score": 0, "detail": "Unable to assess"}


def get_high_risk_users(limit: int = 20) -> List[Dict[str, Any]]:
    """Get a list of high-risk users for the admin dashboard."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = sb.table("profiles").select("id, name, email, last_active_at").execute()
        
        users_with_risk = []
        for user in (result.data or []):
            risk = compute_risk_score(user["id"])
            if risk["risk_level"] in ("high", "critical"):
                users_with_risk.append({
                    "user_id": user["id"],
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "last_active": user.get("last_active_at"),
                    "risk_score": risk["risk_score"],
                    "risk_level": risk["risk_level"],
                    "factors": risk["factors"],
                })
        
        users_with_risk.sort(key=lambda u: u["risk_score"], reverse=True)
        return users_with_risk[:limit]
    except Exception:
        return []
