"""
Unit tests for event_sanitizer module.
"""

import pytest
from common.models.event_sanitizer import EventSanitizer


def test_sanitize_sensitive_keys():
    event = {
        "password": "secret123",
        "api_key": "abc123",
        "token": "xyz789",
        "name": "John Doe",
        "isSanitizationEnabled": True,
    }
    sanitizer = EventSanitizer(event)
    result = sanitizer.get_sanitized_data()

    assert result["password"] == "***password***"
    assert result["api_key"] == "***api_key***"
    assert result["token"] == "***token***"
    assert result["name"] == "John Doe"


def test_sanitize_nested_dict():
    event = {
        "user": {
            "password": "secret123",
            "name": "John Doe",
            "credentials": {"api_key": "abc123"},
        },
        "isSanitizationEnabled": True,
    }
    sanitizer = EventSanitizer(event)
    result = sanitizer.get_sanitized_data()

    assert result["user"]["password"] == "***password***"
    assert result["user"]["name"] == "John Doe"
    assert result["user"]["credentials"]["api_key"] == "***api_key***"


def test_sanitize_list():
    event = {
        "users": [
            {"token": "token123", "name": "User 1"},
            {"token": "token456", "name": "User 2"},
        ],
        "isSanitizationEnabled": True,
    }
    sanitizer = EventSanitizer(event)
    result = sanitizer.get_sanitized_data()

    assert result["users"][0]["token"] == "***token***"
    assert result["users"][0]["name"] == "User 1"
    assert result["users"][1]["token"] == "***token***"
    assert result["users"][1]["name"] == "User 2"


def test_sanitize_patterns():
    event = {
        "data": {
            "description": "SSN: 123-45-6789",
            "card": "4111-1111-1111-1111",
            "notes": "AWS Key: AKIAIOSFODNN7EXAMPLE",
        },
        "isSanitizationEnabled": True,
    }
    sanitizer = EventSanitizer(event)
    result = sanitizer.get_sanitized_data()

    # SSN should be masked
    assert "123-45-6789" not in result["data"]["description"]
    assert "***ssn***" in result["data"]["description"]

    # Credit card should be masked
    assert "4111-1111-1111-1111" not in result["data"]["card"]
    assert "***credit_card***" in result["data"]["card"]

    # AWS key should be masked
    assert "AKIAIOSFODNN7EXAMPLE" not in result["data"]["notes"]
    assert "***aws_key***" in result["data"]["notes"]


def test_non_sensitive_data_preserved():
    event = {
        "username": "john_doe",
        "description": "This is a normal description",
        "count": 42,
        "active": True,
        "isSanitizationEnabled": True,
    }
    result = EventSanitizer(event).get_sanitized_data()

    assert result["username"] == "john_doe"
    assert result["description"] == "This is a normal description"
    assert result["count"] == 42
    assert result["active"] is True


def test_sanitization_disabled_bool_false():
    event = {"password": "secret123", "isSanitizationEnabled": False}
    result = EventSanitizer(event).get_sanitized_data()
    assert result["password"] == "secret123"


def test_sanitization_string_false_is_disabled():
    event = {"password": "secret123", "isSanitizationEnabled": "false"}
    result = EventSanitizer(event).get_sanitized_data()
    assert result["password"] == "secret123"


def test_sanitization_string_true_is_enabled():
    event = {"password": "secret123", "isSanitizationEnabled": "true"}
    result = EventSanitizer(event).get_sanitized_data()
    assert result["password"] == "***password***"


def test_sanitize_compound_key_names():
    event = {
        "user_password": "hunter2",
        "my_token": "abc",
        "isSanitizationEnabled": True,
    }
    result = EventSanitizer(event).get_sanitized_data()

    assert result["user_password"] == "***password***"
    assert result["my_token"] == "***token***"


def test_sanitize_nested_list():
    event = {
        "data": [["SSN: 123-45-6789", "normal"]],
        "isSanitizationEnabled": True,
    }
    result = EventSanitizer(event).get_sanitized_data()

    assert "123-45-6789" not in result["data"][0][0]
    assert "***ssn***" in result["data"][0][0]
    assert result["data"][0][1] == "normal"


def test_sanitize_email_and_phone_patterns():
    event = {
        "message": "Email user@example.com or call 555-867-5309",
        "isSanitizationEnabled": True,
    }
    result = EventSanitizer(event).get_sanitized_data()

    assert "user@example.com" not in result["message"]
    assert "***email***" in result["message"]
    assert "555-867-5309" not in result["message"]
    assert "***phone***" in result["message"]


def test_none_event_returns_empty_dict():
    assert EventSanitizer(None).get_sanitized_data() == {}
