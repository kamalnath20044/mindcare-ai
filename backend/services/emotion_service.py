"""Emotion detection service — OpenCV face detection + TensorFlow CNN classification."""

from __future__ import annotations

import base64
import io
import os

import cv2  # type: ignore
import numpy as np  # type: ignore
from PIL import Image  # type: ignore

# ---------------------------------------------------------------------------
# Emotion labels (FER-2013 order)
# ---------------------------------------------------------------------------
EMOTION_LABELS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

EMOTION_SUGGESTIONS = {
    "Happy": "You look happy! Keep doing what brings you joy. 😊",
    "Sad": "It looks like you may be feeling down. Consider talking to someone you trust, or try a calming breathing exercise. 💙",
    "Angry": "You seem frustrated. A short walk or a few deep breaths might help release that tension.",
    "Fear": "It looks like something might be worrying you. Grounding exercises can help — focus on what you can see, hear, and touch.",
    "Surprise": "You look surprised! I hope it's a pleasant surprise. 😄",
    "Disgust": "Something seems to be bothering you. It's okay to step away from what's causing discomfort.",
    "Neutral": "You seem calm and composed. Great time to reflect or journal about your day.",
}

# ---------------------------------------------------------------------------
# Lazy-loaded model & cascade
# ---------------------------------------------------------------------------
_model = None
_face_cascade = None


def _get_face_cascade():
    global _face_cascade
    if _face_cascade is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _face_cascade = cv2.CascadeClassifier(cascade_path)
    return _face_cascade


def _get_model():
    """Load TensorFlow / Keras emotion model.

    If no custom model file exists we create a simple CNN and return it
    (weights will be random — in production replace with a trained .h5).
    """
    global _model
    if _model is not None:
        return _model

    model_dir = os.path.join(os.path.dirname(__file__), "..", "models", "emotion_model")
    model_path = os.path.join(model_dir, "model.h5")

    try:
        import tensorflow as tf  # type: ignore

        if os.path.exists(model_path):
            _model = tf.keras.models.load_model(model_path)
        else:
            # Build a lightweight placeholder CNN (48×48 grayscale → 7 emotions)
            _model = tf.keras.Sequential(
                [
                    tf.keras.layers.Input(shape=(48, 48, 1)),
                    tf.keras.layers.Conv2D(32, (3, 3), activation="relu"),
                    tf.keras.layers.MaxPooling2D(2, 2),
                    tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
                    tf.keras.layers.MaxPooling2D(2, 2),
                    tf.keras.layers.Conv2D(128, (3, 3), activation="relu"),
                    tf.keras.layers.MaxPooling2D(2, 2),
                    tf.keras.layers.Flatten(),
                    tf.keras.layers.Dense(128, activation="relu"),
                    tf.keras.layers.Dropout(0.5),
                    tf.keras.layers.Dense(7, activation="softmax"),
                ]
            )
            _model.compile(
                optimizer="adam",
                loss="categorical_crossentropy",
                metrics=["accuracy"],
            )
            os.makedirs(model_dir, exist_ok=True)
            _model.save(model_path)
        return _model
    except Exception as e:
        print(f"[emotion_service] Model load error: {e}")
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_emotion_from_base64(image_b64: str) -> dict:
    """Detect the dominant emotion in a base64-encoded image.

    Flow:
        1. Decode base64 → PIL Image → NumPy array
        2. Convert to grayscale
        3. Detect face with Haar cascade
        4. Crop face region, resize to 48×48
        5. Run through CNN
        6. Return emotion label, confidence, and suggestion
        7. Frame data is NOT persisted — deleted after processing
    """
    # Decode image ---------------------------------------------------------
    try:
        # Strip data URI prefix if present
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        img_bytes = base64.b64decode(image_b64)
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        frame = np.array(pil_img)
    except Exception:
        return {"error": "Invalid image data."}

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Detect face ----------------------------------------------------------
    cascade = _get_face_cascade()
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return {"error": "No face detected. Please ensure your face is clearly visible."}

    # Take the largest face
    x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
    face_roi = gray[y : y + h, x : x + w]
    face_resized = cv2.resize(face_roi, (48, 48))

    # Predict emotion ------------------------------------------------------
    model = _get_model()
    if model is None:
        return {"emotion": "Neutral", "confidence": 0.0, "suggestion": EMOTION_SUGGESTIONS["Neutral"]}

    input_tensor = face_resized.astype("float32") / 255.0
    input_tensor = np.expand_dims(input_tensor, axis=(0, -1))  # (1, 48, 48, 1)

    predictions = model.predict(input_tensor, verbose=0)[0]
    emotion_idx = int(np.argmax(predictions))
    emotion_label = EMOTION_LABELS[emotion_idx]
    confidence = float(predictions[emotion_idx])

    # Frame data is local-only — nothing persisted beyond this function -----
    del frame, gray, face_roi, face_resized, img_bytes

    return {
        "emotion": emotion_label,
        "confidence": round(confidence, 4),  # type: ignore
        "suggestion": EMOTION_SUGGESTIONS.get(emotion_label, ""),
        "face_box": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
    }
