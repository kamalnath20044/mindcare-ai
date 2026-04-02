"""APScheduler Background Jobs — follow-ups, alerts, and weekly assessments.

Runs recurring jobs to:
1. Check inactive users and trigger follow-ups (anti-attrition)
2. Re-alert therapists for unacknowledged alerts (24h)
3. Remind users for weekly assessments
"""

from __future__ import annotations
from datetime import datetime
import os


def start_scheduler():
    """Start the APScheduler with all background jobs.
    
    Call this from main.py on application startup.
    """
    try:
        from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
        from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

        scheduler = BackgroundScheduler()

        # Run follow-up check every 6 hours
        scheduler.add_job(
            check_inactive_users,
            IntervalTrigger(hours=6),
            id="check_inactive_users",
            name="Check inactive users for follow-ups",
            replace_existing=True,
        )

        # Re-alert for stale therapist alerts every 4 hours
        scheduler.add_job(
            resend_stale_alerts,
            IntervalTrigger(hours=4),
            id="resend_stale_alerts",
            name="Re-send unacknowledged therapist alerts",
            replace_existing=True,
        )

        # Weekly assessment reminder every Monday at 9 AM UTC
        scheduler.add_job(
            send_assessment_reminders,
            IntervalTrigger(weeks=1),
            id="assessment_reminders",
            name="Send weekly assessment reminders",
            replace_existing=True,
        )

        scheduler.start()
        print("[SCHEDULER] Background jobs started successfully")
        return scheduler

    except ImportError:
        print("[SCHEDULER] APScheduler not installed — background jobs disabled")
        return None
    except Exception as e:
        print(f"[SCHEDULER] Failed to start: {e}")
        return None


def check_inactive_users():
    """Check all users for inactivity and generate follow-ups."""
    print(f"[JOB] Checking inactive users at {datetime.utcnow().isoformat()}")
    try:
        from services.supabase_client import get_supabase  # type: ignore
        from services.followup_service import generate_followup  # type: ignore

        sb = get_supabase()
        users = sb.table("profiles").select("id, last_active_at").execute()

        if not users.data:
            return

        followups_generated = 0
        for user in users.data:
            result = generate_followup(user["id"])
            if result:
                followups_generated += 1

        print(f"[JOB] Generated {followups_generated} follow-up(s)")

    except Exception as e:
        print(f"[JOB] Inactive user check failed: {e}")


def resend_stale_alerts():
    """Re-send therapist alerts that haven't been acknowledged in 24 hours."""
    print(f"[JOB] Checking stale alerts at {datetime.utcnow().isoformat()}")
    try:
        from services.therapist_alert_service import get_stale_alerts, send_alert  # type: ignore

        stale = get_stale_alerts(hours=24)
        for alert in stale:
            send_alert(
                user_id=alert["user_id"],
                alert_type=alert["alert_type"],
                risk_level=alert["risk_level"],
                context=f"[RE-ALERT] {alert.get('context', 'Unacknowledged alert from 24+ hours ago')}",
            )

        if stale:
            print(f"[JOB] Re-sent {len(stale)} stale alert(s)")

    except Exception as e:
        print(f"[JOB] Stale alert check failed: {e}")


def send_assessment_reminders():
    """Send weekly assessment reminders to active users."""
    print(f"[JOB] Sending assessment reminders at {datetime.utcnow().isoformat()}")
    try:
        from services.supabase_client import get_supabase  # type: ignore
        from datetime import timedelta

        sb = get_supabase()
        # Get users active in the last 14 days
        since = (datetime.utcnow() - timedelta(days=14)).isoformat()
        users = sb.table("profiles").select("id").gte("last_active_at", since).execute()

        if not users.data:
            return

        reminders_sent = 0
        for user in users.data:
            user_id = user["id"]
            # Check if they already took an assessment this week
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            phq9 = sb.table("phq9_entries").select("id").eq("user_id", user_id).gte("created_at", week_ago).limit(1).execute()
            if not phq9.data:
                # Create a follow-up reminder
                sb.table("follow_ups").insert({
                    "user_id": user_id,
                    "type": "reminder",
                    "message": "📋 It's been a week since your last assessment. Taking the PHQ-9 helps us track your progress and provide better support.",
                    "priority": "normal",
                }).execute()
                reminders_sent += 1

        print(f"[JOB] Sent {reminders_sent} assessment reminder(s)")

    except Exception as e:
        print(f"[JOB] Assessment reminder failed: {e}")
