"""Homework Service — CBT Homework Assignment Loop.

Assigns CBT-based tasks after each session, tracks completion,
and follows up in the next session. This is a core feedback mechanism
for therapeutic progress.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random


# ─── CBT Homework Task Library ───
HOMEWORK_LIBRARY = {
    "thought_record": [
        {
            "title": "Thought Record Sheet",
            "description": "When you notice a negative thought, write down: 1) The situation, 2) The automatic thought, 3) The emotion you felt (0-100%), 4) Evidence FOR the thought, 5) Evidence AGAINST the thought, 6) A balanced alternative thought. Do this for 3 negative thoughts this week.",
            "difficulty": "medium",
        },
        {
            "title": "Catch Your Inner Critic",
            "description": "For the next 3 days, notice when your inner critic speaks. Write down what it says, then respond as if you were talking to a dear friend in the same situation. Note the difference in tone.",
            "difficulty": "easy",
        },
    ],
    "behavioral_activation": [
        {
            "title": "Activity Scheduling",
            "description": "Plan and complete 3 activities this week that you used to enjoy but have stopped doing. Rate your mood before (1-10) and after (1-10) each activity. Notice if there's a difference.",
            "difficulty": "medium",
        },
        {
            "title": "The 5-Minute Start",
            "description": "Choose one task you've been avoiding. Commit to doing it for just 5 minutes. After 5 minutes, you can stop if you want. Record what happened — did you continue past 5 minutes?",
            "difficulty": "easy",
        },
    ],
    "grounding": [
        {
            "title": "Daily Grounding Practice",
            "description": "Practice the 5-4-3-2-1 technique twice daily (morning and evening): Notice 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. Write a brief note about how you felt before and after.",
            "difficulty": "easy",
        },
        {
            "title": "Sensory Awareness Walk",
            "description": "Take a 15-minute walk focusing entirely on your senses. No phone, no music. Notice textures, sounds, smells, and colors. Write 3 observations you wouldn't normally notice.",
            "difficulty": "medium",
        },
    ],
    "journaling": [
        {
            "title": "Emotion Journal",
            "description": "Each evening, write down: 1) Your strongest emotion today, 2) What triggered it, 3) How you responded, 4) What you might do differently next time. Do this for 5 days.",
            "difficulty": "easy",
        },
        {
            "title": "Letter to Future Self",
            "description": "Write a letter to yourself 6 months from now. Describe what you're going through, what you hope to change, and what strengths you want to remember about yourself.",
            "difficulty": "medium",
        },
    ],
    "breathing": [
        {
            "title": "Breathing Practice Streak",
            "description": "Practice 4-7-8 breathing (inhale 4s, hold 7s, exhale 8s) for 4 cycles, twice a day for 5 days. Track how you feel before and after each session on a 1-10 calm scale.",
            "difficulty": "easy",
        },
    ],
    "gratitude": [
        {
            "title": "Gratitude Jar",
            "description": "Each day, write one thing you're grateful for on a small piece of paper and put it in a jar (or a digital note). At the end of the week, read them all. Reflect on how this exercise affected your mood.",
            "difficulty": "easy",
        },
    ],
    "social": [
        {
            "title": "Connection Challenge",
            "description": "Reach out to 2 people you care about this week. It can be a text, call, or in-person visit. Afterward, write down how the interaction made you feel.",
            "difficulty": "medium",
        },
    ],
    "physical": [
        {
            "title": "Movement Prescription",
            "description": "Do 20 minutes of any physical activity on 3 different days this week. It can be walking, stretching, dancing — anything that gets you moving. Rate your mood before and after.",
            "difficulty": "easy",
        },
    ],
    "mindfulness": [
        {
            "title": "Mindful Eating Exercise",
            "description": "Choose one meal this week to eat mindfully: no screens, eat slowly, notice flavors, textures, and colors. Write 3 things you noticed that you usually miss.",
            "difficulty": "easy",
        },
        {
            "title": "Body Scan Meditation",
            "description": "Do a 10-minute body scan meditation each night before bed this week. Start from your toes and work up to your head, noticing sensations without judgment. Note any patterns you observe.",
            "difficulty": "medium",
        },
    ],
}


def assign_homework(
    user_id: str,
    category: str = "",
    emotion: str = "",
    difficulty: str = "easy",
) -> Dict[str, Any]:
    """Assign a homework task based on session context.
    
    Selects an appropriate task based on the user's emotional state
    and the CBT techniques discussed in the session.
    """
    # Determine category based on emotion if not specified
    if not category:
        emotion_to_category = {
            "stressed": "breathing",
            "anxious": "grounding",
            "sad": "behavioral_activation",
            "angry": "journaling",
            "happy": "gratitude",
            "neutral": "mindfulness",
        }
        category = emotion_to_category.get(emotion.lower(), random.choice(list(HOMEWORK_LIBRARY.keys())))

    # Get tasks for the category
    tasks = HOMEWORK_LIBRARY.get(category, HOMEWORK_LIBRARY["mindfulness"])
    
    # Filter by difficulty
    filtered = [t for t in tasks if t["difficulty"] == difficulty]
    if not filtered:
        filtered = tasks
    
    task = random.choice(filtered)
    due_at = (datetime.utcnow() + timedelta(days=7)).isoformat()

    record = {
        "user_id": user_id,
        "title": task["title"],
        "description": task["description"],
        "category": category,
        "difficulty": task["difficulty"],
        "status": "assigned",
        "due_at": due_at,
    }

    # Persist
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        result = sb.table("homework_assignments").insert(record).execute()
        if result.data:
            record["id"] = result.data[0].get("id")
    except Exception:
        pass

    return record


def get_homework(user_id: str, status: str = "") -> List[Dict[str, Any]]:
    """Get homework assignments for a user."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        query = sb.table("homework_assignments").select("*").eq("user_id", user_id).order("assigned_at", desc=True)
        if status:
            query = query.eq("status", status)
        result = query.limit(20).execute()
        return result.data
    except Exception:
        return []


