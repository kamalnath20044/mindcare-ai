"""Assessment Service — PHQ-9 (depression) and GAD-7 (anxiety) scoring.

Implements validated clinical questionnaires for tracking mental health
severity over time. Scores are stored and analyzed for trends.
"""

from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime, timedelta


# ─── PHQ-9 Questions ───
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading or watching TV",
    "Moving or speaking so slowly that other people noticed, or being so fidgety/restless",
    "Thoughts that you would be better off dead, or of hurting yourself",
]

# ─── GAD-7 Questions ───
GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen",
]

# Answer options for both assessments
ANSWER_OPTIONS = [
    {"value": 0, "label": "Not at all"},
    {"value": 1, "label": "Several days"},
    {"value": 2, "label": "More than half the days"},
    {"value": 3, "label": "Nearly every day"},
]


def score_phq9(answers: List[int]) -> Dict[str, Any]:
    """Score a PHQ-9 assessment.
    
    Args:
        answers: List of 9 integers (0-3) corresponding to each question.
    
    Returns:
        Dict with total_score, severity, interpretation, and recommendations.
    """
    if len(answers) != 9:
        raise ValueError("PHQ-9 requires exactly 9 answers")
    if not all(0 <= a <= 3 for a in answers):
        raise ValueError("Each answer must be between 0 and 3")

    total = sum(answers)

    if total <= 4:
        severity = "none"
        interpretation = "Minimal depression symptoms"
        recommendation = "Continue monitoring. Maintain your current self-care routine."
        color = "#4caf50"
    elif total <= 9:
        severity = "mild"
        interpretation = "Mild depression symptoms"
        recommendation = "Consider watchful waiting. Self-care strategies and CBT exercises may help. Re-assess in 2 weeks."
        color = "#ff9800"
    elif total <= 14:
        severity = "moderate"
        interpretation = "Moderate depression symptoms"
        recommendation = "A treatment plan is recommended. Consider talking to a mental health professional. CBT techniques can be very helpful."
        color = "#ff5722"
    elif total <= 19:
        severity = "moderately_severe"
        interpretation = "Moderately severe depression symptoms"
        recommendation = "Active treatment with therapy and/or medication is strongly recommended. Please consult a mental health professional."
        color = "#f44336"
    else:
        severity = "severe"
        interpretation = "Severe depression symptoms"
        recommendation = "Immediate intervention is recommended. Please reach out to a mental health professional as soon as possible."
        color = "#d32f2f"

    # Check for suicidal ideation (Q9)
    suicidal_flag = answers[8] > 0

    return {
        "total_score": total,
        "severity": severity,
        "interpretation": interpretation,
        "recommendation": recommendation,
        "suicidal_ideation": suicidal_flag,
        "color": color,
        "max_score": 27,
        "questions": [
            {"question": q, "answer": a, "answer_label": ANSWER_OPTIONS[a]["label"]}
            for q, a in zip(PHQ9_QUESTIONS, answers)
        ],
    }


def score_gad7(answers: List[int]) -> Dict[str, Any]:
    """Score a GAD-7 assessment.
    
    Args:
        answers: List of 7 integers (0-3) corresponding to each question.
    
    Returns:
        Dict with total_score, severity, interpretation, and recommendations.
    """
    if len(answers) != 7:
        raise ValueError("GAD-7 requires exactly 7 answers")
    if not all(0 <= a <= 3 for a in answers):
        raise ValueError("Each answer must be between 0 and 3")

    total = sum(answers)

    if total <= 4:
        severity = "none"
        interpretation = "Minimal anxiety symptoms"
        recommendation = "No clinical intervention needed. Continue with self-care and mindfulness practices."
        color = "#4caf50"
    elif total <= 9:
        severity = "mild"
        interpretation = "Mild anxiety symptoms"
        recommendation = "Monitor your anxiety levels. Grounding techniques and breathing exercises can help. Re-assess in 2 weeks."
        color = "#ff9800"
    elif total <= 14:
        severity = "moderate"
        interpretation = "Moderate anxiety symptoms"
        recommendation = "Consider professional evaluation. CBT techniques focused on anxiety management are recommended."
        color = "#ff5722"
    else:
        severity = "severe"
        interpretation = "Severe anxiety symptoms"
        recommendation = "Active treatment is strongly recommended. Please consult a mental health professional for evaluation and support."
        color = "#d32f2f"

    return {
        "total_score": total,
        "severity": severity,
        "interpretation": interpretation,
        "recommendation": recommendation,
        "color": color,
        "max_score": 21,
        "questions": [
            {"question": q, "answer": a, "answer_label": ANSWER_OPTIONS[a]["label"]}
            for q, a in zip(GAD7_QUESTIONS, answers)
        ],
    }


