"""Voice router — audio upload → transcription → chatbot response."""

from fastapi import APIRouter, UploadFile, File, Form  # type: ignore
from services.voice_service import transcribe_audio  # type: ignore
from services.nlp_service import analyze_sentiment, generate_response, detect_distress  # type: ignore

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/transcribe")
async def transcribe_and_respond(
    audio: UploadFile = File(...),
    user_id: str = Form(default=None),
):
    audio_bytes = await audio.read()
    content_type = audio.content_type or "audio/wav"

    transcription = transcribe_audio(audio_bytes, content_type)

    if "error" in transcription:
        return transcription

    text = transcription["text"]
    sentiment = analyze_sentiment(text)
    reply = generate_response(text, sentiment)
    distress = detect_distress(text)

    return {
        "transcription": text,
        "reply": reply,
        "sentiment": sentiment,
        "distress_detected": distress,
    }
