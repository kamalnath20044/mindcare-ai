"""Emotion detection router — webcam frame → emotion classification."""

from fastapi import APIRouter  # type: ignore
from pydantic import BaseModel  # type: ignore

router = APIRouter(prefix="/api/emotion", tags=["emotion"])


class EmotionRequest(BaseModel):
    image: str  # base64-encoded image (data URI or raw base64)
    user_id: str = None  # type: ignore


@router.post("/detect")
async def detect_emotion(req: EmotionRequest):
    try:
        from services.emotion_service import detect_emotion_from_base64  # type: ignore
        result = detect_emotion_from_base64(req.image)
    except Exception as e:
        result = {"emotion": "Neutral", "confidence": 0.0, "suggestion": "Emotion detection is currently unavailable.", "error": str(e)}

    # Persist result if successful and user_id provided
    if "error" not in result and req.user_id:
        try:
            from services.supabase_client import get_supabase  # type: ignore
            sb = get_supabase()
            sb.table("emotion_detections").insert({
                "user_id": req.user_id,
                "emotion": result["emotion"],
                "confidence": result["confidence"],
            }).execute()
        except Exception:
            pass

    return result
