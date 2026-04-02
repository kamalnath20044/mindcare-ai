"""FastAPI entry point — MindCare AI Mental Health Support Platform v4.0.

Production-grade AI-driven mental health chatbot with:
- GPT-3.5 + LangChain CBT therapy engine
- DistilBERT sentiment analysis
- PHQ-9 / GAD-7 clinical assessments
- Composite risk scoring
- Session memory & summaries
- CBT homework loop
- Therapist alert system (SendGrid)
- Admin dashboard
- Rate limiting & input sanitization
- GDPR compliance
- APScheduler background jobs
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from routers import chat, mood, wellness, alerts, auth, followup, analytics  # type: ignore
from routers import assessment, homework, admin, gdpr  # type: ignore
from middleware.rate_limiter import RateLimiterMiddleware  # type: ignore
from config import RATE_LIMIT_PER_MINUTE  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — start/stop background services."""
    # Start APScheduler on startup
    scheduler = None
    try:
        from scheduler import start_scheduler  # type: ignore
        scheduler = start_scheduler()
    except Exception as e:
        print(f"[STARTUP] Scheduler failed: {e}")

    yield

    # Shutdown scheduler
    if scheduler:
        try:
            scheduler.shutdown()
        except Exception:
            pass


app = FastAPI(
    title="MindCare AI — Mental Health Support Platform",
    description=(
        "Production-grade AI-driven mental health support system with "
        "GPT-3.5 CBT therapy engine, clinical assessments (PHQ-9, GAD-7), "
        "composite risk scoring, therapist alerts, admin dashboard, "
        "session memory, homework loop, and GDPR compliance."
    ),
    version="4.0.0",
    lifespan=lifespan,
)

# ─── Rate Limiting Middleware ───
app.add_middleware(RateLimiterMiddleware, requests_per_minute=RATE_LIMIT_PER_MINUTE)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routers ───
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(mood.router)
app.include_router(wellness.router)
app.include_router(alerts.router)
app.include_router(followup.router)
app.include_router(analytics.router)
app.include_router(assessment.router)
app.include_router(homework.router)
app.include_router(admin.router)
app.include_router(gdpr.router)


@app.get("/")
async def root():
    return {
        "service": "MindCare AI — Mental Health Support Platform",
        "version": "4.0.0",
        "status": "running",
        "problem_statement": "AI chatbots + ML to address depression symptom alleviation, attrition, and follow-up loss",
        "architecture": {
            "frontend": "React 19 + Vite + Tailwind CSS",
            "backend": "FastAPI + JWT + APScheduler",
            "ai_ml": "LangChain + GPT-3.5 (CBT) + DistilBERT",
            "background": "APScheduler (follow-ups, alerts, reminders)",
            "data": "Supabase PostgreSQL",
        },
        "features": [
            "AI Virtual Companion (GPT-3.5 + CBT)",
            "DistilBERT Sentiment Analysis",
            "PHQ-9 Depression Screening",
            "GAD-7 Anxiety Screening",
            "Composite Risk Scoring",
            "Crisis Detection & Safety Protocol",
            "Session Memory & Summaries",
            "CBT Homework Loop",
            "Therapist Alert System (SendGrid)",
            "Admin/Therapist Dashboard",
            "Mood & Health Tracking",
            "Anti-Attrition Follow-Up System",
            "Rate Limiting & Input Sanitization",
            "GDPR Compliance (Export/Delete/Consent)",
            "JWT Authentication",
        ],
        "api_docs": "/docs",
    }


@app.get("/health")
async def health():
    gpt_status = "unknown"
    try:
        from services.gpt_service import is_gpt_available  # type: ignore
        gpt_status = "available" if is_gpt_available() else "fallback_mode"
    except Exception:
        gpt_status = "fallback_mode"

    return {"status": "healthy", "version": "4.0.0", "gpt": gpt_status}
