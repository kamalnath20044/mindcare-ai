"""Therapist Alert Service — SendGrid email alerts for high-risk users.

Sends alerts to therapists when users exhibit critical risk factors.
Includes acknowledgement system and re-alert after 24 hours.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json


def send_alert(
    user_id: str,
    alert_type: str,
    risk_level: str,
    context: str,
    trigger_data: Any = None,
) -> Dict[str, Any]:
    """Create and send a therapist alert.
    
    Args:
        user_id: The user who triggered the alert
        alert_type: Type of alert (crisis, high_risk, phq9_severe, etc.)
        risk_level: low, medium, high, critical
        context: Human-readable description of the alert
        trigger_data: Raw data that triggered the alert
    """
    record = {
        "user_id": user_id,
        "alert_type": alert_type,
        "risk_level": risk_level,
        "context": context[:500],
        "trigger_data": json.dumps(trigger_data) if trigger_data else None,
        "status": "pending",
    }

    # Save to database
    alert_id = None
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = sb.table("therapist_alerts").insert(record).execute()
        if result.data:
            alert_id = result.data[0].get("id")
    except Exception:
        pass

    # Send email via SendGrid
    email_sent = _send_email_alert(user_id, alert_type, risk_level, context)

    if email_sent and alert_id:
        try:
            from services.supabase_client import get_supabase  # type: ignore
            sb = get_supabase()
            sb.table("therapist_alerts").update({
                "status": "sent",
                "sent_at": datetime.utcnow().isoformat(),
            }).eq("id", alert_id).execute()
        except Exception:
            pass

    return {
        "alert_id": alert_id,
        "status": "sent" if email_sent else "pending",
        "alert_type": alert_type,
        "risk_level": risk_level,
    }


def acknowledge_alert(alert_id: int, acknowledged_by: str = "therapist") -> Dict[str, Any]:
    """Mark an alert as acknowledged by a therapist."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("therapist_alerts").update({
            "status": "acknowledged",
            "acknowledged_at": datetime.utcnow().isoformat(),
            "acknowledged_by": acknowledged_by,
        }).eq("id", alert_id).execute()
        return {"status": "ok", "message": "Alert acknowledged"}
    except Exception:
        return {"status": "error", "message": "Failed to acknowledge alert"}


def resolve_alert(alert_id: int) -> Dict[str, Any]:
    """Mark an alert as resolved."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("therapist_alerts").update({
            "status": "resolved",
        }).eq("id", alert_id).execute()
        return {"status": "ok", "message": "Alert resolved"}
    except Exception:
        return {"status": "error", "message": "Failed to resolve alert"}


def get_pending_alerts(limit: int = 50) -> List[Dict[str, Any]]:
    """Get all pending/unacknowledged alerts for the therapist dashboard."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("therapist_alerts").select("*")
            .neq("status", "resolved")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def get_alerts_for_user(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get alerts for a specific user."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("therapist_alerts").select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def get_stale_alerts(hours: int = 24) -> List[Dict[str, Any]]:
    """Get alerts that haven't been acknowledged within the threshold.
    
    Used by the scheduler to trigger re-alerts.
    """
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        result = (
            sb.table("therapist_alerts").select("*")
            .eq("status", "sent")
            .lt("sent_at", cutoff)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def _send_email_alert(
    user_id: str, alert_type: str, risk_level: str, context: str
) -> bool:
    """Send an email alert to the therapist via SendGrid."""
    try:
        from config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, THERAPIST_DEFAULT_EMAIL  # type: ignore
        if not SENDGRID_API_KEY or not THERAPIST_DEFAULT_EMAIL:
            print("[ALERT] SendGrid not configured — skipping email")
            return False

        import sendgrid  # type: ignore
        from sendgrid.helpers.mail import Mail, Email, To, Content  # type: ignore

        # Get user info
        user_name = "Unknown User"
        user_email = ""
        try:
            from services.supabase_client import get_supabase  # type: ignore
            sb = get_supabase()
            profile = sb.table("profiles").select("name, email").eq("id", user_id).execute()
            if profile.data:
                user_name = profile.data[0].get("name", "Unknown")
                user_email = profile.data[0].get("email", "")
        except Exception:
            pass

        risk_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(risk_level, "⚪")

        subject = f"{risk_emoji} MindCare Alert: {risk_level.upper()} risk — {user_name}"
        body = f"""
        <h2>{risk_emoji} MindCare AI — Therapist Alert</h2>
        <hr/>
        <p><strong>User:</strong> {user_name} ({user_email})</p>
        <p><strong>Alert Type:</strong> {alert_type}</p>
        <p><strong>Risk Level:</strong> {risk_level.upper()}</p>
        <p><strong>Context:</strong> {context}</p>
        <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
        <hr/>
        <p>Please review this alert in the <a href="#">MindCare Admin Dashboard</a>.</p>
        <p><em>This alert will be re-sent in 24 hours if not acknowledged.</em></p>
        """

        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        mail = Mail(
            from_email=Email(SENDGRID_FROM_EMAIL),
            to_emails=To(THERAPIST_DEFAULT_EMAIL),
            subject=subject,
            html_content=Content("text/html", body),
        )
        sg.client.mail.send.post(request_body=mail.get())
        print(f"[ALERT] Email sent to {THERAPIST_DEFAULT_EMAIL} for user {user_id}")
        return True

    except Exception as e:
        print(f"[ALERT] Email send failed: {e}")
        return False