def save_phq9(user_id: str, answers: List[int]) -> Dict[str, Any]:
    """Score and persist a PHQ-9 assessment."""
    result = score_phq9(answers)
    record = {
        "user_id": user_id,
        **{f"q{i+1}": a for i, a in enumerate(answers)},
        "total_score": result["total_score"],
        "severity": result["severity"],
    }
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("phq9_entries").insert(record).execute()
    except Exception:
        pass

    # Trigger alert if severe
    if result["severity"] in ("moderately_severe", "severe"):
        _trigger_assessment_alert(user_id, "phq9", result)

    return result


def save_gad7(user_id: str, answers: List[int]) -> Dict[str, Any]:
    """Score and persist a GAD-7 assessment."""
    result = score_gad7(answers)
    record = {
        "user_id": user_id,
        **{f"q{i+1}": a for i, a in enumerate(answers)},
        "total_score": result["total_score"],
        "severity": result["severity"],
    }
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("gad7_entries").insert(record).execute()
    except Exception:
        pass

    if result["severity"] == "severe":
        _trigger_assessment_alert(user_id, "gad7", result)

    return result


def get_phq9_history(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get PHQ-9 assessment history for a user."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("phq9_entries")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data
    except Exception:
        return []


def get_gad7_history(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get GAD-7 assessment history for a user."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = (
            sb.table("gad7_entries")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data
    except Exception:
        return []


def get_assessment_trends(user_id: str) -> Dict[str, Any]:
    """Get combined assessment trends for dashboard display."""
    phq9_data = get_phq9_history(user_id)
    gad7_data = get_gad7_history(user_id)

    trends: Dict[str, Any] = {
        "phq9": {"entries": phq9_data, "trend": "stable", "latest_score": None, "latest_severity": None},
        "gad7": {"entries": gad7_data, "trend": "stable", "latest_score": None, "latest_severity": None},
    }

    if phq9_data:
        trends["phq9"]["latest_score"] = phq9_data[0].get("total_score")
        trends["phq9"]["latest_severity"] = phq9_data[0].get("severity")
        if len(phq9_data) >= 2:
            recent = phq9_data[0]["total_score"]
            previous = phq9_data[1]["total_score"]
            if recent > previous + 3:
                trends["phq9"]["trend"] = "worsening"
            elif recent < previous - 3:
                trends["phq9"]["trend"] = "improving"

    if gad7_data:
        trends["gad7"]["latest_score"] = gad7_data[0].get("total_score")
        trends["gad7"]["latest_severity"] = gad7_data[0].get("severity")
        if len(gad7_data) >= 2:
            recent = gad7_data[0]["total_score"]
            previous = gad7_data[1]["total_score"]
            if recent > previous + 2:
                trends["gad7"]["trend"] = "worsening"
            elif recent < previous - 2:
                trends["gad7"]["trend"] = "improving"

    return trends


def get_questions(assessment_type: str) -> Dict[str, Any]:
    """Get questions for a specific assessment type."""
    if assessment_type == "phq9":
        return {
            "type": "phq9",
            "title": "PHQ-9 Depression Screening",
            "description": "Over the last 2 weeks, how often have you been bothered by any of the following problems?",
            "questions": PHQ9_QUESTIONS,
            "options": ANSWER_OPTIONS,
        }
    elif assessment_type == "gad7":
        return {
            "type": "gad7",
            "title": "GAD-7 Anxiety Screening",
            "description": "Over the last 2 weeks, how often have you been bothered by any of the following problems?",
            "questions": GAD7_QUESTIONS,
            "options": ANSWER_OPTIONS,
        }
    raise ValueError(f"Unknown assessment type: {assessment_type}")


def _trigger_assessment_alert(user_id: str, assessment_type: str, result: Dict[str, Any]) -> None:
    """Trigger a therapist alert for severe assessment scores."""
    try:
        from services.therapist_alert_service import send_alert  # type: ignore
        send_alert(
            user_id=user_id,
            alert_type=f"{assessment_type}_severe",
            risk_level="high" if result["severity"] in ("moderately_severe", "moderate") else "critical",
            context=f"{assessment_type.upper()} Score: {result['total_score']}/{result['max_score']} — Severity: {result['severity']}",
            trigger_data=result,
        )
    except Exception:
        pass
