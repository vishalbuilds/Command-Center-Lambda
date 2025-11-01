"""
Unit tests for event_sanitizer module.
"""
import pytest
from common.event_sanitizer import EventSanitizer

def test_sanitize_sensitive_keys():
    event = {
        "password": "secret123",
        "api_key": "abc123",
        "email": "test@example.com",
        "name": "John Doe"
    }
    
    sanitizer = EventSanitizer(event)
    result = sanitizer.data
    
    assert result["password"] == "***MASKED***"
    assert result["api_key"] == "***MASKED***"
    assert result["email"] == "***MASKED***"
    assert result["name"] == "John Doe"

def test_sanitize_nested_dict():
    event = {
        "user": {
            "password": "secret123",
            "name": "John Doe",
            "credentials": {
                "api_key": "abc123"
            }
        }
    }
    
    sanitizer = EventSanitizer(event)
    result = sanitizer.data
    
    assert result["user"]["password"] == "***MASKED***"
    assert result["user"]["name"] == "John Doe"
    assert result["user"]["credentials"]["api_key"] == "***MASKED***"

def test_sanitize_list():
    event = {
        "users": [
            {"email": "user1@example.com", "name": "User 1"},
            {"email": "user2@example.com", "name": "User 2"}
        ]
    }
    
    sanitizer = EventSanitizer(event)
    result = sanitizer.data
    
    assert result["users"][0]["email"] == "***MASKED***"
    assert result["users"][0]["name"] == "User 1"
    assert result["users"][1]["email"] == "***MASKED***"
    assert result["users"][1]["name"] == "User 2"

def test_sanitize_patterns():
    event = {
        "data": {
            "text": "My email is user@example.com and my phone is 1234567890",
            "description": "SSN: 123-45-6789",
            "card": "4111-1111-1111-1111"
        }
    }
    
    sanitizer = EventSanitizer(event)
    result = sanitizer.data
    
    assert "user@example.com" not in result["data"]["text"]
    assert "***MASKED***" in result["data"]["text"]
    assert "123-45-6789" not in result["data"]["description"]
    assert "4111-1111-1111-1111" not in result["data"]["card"]

def test_custom_mask_text():
    event = {
        "password": "secret123",
        "email": "test@example.com"
    }
    
    sanitizer = EventSanitizer(event, mask_text="[REDACTED]")
    result = sanitizer.data
    
    assert result["password"] == "[REDACTED]"
    assert result["email"] == "[REDACTED]"