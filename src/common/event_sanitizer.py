import re
from typing import Any, Dict
from common.logger import Logger

LOGGER = Logger(__name__)


class EventSanitizer:

    SENSITIVE_KEYS = {
        "password", "passwd", "secret", "api_key", "apikey", "access_token",
        "auth_token", "token", "card_number", "credit_card", "ssn", "aadhar",
        "dob", "address",
        "awsaccesskeyid", "aws_secret_access_key", "secretaccesskey", "sessiontoken",
        "authorization", "auth", "x-amz-security-token"
    }

    SENSITIVE_PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
        "aws_key": r"AKIA[0-9A-Z]{16}",
        "aws_secret": r"(?<![A-Za-z0-9])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9])"
    }

    MASK_TEXT = "***MASKED***"

    def __init__(self, event: Dict = None, mask_text: str = None):
        if mask_text:
            self.MASK_TEXT = mask_text
        if event is not None:
            self.data = self._sanitize_dict(event)
        else:
            self.data = None

    def _mask_value(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        return self.MASK_TEXT

    def _sanitize_value(self, value: Any) -> Any:
        if isinstance(value, str):
            sanitized_value = value
            for _, pattern in self.SENSITIVE_PATTERNS.items():
                sanitized_value = re.sub(pattern, self.MASK_TEXT, sanitized_value)
            return sanitized_value
        return value

    def _sanitize_dict(self, data: Dict) -> Dict:
        sanitized = {}
        for key, value in data.items():
            if key.lower() in self.SENSITIVE_KEYS:
                sanitized[key] = self._mask_value(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_dict(v) if isinstance(v, dict) else self._sanitize_value(v)
                    for v in value
                ]
            else:
                sanitized[key] = self._sanitize_value(value)
        LOGGER.debug(f"Sanitized event: {sanitized}")
        return sanitized
