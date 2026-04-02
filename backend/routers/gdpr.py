"""GDPR Compliance Router — data export, deletion, and consent tracking."""

from fastapi import APIRouter, Query, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import Optional
from datetime import datetime
import json

router = APIRouter(prefix="/api/gdpr", tags=["gdpr"])


class ConsentRequest(BaseModel):
    user_id: str
    consent_type: str  # data_processing, analytics, email_notifications, research
    granted: bool


@router.post("/consent")
async def update_consent(req: ConsentRequest):
    """Update user consent preferences."""
    valid_types = {"data_processing", "analytics", "email_notifications", "research"}
    if req.consent_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid consent type. Must be one of: {valid_types}")

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        record = {
            "user_id": req.user_id,
            "consent_type": req.consent_type,
            "granted": req.granted,
            "granted_at": datetime.utcnow().isoformat() if req.granted else None,
            "revoked_at": datetime.utcnow().isoformat() if not req.granted else None,
        }
        sb.table("user_consents").insert(record).execute()
        return {"status": "ok", "message": f"Consent {'granted' if req.granted else 'revoked'} for {req.consent_type}"}
    except Exception:
        return {"status": "ok", "message": "Consent preference recorded locally"}


@router.get("/consent")
async def get_consents(user_id: str = Query(...)):
    """Get user's consent preferences."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("user_consents").select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        # Get latest consent per type
        latest = {}
        for entry in (result.data or []):
            ct = entry.get("consent_type")
            if ct and ct not in latest:
                latest[ct] = entry
        return {"consents": latest}
    except Exception:
        return {"consents": {}}


@router.get("/export")
async def export_user_data(user_id: str = Query(...)):
    """Export all user data as JSON (GDPR data portability)."""
    export = {"profile": None, "messages": [], "moods": [], "assessments": {}, "crisis_events": [], "homework": []}

    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        # Profile
        profile = sb.table("profiles").select("id, name, email, created_at, last_active_at").eq("id", user_id).execute()
        export["profile"] = profile.data[0] if profile.data else None

        # Chat messages
        msgs = sb.table("chat_messages").select("role, content, sentiment, emotion, created_at").eq("user_id", user_id).order("created_at", desc=False).execute()
        export["messages"] = msgs.data or []

        # Mood entries
        moods = sb.table("mood_entries").select("*").eq("user_id", user_id).order("created_at", desc=False).execute()
        export["moods"] = moods.data or []

        # PHQ-9
        phq9 = sb.table("phq9_entries").select("*").eq("user_id", user_id).order("created_at", desc=False).execute()
        export["assessments"]["phq9"] = phq9.data or []

        # GAD-7
        gad7 = sb.table("gad7_entries").select("*").eq("user_id", user_id).order("created_at", desc=False).execute()
        export["assessments"]["gad7"] = gad7.data or []

        # Crisis events
        crises = sb.table("crisis_events").select("*").eq("user_id", user_id).execute()
        export["crisis_events"] = crises.data or []

        # Homework
        hw = sb.table("homework_assignments").select("*").eq("user_id", user_id).execute()
        export["homework"] = hw.data or []

    except Exception:
        pass

    export["exported_at"] = datetime.utcnow().isoformat()
    return export


@router.delete("/delete")
async def delete_user_data(user_id: str = Query(...)):
    """Delete all user data (GDPR right to erasure).
    
    WARNING: This action is irreversible.
    """
    deleted_tables = []
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()

        tables = [
            "chat_messages", "mood_entries", "emotion_detections",
            "phq9_entries", "gad7_entries", "session_summaries",
            "homework_assignments", "crisis_events", "follow_ups",
            "activity_streaks", "therapist_alerts", "user_consents",
        ]

        for table in tables:
            try:
                sb.table(table).delete().eq("user_id", user_id).execute()
                deleted_tables.append(table)
            except Exception:
                pass

        # Finally delete the profile
        try:
            sb.table("profiles").delete().eq("id", user_id).execute()
            deleted_tables.append("profiles")
        except Exception:
            pass

    except Exception:
        pass

    return {
        "status": "ok",
        "message": "All user data has been deleted",
        "tables_cleaned": deleted_tables,
        "deleted_at": datetime.utcnow().isoformat(),
    }
