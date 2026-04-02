"""Input Sanitizer Middleware — protects against XSS and injection attacks.

Sanitizes user input in request bodies to remove potentially dangerous content.
"""

from __future__ import annotations
import re
import html
from typing import Any, Dict


# Patterns to remove from user input
DANGEROUS_PATTERNS = [
    re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick=, onerror=, etc.
    re.compile(r'data:text/html', re.IGNORECASE),
    re.compile(r'<iframe[^>]*>', re.IGNORECASE),
    re.compile(r'<object[^>]*>', re.IGNORECASE),
    re.compile(r'<embed[^>]*>', re.IGNORECASE),
]

# SQL injection patterns
SQL_PATTERNS = [
    re.compile(r'\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC)\b.*\b(FROM|INTO|TABLE|WHERE)\b', re.IGNORECASE),
    re.compile(r';\s*(DROP|DELETE|ALTER|CREATE)', re.IGNORECASE),
    re.compile(r"';\s*--", re.IGNORECASE),
]


def sanitize_string(value: str) -> str:
    """Sanitize a string input value."""
    if not isinstance(value, str):
        return value

    # Remove dangerous HTML/JS patterns
    cleaned = value
    for pattern in DANGEROUS_PATTERNS:
        cleaned = pattern.sub('', cleaned)

    # Escape remaining HTML entities
    cleaned = html.escape(cleaned, quote=False)

    # Un-escape common safe characters that users type naturally
    cleaned = cleaned.replace('&amp;', '&')
    cleaned = cleaned.replace('&#x27;', "'")
    cleaned = cleaned.replace('&quot;', '"')

    # Trim excessive whitespace
    cleaned = re.sub(r'\s{3,}', '  ', cleaned)

    return cleaned.strip()


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize all string values in a dictionary."""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(v) if isinstance(v, str)
                else sanitize_dict(v) if isinstance(v, dict)
                else v
                for v in value
            ]
        else:
            sanitized[key] = value
    return sanitized


def check_sql_injection(text: str) -> bool:
    """Check if text contains potential SQL injection patterns."""
    for pattern in SQL_PATTERNS:
        if pattern.search(text):
            return True
    return False
