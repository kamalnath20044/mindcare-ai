"""Application configuration — loads environment variables."""

import os
from dotenv import load_dotenv  # type: ignore

load_dotenv()

# ─── Supabase ───
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# ─── OpenAI (GPT-3.5) ───
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# ─── SendGrid (Therapist Alerts) ───
SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "alerts@mindcare-ai.com")
THERAPIST_DEFAULT_EMAIL: str = os.getenv("THERAPIST_DEFAULT_EMAIL", "")

# ─── Redis ───
REDIS_URL: str = os.getenv("REDIS_URL", "")

# ─── JWT ───
JWT_SECRET: str = os.getenv("JWT_SECRET", "mindcare-ai-secret-key-2024")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_SECONDS: int = 604800  # 7 days

# ─── Rate Limiting ───
RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))

# ─── Paths ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
