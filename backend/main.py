"""FastAPI entry point — AI-Driven Mental Health Support Chatbot Backend v3.0."""

import os
from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from routers import chat, emotion, voice, mood, wellness, alerts, auth, followup, analytics  # type: ignore

app = FastAPI(
    title="MindCare AI — Mental Health Support Platform",
    description=(
        "AI-driven mental health support system with context-aware chatbot, "
        "crisis detection, personalization engine, follow-up system, facial "
        "emotion detection, mood tracking, analytics dashboard, and more."
    ),
    version="3.0.0",
)

# CORS — allow dev + production origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

# Add production origins from env
PROD_FRONTEND = os.getenv("FRONTEND_URL", "")
if PROD_FRONTEND:
    ALLOWED_ORIGINS.append(PROD_FRONTEND)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(emotion.router)
app.include_router(voice.router)
app.include_router(mood.router)
app.include_router(wellness.router)
app.include_router(alerts.router)
app.include_router(followup.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    return {
        "service": "MindCare AI — Mental Health Support Platform",
        "version": "3.0.0",
        "status": "running",
        "problem_statement": "AI chatbots + ML to address depression symptom alleviation, attrition, and follow-up loss",
        "features": [
            "Context-Aware AI Therapist",
            "Crisis Detection & Safety Protocol",
            "Personalization Engine",
            "Follow-Up System (Anti-Attrition)",
            "Engagement Streaks",
            "Chat Memory (Persistent)",
            "Facial Emotion Detection (OpenCV + TensorFlow)",
            "Voice Assistant",
            "Mood Tracking & Analytics",
            "Smart Alerts & Recommendations",
            "Wellness Tools",
            "JWT Authentication",
            "Supabase Database Integration",
        ],
        "api_docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "3.0.0"}
