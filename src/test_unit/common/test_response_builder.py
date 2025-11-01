"""
Unit tests for response_builder module.
"""
import pytest
from datetime import datetime, timezone
from common.response_builder import ResponseBuilder

@pytest.fixture
def response_builder():
    return ResponseBuilder()

def test_success_response_minimal(response_builder):
    result = response_builder.success()
    assert result["statusCode"] == 200
    assert result["result"] == "success"
    assert "headers" in result
    assert "Content-Type" in result["headers"]
    assert isinstance(result["body"], str)

def test_success_response_with_data(response_builder):
    test_data = {"key": "value"}
    test_message = "Test message"
    
    result = response_builder.success(
        status_code=201,
        message=test_message,
        data=test_data
    )
    
    assert result["statusCode"] == 201
    assert result["result"] == "success"
    assert test_message in result["body"]
    assert "value" in result["body"]

def test_error_response_minimal(response_builder):
    result = response_builder.error()
    assert result["statusCode"] == 400
    assert result["result"] == "error"
    assert "headers" in result
    assert "Content-Type" in result["headers"]
    assert isinstance(result["body"], str)

def test_error_response_with_data(response_builder):
    test_data = {"error": "test error"}
    test_message = "Error message"
    
    result = response_builder.error(
        status_code=500,
        message=test_message,
        data=test_data
    )
    
    assert result["statusCode"] == 500
    assert result["result"] == "error"
    assert test_message in result["body"]
    assert "test error" in result["body"]

def test_response_with_custom_timestamp(response_builder):
    test_timestamp = datetime(2025, 1, 1, tzinfo=timezone.utc)
    
    result = response_builder.success(ts=test_timestamp)
    assert "2025-01-01" in result["body"]