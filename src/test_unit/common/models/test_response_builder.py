"""
Unit tests for response_builder module.
"""
import pytest
from datetime import datetime, timezone
from common.models.lambda_response import LambdaResponse

def test_success_response_minimal():
    result = LambdaResponse.success()
    assert result["statusCode"] == 200
    assert result["result"] == "success"
    assert isinstance(result["body"], str)

def test_success_response_with_data():
    test_data = {"key": "value"}
    test_message = "Test message"
    
    result = LambdaResponse.success(
        status_code=201,
        message=test_message,
        data=test_data
    )
    
    assert result["statusCode"] == 201
    assert result["result"] == "success"
    assert test_message in result["body"]
    assert "value" in result["body"]

def test_error_response_minimal():
    result = LambdaResponse.error()
    assert result["statusCode"] == 400
    assert result["result"] == "error"
    assert isinstance(result["body"], str)

def test_error_response_with_data():
    test_data = {"error": "test error"}
    test_message = "Error message"
    
    result = LambdaResponse.error(
        status_code=500,
        message=test_message,
        data=test_data
    )
    
    assert result["statusCode"] == 500
    assert result["result"] == "error"
    assert test_message in result["body"]
    assert "test error" in result["body"]

def test_response_with_custom_timestamp():
    test_timestamp = datetime(2025, 1, 1, tzinfo=timezone.utc)
    
    result = LambdaResponse.success(ts=test_timestamp)
    assert "2025-01-01" in result["body"]