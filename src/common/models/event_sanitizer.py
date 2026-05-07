import re
from typing import Any, Dict, Optional
from aws_lambda_powertools import Logger

LOGGER = Logger(child=True)

SENSITIVE_KEYS = {
    "password", "passwd", "secret", "token", "key",
    "api_key", "apikey", "access_token", "auth_token",
    "card_number", "credit_card", "ssn", "aadhar",
    "dob", "address", "auth", "authorization", "credential",
    "awsaccesskeyid", "aws_secret_access_key", "secretaccesskey",
    "sessiontoken", "x-amz-security-token",
    "email", "phone", "mobile",
}

SENSITIVE_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
    "aws_key": r"\bAKIA[0-9A-Z]{16}\b",
    "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
}

_SPLIT_RE = re.compile(r"[_\-]+")


class EventSanitizer:

    def __init__(self, event: Dict = None):
        self.event = event

    def _pii_type(self, key: str) -> Optional[str]:
        lower = key.lower()
        if lower in SENSITIVE_KEYS:
            return lower
        for part in _SPLIT_RE.split(lower):
            if part in SENSITIVE_KEYS:
                return part
        return None

    def _sanitize_value(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        for name, pattern in SENSITIVE_PATTERNS.items():
            value = re.sub(pattern, f"***{name}***", value)
        return value

    def _sanitize_node(self, value: Any) -> Any:
        if isinstance(value, dict):
            sanitized = {}
            for key, val in value.items():
                pii = self._pii_type(key)
                sanitized[key] = f"***{pii}***" if pii else self._sanitize_node(val)
            return sanitized
        if isinstance(value, list):
            return [self._sanitize_node(item) for item in value]
        return self._sanitize_value(value)

    def get_sanitized_data(self) -> Dict:
        if self.event is None:
            return {}
        is_enabled = self.event.get("isSanitizationEnabled", False)
        if isinstance(is_enabled, str):
            is_enabled = is_enabled.lower() in ("true", "1", "yes")
        if not is_enabled:
            LOGGER.info("Sanitisation is disabled")
            return self.event
        LOGGER.info("Sanitisation is enabled")
        return self._sanitize_node(self.event)
