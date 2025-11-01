"""
Unit tests for event_sanitizer module.
"""
import pytest
from common.event_sanitizer import EventSanitizer

def test_sanitize_sensitive_keys():
    event = {
        "password": "secret123",
        "api_key": "abc123",
        "token": "xyz789",
        "name": "John Doe"
    }
    
    sanitizer = EventSanitizer(event)
    result = sanitizer.data
    
    assert result["password"] == "***MASKED***"
    assert result["api_key"] == "***MASKED***"
    assert result["token"] == "***MASKED***"
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
            {"token": "token123", "name": "User 1"},
            {"token": "token456", "name": "User 2"}
        ]
    }
    
    sanitizer = EventSanitizer(event)
    result = sanitizer.data
    
    assert result["users"][0]["token"] == "***MASKED***"
    assert result["users"][0]["name"] == "User 1"
    assert result["users"][1]["token"] == "***MASKED***"
    assert result["users"][1]["name"] == "User 2"

def test_sanitize_patterns():
    event = {
        "data": {
            "description": "SSN: 123-45-6789",
            "card": "4111-1111-1111-1111",
            "notes": "AWS Key: AKIAIOSFODNN7EXAMPLE"
        }
    }
    
    sanitizer = EventSanitizer(event)
    result = sanitizer.data
    
    # SSN should be masked
    assert "123-45-6789" not in result["data"]["description"]
    assert "***MASKED***" in result["data"]["description"]
    
    # Credit card should be masked
    assert "4111-1111-1111-1111" not in result["data"]["card"]
    assert "***MASKED***" in result["data"]["card"]
    
    # AWS key should be masked
    assert "AKIAIOSFODNN7EXAMPLE" not in result["data"]["notes"]
    assert "***MASKED***" in result["data"]["notes"]

def test_custom_mask_text():
    event = {
        "password": "secret123",
        "api_key": "test_key_123"
    }
    
    sanitizer = EventSanitizer(event, mask_text="[REDACTED]")
    result = sanitizer.data
    
    assert result["password"] == "[REDACTED]"
    assert result["api_key"] == "[REDACTED]"

def test_non_sensitive_data_preserved():
    """Test that non-sensitive data is not modified"""
    event = {
        "username": "john_doe",
        "description": "This is a normal description",
        "count": 42,
        "active": True
    }
    
    sanitizer = EventSanitizer(event)
    result = sanitizer.data
    
    assert result["username"] == "john_doe"
    assert result["description"] == "This is a normal description"
    assert result["count"] == 42
    assert result["active"] == True