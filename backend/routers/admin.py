"""Admin Dashboard Router — therapist/admin monitoring endpoints.

Provides data for the admin dashboard including:
- High-risk user monitoring
- Crisis event logs
- User activity & retention stats
- Therapist alert management
- Weekly summaries
"""

from fastapi import APIRouter, Query, Depends  # type: ignore
from typing import Optional
from datetime import datetime, timedelta
from services.risk_scoring_service import compute_risk_score, get_high_risk_users  # type: ignore
from services.therapist_alert_service import (  # type: ignore
    get_pending_alerts, acknowledge_alert, resolve_alert, get_alerts_for_user,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/overview")
async def admin_overview():
    """Get high-level platform statistics for the admin dashboard."""
    stats = {
        "total_users": 0,
        "active_users_7d": 0,
        "active_users_30d": 0,
        "total_messages": 0,
        "total_crisis_events": 0,
        "pending_alerts": 0,
        "high_risk_users": 0,
    }

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        # Total users
        users = sb.table("profiles").select("id", count="exact").execute()
        stats["total_users"] = users.count or 0

        # Active users (7 days)
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        active_7d = sb.table("profiles").select("id", count="exact").gte("last_active_at", week_ago).execute()
        stats["active_users_7d"] = active_7d.count or 0

        # Active users (30 days)
        month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        active_30d = sb.table("profiles").select("id", count="exact").gte("last_active_at", month_ago).execute()
        stats["active_users_30d"] = active_30d.count or 0

        # Total messages
        msgs = sb.table("chat_messages").select("id", count="exact").execute()
        stats["total_messages"] = msgs.count or 0

        # Crisis events (30 days)
        crises = sb.table("crisis_events").select("id", count="exact").gte("created_at", month_ago).execute()
        stats["total_crisis_events"] = crises.count or 0

        # Pending alerts
        alerts = sb.table("therapist_alerts").select("id", count="exact").neq("status", "resolved").execute()
        stats["pending_alerts"] = alerts.count or 0

    except Exception:
        pass

    # High risk users count
    high_risk = get_high_risk_users(limit=50)
    stats["high_risk_users"] = len(high_risk)

    return stats


@router.get("/users")
async def list_users(
    limit: int = Query(default=50),
    offset: int = Query(default=0),
    sort: str = Query(default="last_active_at"),
):
    """List all users with basic info for admin monitoring."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("profiles")
            .select("id, name, email, role, last_active_at, created_at")
            .order(sort, desc=True)
            .limit(limit)
            .execute()
        )
        return {"users": result.data or [], "total": len(result.data or [])}
    except Exception:
        return {"users": [], "total": 0}


@router.get("/high-risk")
async def high_risk_users(limit: int = Query(default=20)):
    """Get list of high-risk users with risk scores."""
    return {"users": get_high_risk_users(limit)}


@router.get("/risk/{user_id}")
async def user_risk_score(user_id: str):
    """Get detailed risk assessment for a specific user."""
    return compute_risk_score(user_id)


@router.get("/crisis-events")
async def crisis_events(
    limit: int = Query(default=50),
    user_id: Optional[str] = Query(default=None),
):
    """Get crisis event logs."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        query = sb.table("crisis_events").select("*").order("created_at", desc=True).limit(limit)
        if user_id:
            query = query.eq("user_id", user_id)
        result = query.execute()
        return {"events": result.data or []}
    except Exception:
        return {"events": []}


@router.get("/alerts")
async def admin_alerts(limit: int = Query(default=50)):
    """Get pending therapist alerts."""
    return {"alerts": get_pending_alerts(limit)}


@router.post("/alerts/{alert_id}/acknowledge")
async def ack_alert(alert_id: int, by: str = Query(default="therapist")):
    """Acknowledge a therapist alert."""
    return acknowledge_alert(alert_id, by)


@router.post("/alerts/{alert_id}/resolve")
async def res_alert(alert_id: int):
    """Resolve a therapist alert."""
    return resolve_alert(alert_id)


@router.get("/user-detail/{user_id}")
async def user_detail(user_id: str):
    """Get detailed info about a specific user for admin review."""
    detail = {"profile": None, "risk": None, "recent_messages": [], "mood_history": [], "assessments": None, "alerts": []}

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        # Profile
        profile = sb.table("profiles").select("*").eq("id", user_id).execute()
        if profile.data:
            detail["profile"] = profile.data[0]

        # Recent messages
        msgs = sb.table("chat_messages").select("role, content, sentiment, created_at").eq("user_id", user_id).order("created_at", desc=True).limit(20).execute()
        detail["recent_messages"] = msgs.data or []

        # Mood history
        moods = sb.table("mood_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(14).execute()
        detail["mood_history"] = moods.data or []

    except Exception:
        pass

    # Risk score
    detail["risk"] = compute_risk_score(user_id)

    # Assessment trends
    try:
        from services.assessment_service import get_assessment_trends  # type: ignore
        detail["assessments"] = get_assessment_trends(user_id)
    except Exception:
        pass

    # Alerts
    detail["alerts"] = get_alerts_for_user(user_id)

    return detail


@router.get("/retention")
async def retention_stats():
    """Get user retention statistics (1/7/14/30 days)."""
    retention = {"day_1": 0, "day_7": 0, "day_14": 0, "day_30": 0, "total_users": 0}

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        users = sb.table("profiles").select("id", count="exact").execute()
        total = users.count or 0
        retention["total_users"] = total
        if total == 0:
            return retention

        for label, days in [("day_1", 1), ("day_7", 7), ("day_14", 14), ("day_30", 30)]:
            since = (datetime.utcnow() - timedelta(days=days)).isoformat()
            active = sb.table("profiles").select("id", count="exact").gte("last_active_at", since).execute()
            count = active.count or 0
            retention[label] = round(count / total * 100, 1)

    except Exception:
        pass

    return retention


@router.get("/phq9-distribution")
async def phq9_distribution():
    """Get PHQ-9 severity distribution across all users."""
    distribution = {"none": 0, "mild": 0, "moderate": 0, "moderately_severe": 0, "severe": 0}

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        # Get latest PHQ-9 for each user by fetching recent entries
        result = sb.table("phq9_entries").select("severity, user_id").order("created_at", desc=True).limit(200).execute()
        if result.data:
            # Get latest per user
            seen_users = set()
            for entry in result.data:
                uid = entry.get("user_id")
                if uid not in seen_users:
                    seen_users.add(uid)
                    sev = entry.get("severity", "none")
                    if sev in distribution:
                        distribution[sev] += 1

    except Exception:
        pass

    return {"distribution": distribution, "total_assessed": sum(distribution.values())}


@router.get("/weekly-summary")
async def weekly_summary():
    """Generate a weekly summary of platform activity and at-risk users."""
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

    summary = {
        "period": f"{(datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.utcnow().strftime('%Y-%m-%d')}",
        "new_users": 0,
        "active_users": 0,
        "total_messages": 0,
        "crisis_events": 0,
        "assessments_completed": 0,
        "high_risk_users": [],
        "top_concerns": [],
    }

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        # New users this week
        new_users = sb.table("profiles").select("id", count="exact").gte("created_at", week_ago).execute()
        summary["new_users"] = new_users.count or 0

        # Active users
        active = sb.table("profiles").select("id", count="exact").gte("last_active_at", week_ago).execute()
        summary["active_users"] = active.count or 0

        # Messages
        msgs = sb.table("chat_messages").select("id", count="exact").gte("created_at", week_ago).execute()
        summary["total_messages"] = msgs.count or 0

        # Crisis events
        crises = sb.table("crisis_events").select("id", count="exact").gte("created_at", week_ago).execute()
        summary["crisis_events"] = crises.count or 0

        # Assessments
        phq9 = sb.table("phq9_entries").select("id", count="exact").gte("created_at", week_ago).execute()
        gad7 = sb.table("gad7_entries").select("id", count="exact").gte("created_at", week_ago).execute()
        summary["assessments_completed"] = (phq9.count or 0) + (gad7.count or 0)

    except Exception:
        pass

    # High risk users
    summary["high_risk_users"] = get_high_risk_users(limit=10)

    return summary
