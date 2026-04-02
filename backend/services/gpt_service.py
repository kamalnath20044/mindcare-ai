"""GPT Service — LangChain + OpenAI GPT-3.5 CBT-based AI Therapist.

Replaces BlenderBot with a production-grade conversational AI engine
that uses Cognitive Behavioral Therapy (CBT) techniques.
Falls back to curated therapeutic responses when OpenAI is unavailable.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
import random
import os

# ─── CBT System Prompt ───
CBT_SYSTEM_PROMPT = """You are MindCare AI, a compassionate and professionally-trained AI mental health companion.
You use Cognitive Behavioral Therapy (CBT) techniques to support users.

RULES (STRICT):
1. NEVER diagnose. You are NOT a doctor or licensed therapist.
2. Be empathetic, warm, and human — never robotic or clinical.
3. Use CBT techniques naturally:
   - Thought reframing: Help users challenge negative automatic thoughts
   - Behavioral activation: Encourage small, achievable positive actions
   - Grounding techniques: 5-4-3-2-1 sensory, deep breathing, body scan
   - Cognitive restructuring: Identify cognitive distortions
   - Socratic questioning: Ask open-ended questions to guide self-discovery
4. Keep responses under 120 words.
5. ALWAYS end with a thoughtful question to keep the conversation going.
6. Suggest professional help when the user shows persistent distress.
7. Validate emotions before offering techniques.
8. Reference previous conversation context when available.
9. Never minimize or dismiss what the user is feeling.
10. Use warm language with occasional emoji (1-2 max per response).

RESPONSE STRUCTURE:
- Start with empathy/validation (1-2 sentences)
- Offer insight or technique (2-3 sentences)
- End with an open-ended question

CONTEXT ABOUT THIS USER:
{user_context}

