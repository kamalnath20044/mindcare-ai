"""Application configuration — loads environment variables."""

import os
from dotenv import load_dotenv  # type: ignore

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models", "emotion_model")
HAARCASCADE_PATH = os.path.join(
    BASE_DIR, "models", "haarcascade_frontalface_default.xml"
)
