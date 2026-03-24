"""Chat Memory Service — maintains conversation context for intelligent responses."""

from __future__ import annotations
from typing import Dict, List, Any
from collections import defaultdict
import time


class ChatMemory:
    """In-memory conversation history manager.
    
    Maintains per-user conversation context so the AI can respond
    intelligently based on previous messages in the session.
    """

    def __init__(self, max_history: int = 20, session_timeout: int = 3600):
        self._history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._timestamps: Dict[str, float] = {}
        self.max_history = max_history
        self.session_timeout = session_timeout  # seconds

    def _cleanup_expired(self, user_id: str) -> None:
        """Remove session if it's expired."""
        last = self._timestamps.get(user_id, 0)
        if time.time() - last > self.session_timeout:
            self._history[user_id] = []

    def add_message(self, user_id: str, role: str, content: str, metadata: Dict[str, Any] | None = None) -> None:
        """Add a message to the user's conversation history."""
        self._cleanup_expired(user_id)
        self._timestamps[user_id] = time.time()

        entry = {"role": role, "content": content, "timestamp": time.time()}
        if metadata:
            entry["metadata"] = metadata  # type: ignore

        self._history[user_id].append(entry)

        # Keep only the last N messages
        if len(self._history[user_id]) > self.max_history:
            self._history[user_id] = self._history[user_id][-self.max_history:]  # type: ignore

    def get_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the recent conversation history for a user."""
        self._cleanup_expired(user_id)
        return self._history[user_id][-limit:]  # type: ignore

    def get_context_summary(self, user_id: str) -> str:
        """Build a context string from recent conversation for the LLM."""
        history = self.get_history(user_id, limit=8)
        if not history:
            return ""

        lines = []
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content'][:200]}")

        return "\n".join(lines)

    def get_mood_trend(self, user_id: str) -> Dict[str, Any]:
        """Analyze recent conversation for mood patterns."""
        history = self.get_history(user_id, limit=15)
        if not history:
            return {"trend": "unknown", "messages_analyzed": 0}

        user_messages = [m for m in history if m.get("role") == "user"]
        sentiments = [m.get("metadata", {}).get("sentiment", "") for m in user_messages if m.get("metadata")]

        positive = sum(1 for s in sentiments if s == "POSITIVE")
        negative = sum(1 for s in sentiments if s == "NEGATIVE")
        total = len(sentiments)

        if total == 0:
            return {"trend": "unknown", "messages_analyzed": 0}

        if negative / total > 0.6:
            trend = "declining"
        elif positive / total > 0.6:
            trend = "improving"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "positive_count": positive,
            "negative_count": negative,
            "messages_analyzed": total,
        }

    def clear(self, user_id: str) -> None:
        """Clear conversation history for a user."""
        self._history[user_id] = []
        self._timestamps.pop(user_id, None)


# Global singleton
chat_memory = ChatMemory()