def complete_homework(
    homework_id: int,
    completion_note: str = "",
    rating: int = 3,
) -> Dict[str, Any]:
    """Mark a homework assignment as completed."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("homework_assignments").update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "completion_note": completion_note,
            "rating": max(1, min(5, rating)),
        }).eq("id", homework_id).execute()
        return {"status": "ok", "message": "Homework completed! Great work! 🎉"}
    except Exception:
        return {"status": "error", "message": "Could not update homework status."}


def skip_homework(homework_id: int) -> Dict[str, Any]:
    """Mark a homework assignment as skipped."""
    try:
        from services.supabase_client import get_supabase  # type: ignore
        sb = get_supabase()
        sb.table("homework_assignments").update({
            "status": "skipped",
        }).eq("id", homework_id).execute()
        return {"status": "ok", "message": "Homework skipped. We'll try a different approach next time."}
    except Exception:
        return {"status": "error", "message": "Could not update homework status."}


def get_pending_homework_context(user_id: str) -> str:
    """Get pending/completed homework context for the chat AI."""
    pending = get_homework(user_id, status="assigned")
    completed = get_homework(user_id, status="completed")

    parts = []
    if pending:
        hw = pending[0]
        parts.append(f"The user has a pending homework: '{hw['title']}' (Category: {hw['category']}). Ask about their progress.")

    if completed:
        hw = completed[0]
        note = hw.get("completion_note", "")
        rating = hw.get("rating", "")
        parts.append(
            f"The user recently completed: '{hw['title']}'"
            + (f" — they rated it {rating}/5" if rating else "")
            + (f" and noted: '{note[:100]}'" if note else "")
            + ". Acknowledge their effort!"
        )

    return " ".join(parts)


def get_homework_stats(user_id: str) -> Dict[str, Any]:
    """Get homework completion statistics."""
    all_hw = get_homework(user_id)
    if not all_hw:
        return {"total": 0, "completed": 0, "skipped": 0, "pending": 0, "completion_rate": 0}

    completed = sum(1 for h in all_hw if h.get("status") == "completed")
    skipped = sum(1 for h in all_hw if h.get("status") == "skipped")
    pending = sum(1 for h in all_hw if h.get("status") in ("assigned", "in_progress"))
    total = len(all_hw)

    avg_rating = 0
    rated = [h.get("rating", 0) for h in all_hw if h.get("rating")]
    if rated:
        avg_rating = round(sum(rated) / len(rated), 1)

    return {
        "total": total,
        "completed": completed,
        "skipped": skipped,
        "pending": pending,
        "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
        "avg_rating": avg_rating,
    }
