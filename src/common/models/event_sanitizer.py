import re
from typing import Any, Dict
from aws_lambda_powertools import Logger

LOGGER = Logger()

SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "access_token",
    "auth_token",
    "token",
    "card_number",
    "credit_card",
    "ssn",
    "aadhar",
    "dob",
    "address",
    "awsaccesskeyid",
    "aws_secret_access_key",
    "secretaccesskey",
    "sessiontoken",
    "authorization",
    "auth",
    "x-amz-security-token",
}

SENSITIVE_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret": r"(?<![A-Za-z0-9])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9])",
}


class EventSanitizer:

    def __init__(self, event: Dict = None):
        self.event = event
        self.custom_mask_text = ""

    def _mask_value(self, value: Any, key_name: str) -> Any:
        if not isinstance(value, str):
            return (
                self.custom_mask_text if self.custom_mask_text else f"***{key_name}***"
            )
        if self.custom_mask_text:
            return self.custom_mask_text
        return f"***{key_name}***"

    def _sanitize_value(self, value: Any) -> Any:
        if isinstance(value, str):
            sanitized_value = value
            for name, pattern in SENSITIVE_PATTERNS.items():
                mask = (
                    self.custom_mask_text if self.custom_mask_text else f"***{name}***"
                )
                sanitized_value = re.sub(pattern, mask, sanitized_value)
            return sanitized_value
        return value

    def _sanitize_dict(self, data: Dict) -> Dict:

        if data is None:
            return {}

        sanitized = {}
        for key, value in data.items():
            lower_key = key.lower()
            if lower_key in SENSITIVE_KEYS:
                sanitized[key] = self._mask_value(value, lower_key)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    (
                        self._sanitize_dict(v)
                        if isinstance(v, dict)
                        else self._sanitize_value(v)
                    )
                    for v in value
                ]
            else:
                sanitized[key] = self._sanitize_value(value)
        return sanitized

    def get_sanitized_data(self) -> Dict:
        if self.event is None:
            return {}
        if self.event.get("isSanitizationEnabled", False):
            LOGGER.info(
                "Sanitisation is enabled", extra={"maskText": self.custom_mask_text}
            )
            self.custom_mask_text = self.event.get("maskText", "")
            return self._sanitize_dict(self.event)
        else:
            LOGGER.info("Sanitisation is disabled")
            return self.event