CONVERSATION HISTORY:
{chat_history}
"""

# ─── LangChain + OpenAI Integration ───
_chain = None
_openai_available: bool | None = None


def _init_langchain():
    """Initialize LangChain with OpenAI GPT-3.5."""
    global _chain, _openai_available
    try:
        from config import OPENAI_API_KEY  # type: ignore
        if not OPENAI_API_KEY:
            _openai_available = False
            return None

        from langchain_openai import ChatOpenAI  # type: ignore
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder  # type: ignore
        from langchain.schema import SystemMessage, HumanMessage  # type: ignore

        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=200,
            api_key=OPENAI_API_KEY,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", CBT_SYSTEM_PROMPT),
            ("human", "{user_message}"),
        ])

        _chain = prompt | llm
        _openai_available = True
        return _chain

    except Exception as e:
        print(f"[GPT] LangChain initialization failed: {e}")
        _openai_available = False
        return None


def _get_chain():
    """Get or initialize the LangChain chain."""
    global _chain
    if _chain is None:
        _init_langchain()
    return _chain


# ─── Curated CBT Responses (Fallback) ───
CBT_RESPONSES = {
    "stress": {
        "empathy": [
            "I can hear that you're under a lot of pressure right now. That takes real strength to acknowledge.",
            "It sounds like things have been really stressful for you. I appreciate you sharing this with me.",
            "That does sound overwhelming. You're carrying a heavy load right now.",
        ],
        "technique": [
            "Let's try a CBT technique called 'cognitive restructuring.' When you think 'I can't handle this,' try reframing it as 'I'm finding this challenging, but I've handled difficult things before.' What's one time you overcame something tough?",
            "Here's a 'behavioral activation' idea: What's the smallest, most manageable step you could take right now to address one source of stress? Sometimes tiny actions break the cycle.",
            "Let's try box breathing together — inhale for 4 counts, hold 4, exhale 4, hold 4. This activates your parasympathetic nervous system. Can you try one cycle right now?",
        ],
    },
    "anxiety": {
        "empathy": [
            "I understand how uncomfortable anxiety can feel — like your mind won't stop racing. That's really tough.",
            "Anxiety can make everything feel urgent and overwhelming. You're not alone in feeling this way.",
            "That sounds really difficult to deal with. Thank you for trusting me with this.",
        ],
        "technique": [
            "Let's try the 5-4-3-2-1 grounding technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. This anchors you to the present moment. What are 5 things you can see right now?",
            "In CBT, we call anxious thoughts 'cognitive distortions.' One common one is 'catastrophizing' — imagining the worst possible outcome. What's the actual evidence for your worry? And what's the most likely outcome?",
            "Try 'worry scheduling': Set aside 15 minutes later today to worry deliberately. If anxious thoughts come up before then, tell yourself 'I'll address this during worry time.' Would you like to try this?",
        ],
    },
    "sad": {
        "empathy": [
            "I'm sorry you're going through this. Sadness can feel really heavy. 💙",
            "It takes courage to acknowledge when we're feeling down. I'm glad you told me.",
            "I can sense this is weighing on you deeply. Your feelings are completely valid.",
        ],
        "technique": [
            "In CBT, we use 'behavioral activation' for sadness. Even small actions can shift your mood. What's one thing that used to bring you joy, even a tiny bit? Could you try it for just 5 minutes today?",
            "Let's try 'thought recording': Write down the sad thought, the evidence for it, the evidence against it, and a balanced alternative. What specific thought is loudest right now?",
            "Sometimes sadness is telling us something important. What do you think your sadness is trying to communicate? Understanding it can be the first step toward working through it.",
        ],
    },
    "happy": {
        "empathy": [
            "That's wonderful to hear! 😊 I'm genuinely happy you're feeling good.",
            "It's great that you're in a positive space right now! Let's make the most of it.",
            "I love hearing this! These positive moments are worth savoring.",
        ],
        "technique": [
            "To anchor this positive feeling, try 'gratitude journaling' — write down 3 specific things that contributed to your happiness today. This rewires your brain to notice more positives. What's one thing you're grateful for right now?",
            "In CBT, we call this 'positive data logging.' When you feel good, note what you did, who you were with, and where you were. This helps identify your 'happiness ingredients.' What contributed to this feeling?",
            "This is a great time to build 'resilience reserves.' Take a mental snapshot of how you feel right now. You can revisit this memory during tough times. What makes this moment special?",
        ],
    },
    "angry": {
        "empathy": [
            "I can feel the frustration in your words. That sounds really aggravating.",
            "Anger is a powerful emotion, and yours sounds justified. I hear you.",
            "It's clear this situation has really gotten to you. That's completely understandable.",
        ],
        "technique": [
            "In CBT, we use the STOP technique for anger: Stop what you're doing, Take three deep breaths, Observe your body sensations, Proceed with awareness. Can you take those three breaths right now?",
            "Let's try 'cognitive restructuring' for anger. Sometimes we make assumptions about others' intentions. What might be an alternative explanation for what happened? Sometimes things aren't personal.",
            "A powerful anger management technique is 'the letter you never send.' Write down exactly what you're angry about, uncensored. Then read it tomorrow with fresh eyes. Would you like to try this?",
        ],
    },
    "default": {
        "empathy": [
            "Thank you for sharing that with me. I'm here and I'm listening. 💚",
            "I appreciate you opening up. How does that make you feel?",
            "I hear you, and what you're saying is important. Let's explore it together.",
            "Thank you for being honest with me about this. That takes courage.",
        ],
        "technique": [
            "A helpful CBT check-in: On a scale of 1-10, how would you rate your overall well-being right now? This helps us track your progress over time. What number feels right?",
            "Let's try a mindful moment: Close your eyes for 30 seconds, focus on your breath, and notice any sensations in your body without judgment. What did you notice?",
            "Here's a CBT exercise: What's one negative thought you've had today? Now, what would you say to a close friend having that same thought? Often we're much kinder to others than ourselves.",
            "Consider the 'evidence technique': What's something you're worried about? What's the evidence it will happen? And what's the evidence it won't? This helps put things in perspective.",
        ],
    },
}

FOLLOWUP_RESPONSES = [
    "That's a really insightful observation. What do you think led you to see it that way?",
    "I'm noticing a pattern here. Would you like to explore what might be driving these feelings?",
    "Building on what you said — how has that been affecting your daily life?",
    "That connects to something you mentioned earlier. It sounds like this theme is important to you.",
    "Thank you for going deeper on this. What feels like the most important thing to address right now?",
    "I can tell you've been thinking about this carefully. What would your ideal outcome look like?",
    "You're showing real self-awareness by recognizing that. How does naming it out loud feel?",
    "That's really brave to acknowledge. What small step could you take today to start shifting this?",
]

KEYWORDS_MAP = {
    "stress": ["stress", "stressed", "pressure", "overwhelm", "burnout", "tired", "exhausted", "overwork", "deadline", "overloaded"],
    "anxiety": ["anxious", "anxiety", "worried", "worry", "panic", "nervous", "fear", "scared", "dread", "uneasy", "restless"],
    "sad": ["sad", "depressed", "unhappy", "lonely", "down", "hopeless", "cry", "crying", "grief", "heartbroken", "empty", "miserable"],
    "happy": ["happy", "great", "good", "wonderful", "amazing", "fantastic", "joy", "excited", "grateful", "blessed", "content", "proud"],
    "angry": ["angry", "furious", "mad", "irritated", "annoyed", "frustrated", "rage", "livid", "resentful"],
}


def _detect_keyword_category(text: str) -> str:
    """Detect emotional category from keywords in text."""
    lower = text.lower()
    for category, keywords in KEYWORDS_MAP.items():
        for kw in keywords:
            if kw in lower:
                return category
    return "default"


# ─── Public API ───

def generate_gpt_response(
    user_message: str,
    user_context: str = "",
    chat_history: str = "",
    sentiment: Dict[str, Any] | None = None,
) -> str:
    """Generate an AI therapist response using GPT-3.5 + LangChain.
    
    Falls back to curated CBT responses when OpenAI is unavailable.
    """
    # Try GPT first
    chain = _get_chain()
    if chain and _openai_available:
        try:
            result = chain.invoke({
                "user_context": user_context or "No prior context available.",
                "chat_history": chat_history or "This is the start of the conversation.",
                "user_message": user_message,
            })
            response = result.content if hasattr(result, "content") else str(result)
            if response and len(response) > 20:
                return response.strip()
        except Exception as e:
            print(f"[GPT] OpenAI call failed: {e}")

    # Fallback: curated CBT responses
    return _generate_fallback_response(user_message, user_context)


def _generate_fallback_response(message: str, context: str) -> str:
    """Generate a structured CBT response using curated templates."""
    category = _detect_keyword_category(message)
    responses = CBT_RESPONSES.get(category, CBT_RESPONSES["default"])
    has_prior_context = bool(context and len(context.strip().split("\n")) > 2)

    empathy = random.choice(responses["empathy"])
    technique = random.choice(responses["technique"])

    if has_prior_context:
        bridge = random.choice(FOLLOWUP_RESPONSES)
        return f"{empathy} {bridge}\n\n💡 **Try this:** {technique}"
    else:
        return f"{empathy}\n\n💡 **Try this:** {technique}"


def is_gpt_available() -> bool:
    """Check if GPT/OpenAI is configured and available."""
    if _openai_available is None:
        _init_langchain()
    return bool(_openai_available)
