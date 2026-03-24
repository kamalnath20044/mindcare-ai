"""Wellness router — mental health tips, exercises, and resources."""

from fastapi import APIRouter  # type: ignore
import random

router = APIRouter(prefix="/api/wellness", tags=["wellness"])

MEDITATION_EXERCISES = [
    {
        "title": "Body Scan Meditation",
        "duration": "10 minutes",
        "description": "Lie down comfortably and slowly bring your attention to each part of your body, starting from your toes and moving up to the top of your head. Notice any sensations without judgment.",
        "category": "meditation",
    },
    {
        "title": "Mindful Breathing",
        "duration": "5 minutes",
        "description": "Sit comfortably and focus on your breath. Inhale slowly for 4 counts, hold for 4 counts, exhale for 6 counts. Repeat and let your mind settle.",
        "category": "meditation",
    },
    {
        "title": "Loving-Kindness Meditation",
        "duration": "15 minutes",
        "description": "Close your eyes and repeat: 'May I be happy, may I be healthy, may I be safe.' Then extend the same wishes to loved ones, acquaintances, and all beings.",
        "category": "meditation",
    },
]

BREATHING_EXERCISES = [
    {
        "title": "4-7-8 Breathing",
        "description": "Inhale through your nose for 4 seconds, hold your breath for 7 seconds, exhale through your mouth for 8 seconds. Repeat 4 times.",
        "category": "breathing",
    },
    {
        "title": "Box Breathing",
        "description": "Inhale for 4 seconds, hold for 4 seconds, exhale for 4 seconds, hold for 4 seconds. Repeat for 5 minutes.",
        "category": "breathing",
    },
    {
        "title": "Diaphragmatic Breathing",
        "description": "Place one hand on your chest, another on your belly. Breathe deeply through your nose so your belly rises. Exhale slowly. Repeat 10 times.",
        "category": "breathing",
    },
]

MOTIVATIONAL_MESSAGES = [
    "You are stronger than you think. Every step forward, no matter how small, is progress. 💪",
    "It's okay to not be okay. What matters is that you're here and you're trying. 🌟",
    "Your feelings are valid. Take things one moment at a time. 🌈",
    "You deserve peace, happiness, and love — including from yourself. ❤️",
    "Difficult roads often lead to beautiful destinations. Keep going. 🌄",
    "You are not alone. There are people who care about you and want to help. 🤝",
    "Today is a new beginning. Be gentle with yourself. 🌱",
    "Courage doesn't mean you aren't afraid. It means you keep going despite the fear. 🦋",
    "Small acts of self-care add up. You're investing in your well-being. ✨",
    "Remember: storms don't last forever. Brighter days are ahead. ☀️",
]

RELAXATION_TIPS = [
    {
        "title": "Progressive Muscle Relaxation",
        "description": "Tense each muscle group for 5 seconds, then release. Start with your feet and work up to your face.",
        "category": "relaxation",
    },
    {
        "title": "Warm Bath or Shower",
        "description": "A warm bath or shower can lower cortisol levels and relax tense muscles. Add calming scents like lavender.",
        "category": "relaxation",
    },
    {
        "title": "Journaling",
        "description": "Write down your thoughts and feelings. It helps process emotions and can bring clarity to stressful situations.",
        "category": "relaxation",
    },
    {
        "title": "Listen to Calming Music",
        "description": "Put on some soft, instrumental music. Nature sounds and lo-fi beats can help reduce stress and anxiety.",
        "category": "relaxation",
    },
]

EMERGENCY_RESOURCES = [
    {"name": "iCall (India)", "number": "9152987821", "description": "Professional counselling service"},
    {"name": "Vandrevala Foundation", "number": "1860-2662-345", "description": "24/7 mental health helpline"},
    {"name": "NIMHANS", "number": "080-46110007", "description": "National Institute of Mental Health"},
    {"name": "Crisis Text Line", "number": "Text HOME to 741741", "description": "Free 24/7 crisis support via text"},
    {"name": "AASRA", "number": "91-22-27546669", "description": "24/7 crisis intervention centre"},
]


@router.get("/tips")
async def get_wellness_tips():
    return {
        "meditation": MEDITATION_EXERCISES,
        "breathing": BREATHING_EXERCISES,
        "relaxation": RELAXATION_TIPS,
        "motivational_message": random.choice(MOTIVATIONAL_MESSAGES),
    }


@router.get("/motivation")
async def get_motivation():
    return {"message": random.choice(MOTIVATIONAL_MESSAGES)}


@router.get("/emergency")
async def get_emergency_resources():
    return {"resources": EMERGENCY_RESOURCES}
