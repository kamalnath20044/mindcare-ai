"""NLP service — sentiment analysis + context-aware AI therapist responses.

Uses DistilBERT for sentiment analysis + GPT-3.5 via LangChain for responses.
Falls back to keyword-based analysis and curated responses when models are unavailable.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List

# ---------------------------------------------------------------------------
# Lazy-loaded sentiment pipeline (DistilBERT)
# ---------------------------------------------------------------------------
_sentiment_pipeline: Any = None


def _get_sentiment_pipeline() -> Any:
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        from transformers import pipeline  # type: ignore
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )
    return _sentiment_pipeline


KEYWORDS_MAP = {
    "stress": ["stress", "stressed", "pressure", "overwhelm", "burnout", "tired", "exhausted", "overwork", "deadline"],
    "anxiety": ["anxious", "anxiety", "worried", "worry", "panic", "nervous", "fear", "scared", "dread", "uneasy"],
    "sad": ["sad", "depressed", "unhappy", "lonely", "down", "hopeless", "cry", "crying", "grief", "heartbroken", "empty"],
    "happy": ["happy", "great", "good", "wonderful", "amazing", "fantastic", "joy", "excited", "grateful", "blessed"],
    "angry": ["angry", "furious", "mad", "irritated", "annoyed", "frustrated", "rage", "livid"],
}


def _detect_keyword_category(text: str) -> str:
    """Detect emotional category from keywords in text."""
    lower = text.lower()
    for category, keywords in KEYWORDS_MAP.items():
        for kw in keywords:
            if kw in lower:
                return category
    return "default"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Return sentiment label and confidence score using DistilBERT."""
    try:
        pipe = _get_sentiment_pipeline()
        result = pipe(text[:512])[0]  # type: ignore
        return {"label": result["label"], "score": round(result["score"], 4)}
    except Exception:
        # Fallback: keyword-based sentiment when transformers not available
        category = _detect_keyword_category(text)
        if category in ("happy",):
            return {"label": "POSITIVE", "score": 0.85}
        elif category in ("sad", "angry", "anxiety", "stress"):
            return {"label": "NEGATIVE", "score": 0.80}
        return {"label": "NEUTRAL", "score": 0.60}


def generate_response(
    user_message: str,
    sentiment: Dict[str, Any] | None = None,
    context: str = "",
    therapist_mode: bool = True,
) -> str:
    """Generate an empathetic, context-aware chatbot response.
    
    Uses GPT-3.5 + LangChain when available, falls back to curated CBT responses.
    """
    from services.gpt_service import generate_gpt_response  # type: ignore

    # Build chat history context from memory
    chat_history = context if context else ""

    # Get user context from personalization
    user_context = ""
    if context:
        user_context = context

    return generate_gpt_response(
        user_message=user_message,
        user_context=user_context,
        chat_history=chat_history,
        sentiment=sentiment,
    )


def detect_distress(text: str) -> bool:
    """Return True if the message suggests severe emotional distress."""
    distress_phrases = [
        "kill myself", "end my life", "suicide", "want to die",
        "self harm", "self-harm", "hurt myself", "no reason to live",
        "can't go on", "give up on life", "don't want to exist",
        "better off dead", "nobody cares", "no hope",
    ]
    lower = text.lower()
    return any(phrase in lower for phrase in distress_phrases)


def analyze_emotion_from_text(text: str) -> Dict[str, Any]:
    """Perform deeper text-based emotion analysis."""
    category = _detect_keyword_category(text)
    sentiment = analyze_sentiment(text)

    emotion_map = {
        "stress": "Stressed",
        "anxiety": "Anxious",
        "sad": "Sad",
        "happy": "Happy",
        "angry": "Angry",
        "default": "Neutral",
    }

    intensity = "moderate"
    score = sentiment.get("score", 0.5)
    if score > 0.9:
        intensity = "strong"
    elif score < 0.6:
        intensity = "mild"

    return {
        "emotion": emotion_map.get(category, "Neutral"),
        "category": category,
        "intensity": intensity,
        "sentiment": sentiment,
    }
