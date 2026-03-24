"""Voice service — speech-to-text using SpeechRecognition."""

from __future__ import annotations

import os
import shutil
import tempfile
import speech_recognition as sr  # type: ignore
from pydub import AudioSegment  # type: ignore

# Ensure pydub can find ffmpeg even before a shell restart
_FFMPEG_WINGET = os.path.expanduser(
    r"~\AppData\Local\Microsoft\WinGet\Packages"
)
for _root, _dirs, _files in os.walk(_FFMPEG_WINGET):
    if "ffmpeg.exe" in _files:
        AudioSegment.converter = os.path.join(_root, "ffmpeg.exe")  # type: ignore
        break
else:
    # Fall back to PATH lookup
    _found = shutil.which("ffmpeg")
    if _found:
        AudioSegment.converter = _found  # type: ignore


recognizer = sr.Recognizer()


def _convert_to_wav(src_path: str, src_format: str) -> str:
    """Convert an audio file to WAV format using pydub and return the WAV path."""
    audio_segment = AudioSegment.from_file(src_path, format=src_format)  # type: ignore
    wav_path = src_path.rsplit(".", 1)[0] + ".wav"
    audio_segment.export(wav_path, format="wav")  # type: ignore
    return wav_path


def transcribe_audio(audio_bytes: bytes, content_type: str = "audio/wav") -> dict:  # type: ignore
    """Convert audio bytes to text via Google Web Speech API.

    Accepts raw WAV / WEBM bytes.  Returns dict with 'text' or 'error'.
    """
    tmp_path = None
    wav_path = None
    try:
        # Determine file format from content type
        is_webm = "webm" in content_type
        suffix = ".webm" if is_webm else ".wav"

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(audio_bytes)
        tmp.close()
        tmp_path = tmp.name

        # Convert non-WAV formats to WAV so SpeechRecognition can read them
        if is_webm:
            wav_path = _convert_to_wav(tmp_path, "webm")
        else:
            wav_path = tmp_path

        with sr.AudioFile(wav_path) as source:  # type: ignore
            audio_data = recognizer.record(source)  # type: ignore

        text = recognizer.recognize_google(audio_data)  # type: ignore
        return {"text": text}

    except sr.UnknownValueError:
        return {"error": "Could not understand the audio. Please try again."}
    except sr.RequestError as e:
        return {"error": f"Speech recognition service error: {e}"}
    except Exception as e:
        return {"error": f"Audio processing error: {str(e)}"}
    finally:
        # Clean up temp files
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if wav_path and wav_path != tmp_path and os.path.exists(wav_path):
            os.unlink(wav_path)
