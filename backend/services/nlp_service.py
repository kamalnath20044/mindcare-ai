"""NLP service — sentiment analysis + context-aware AI therapist responses."""

from __future__ import annotations
from typing import Dict, Any, Optional, List
import random

# ---------------------------------------------------------------------------
# Lazy-loaded pipelines (downloaded on first call)
# ---------------------------------------------------------------------------
_sentiment_pipeline: Any = None
_text_gen_pipeline: Any = None


def _get_sentiment_pipeline() -> Any:
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        from transformers import pipeline  # type: ignore
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )
    return _sentiment_pipeline


def _get_text_gen_pipeline() -> Any:
    global _text_gen_pipeline
    if _text_gen_pipeline is None:
        from transformers import pipeline  # type: ignore
        _text_gen_pipeline = pipeline(
            "text2text-generation",
            model="facebook/blenderbot-400M-distill",
        )
    return _text_gen_pipeline


# ---------------------------------------------------------------------------
# AI Therapist — Curated therapeutic responses
# ---------------------------------------------------------------------------
THERAPEUTIC_RESPONSES = {
    "stress": {
        "empathy": [
            "I can hear that you're under a lot of pressure right now.",
            "It sounds like things have been really stressful for you.",
            "That does sound overwhelming. Thank you for sharing this with me.",
        ],
        "validation": [
            "It's completely natural to feel stressed in that situation.",
            "Your feelings of stress are valid and understandable.",
            "Anyone in your position would likely feel the same way.",
        ],
        "technique": [
            "Let's try something together — can you take 3 slow, deep breaths right now? In through your nose for 4 counts, out through your mouth for 6.",
            "One technique that helps is the 'brain dump' — write down everything on your mind for 5 minutes without filtering. It helps externalize the overwhelm.",
            "Try the 'smallest step' approach: what is the tiniest thing you could do right now to move forward? Sometimes just one small action breaks the paralysis.",
        ],
    },
    "anxiety": {
        "empathy": [
            "I understand how uncomfortable anxiety can feel — like your mind won't stop racing.",
            "Anxiety can make everything feel urgent and scary. I hear you.",
            "That sounds really difficult to deal with. Thank you for trusting me with this.",
        ],
        "validation": [
            "Anxiety is your brain trying to protect you, even when there's no real danger.",
            "What you're experiencing is very common, and there's no shame in feeling this way.",
            "Many people struggle with similar feelings. You're not alone in this.",
        ],
        "technique": [
            "Let's try grounding together: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.",
            "Try labeling your anxiety: say to yourself 'I notice I'm feeling anxious.' This creates distance between you and the feeling.",
            "Progressive muscle relaxation can help: starting from your toes, tense each muscle group for 5 seconds, then release. Work up to your shoulders.",
        ],
    },
    "sad": {
        "empathy": [
            "I'm sorry you're going through this. Sadness can feel really heavy.",
            "It takes courage to acknowledge when we're feeling down. I'm glad you told me.",
            "I can sense this is weighing on you deeply. I'm here to listen.",
        ],
        "validation": [
            "Sadness is a natural human emotion — it tells us something important to us is affected.",
            "It's okay to feel sad. You don't have to 'fix' it right away.",
            "Your feelings are real and they matter. Don't dismiss what you're going through.",
        ],
        "technique": [
            "When sadness feels heavy, gentle movement can help — even a 5 minute walk can shift your state slightly.",
            "Try writing a letter to yourself as if you were your own best friend. What would you say?",
            "Sometimes sadness needs to be felt, not fixed. Allow yourself to sit with it for a few minutes without judgment.",
        ],
    },
    "happy": {
        "empathy": [
            "That's wonderful to hear! 😊 I'm happy you're feeling good.",
            "It's great that you're in a positive space right now!",
            "I love hearing this! Positive moments are worth celebrating.",
        ],
        "validation": [
            "Savor this feeling — positive emotions are important for your well-being.",
            "You deserve to feel happy. Don't let anyone tell you otherwise.",
            "This is a great sign of emotional resilience.",
        ],
        "technique": [
            "To make this positive feeling last longer, try writing down what contributed to it. Gratitude journaling boosts long-term happiness.",
            "Consider sharing your good mood with someone — acts of kindness during happy moments amplify the positivity.",
            "Take a mental snapshot of this moment. You can revisit it later when things feel tough.",
        ],
    },
    "angry": {
        "empathy": [
            "I can feel the frustration in your words. That sounds really aggravating.",
            "Anger is a powerful emotion, and I understand why you'd feel that way.",
            "It's clear this situation has really gotten to you. That's understandable.",
        ],
        "validation": [
            "Anger often signals that a boundary has been crossed or something feels unfair.",
            "Your frustration is valid. It's important to acknowledge it rather than suppress it.",
            "Feeling angry doesn't make you a bad person — it makes you human.",
        ],
        "technique": [
            "When anger rises, try the STOP technique: Stop, Take a breath, Observe your body sensations, Proceed with awareness.",
            "Physical release helps with anger — try squeezing a stress ball, going for a brisk walk, or doing 10 pushups.",
            "Write it out — putting angry thoughts on paper can help you process them without saying something you might regret.",
        ],
    },
    "default": {
        "empathy": [
            "Thank you for sharing that with me. I'm here to listen.",
            "I appreciate you opening up. How does that make you feel?",
            "I'm glad you felt comfortable telling me that.",
        ],
        "validation": [
            "Your feelings, whatever they are, are valid and important.",
            "There's no right or wrong way to feel. Everything you experience matters.",
            "Take things one step at a time. There's no rush.",
        ],
        "technique": [
            "A check-in question: on a scale of 1-10, how would you rate your overall well-being right now?",
            "Try this: close your eyes for 30 seconds and just breathe. Notice how your body feels.",
            "Consider keeping a mood journal — tracking your emotions can reveal helpful patterns over time.",
        ],
    },
}

KEYWORDS_MAP = {
    "stress": ["stress", "stressed", "pressure", "overwhelm", "burnout", "tired", "exhausted", "overwork", "deadline"],
    "anxiety": ["anxious", "anxiety", "worried", "worry", "panic", "nervous", "fear", "scared", "dread", "uneasy"],
    "sad": ["sad", "depressed", "unhappy", "lonely", "down", "hopeless", "cry", "crying", "grief", "heartbroken", "empty"],
    "happy": ["happy", "great", "good", "wonderful", "amazing", "fantastic", "joy", "excited", "grateful", "blessed"],
    "angry": ["angry", "furious", "mad", "irritated", "annoyed", "frustrated", "rage", "furious", "livid"],
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
    """Return sentiment label and confidence score."""
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
    
    When therapist_mode is True, generates structured therapeutic responses
    with empathy, validation, and actionable techniques.
    """
    category = _detect_keyword_category(user_message)

    if therapist_mode:
        return _generate_therapist_response(user_message, category, context)

    # Standard mode — use generative model
    return _generate_standard_response(user_message, category, context)


def _generate_therapist_response(message: str, category: str, context: str) -> str:
    """Generate a structured AI Therapist response."""
    responses = THERAPEUTIC_RESPONSES.get(category, THERAPEUTIC_RESPONSES["default"])

    empathy = random.choice(responses["empathy"])
    validation = random.choice(responses["validation"])
    technique = random.choice(responses["technique"])

    # Build contextual awareness
    context_note = ""
    if context:
        line_count = len(context.strip().split("\n"))
        if line_count > 4:
            context_note = "\n\nI've been following our conversation, and I want you to know I'm paying attention to everything you've shared. "

    # Also try the generative model for a more natural touch
    generated_part = ""
    try:
        pipe = _get_text_gen_pipeline()
        prompt = message[:128]  # type: ignore
        if context:
            prompt = f"{context[-200:]}\nUser: {message[:100]}"  # type: ignore
        gen = pipe(prompt[:256], max_length=100)[0]["generated_text"]  # type: ignore
        gen = gen.strip()
        if len(gen) > 15 and not gen.startswith("I'm"):
            generated_part = f"\n\n{gen}"
    except Exception:
        # BlenderBot not available — use curated responses only (still excellent)
        pass

    # Compose the full therapeutic response
    response = f"{empathy} {validation}{context_note}{generated_part}\n\n💡 **Try this:** {technique}"
    return response


def _generate_standard_response(message: str, category: str, context: str) -> str:
    """Generate a standard non-therapist response."""
    try:
        pipe = _get_text_gen_pipeline()
        generated = pipe(message[:128], max_length=128)[0]["generated_text"]  # type: ignore
        generated = generated.strip()
        if len(generated) > 10:
            tip = random.choice(THERAPEUTIC_RESPONSES.get(category, THERAPEUTIC_RESPONSES["default"])["technique"])
            return f"{generated}\n\n💡 {tip}"
    except Exception:
        pass

    return random.choice(THERAPEUTIC_RESPONSES.get(category, THERAPEUTIC_RESPONSES["default"])["empathy"])


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

    # Map sentiment + keywords to a more nuanced emotion
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
