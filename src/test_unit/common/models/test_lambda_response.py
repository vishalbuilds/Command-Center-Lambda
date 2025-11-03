"""
Unit tests for lambda_response module.
"""
import pytest
import json
from datetime import datetime, timezone
from common.models.lambda_response import LambdaResponse


class TestLambdaResponse:
    
    def test_success_response_default(self):
        """Test default success response."""
        response = LambdaResponse.success()
        
        assert response["statusCode"] == 200
        assert response["result"] == "success"
        assert "body" in response
        
        body = json.loads(response["body"])
        assert body["message"] is None
        assert body["data"] is None
        assert "timestamp" in body
    
    def test_success_response_with_data(self):
        """Test success response with message and data."""
        message = "Operation completed successfully"
        data = {"user_id": 123, "status": "active"}
        
        response = LambdaResponse.success(message=message, data=data)
        
        assert response["statusCode"] == 200
        assert response["result"] == "success"
        
        body = json.loads(response["body"])
        assert body["message"] == message
        assert body["data"] == data
        assert "timestamp" in body
    
    def test_success_response_custom_status_code(self):
        """Test success response with custom status code."""
        response = LambdaResponse.success(status_code=201)
        
        assert response["statusCode"] == 201
        assert response["result"] == "success"
    
    def test_success_response_custom_timestamp(self):
        """Test success response with custom timestamp."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        response = LambdaResponse.success(ts=custom_time)
        
        body = json.loads(response["body"])
        assert body["timestamp"] == custom_time.isoformat()
    
    def test_error_response_default(self):
        """Test default error response."""
        response = LambdaResponse.error()
        
        assert response["statusCode"] == 400
        assert response["result"] == "error"
        assert "body" in response
        
        body = json.loads(response["body"])
        assert body["message"] is None
        assert body["data"] is None
        assert "timestamp" in body
    
    def test_error_response_with_data(self):
        """Test error response with message and data."""
        message = "Validation failed"
        data = {"errors": ["Field is required", "Invalid format"]}
        
        response = LambdaResponse.error(message=message, data=data)
        
        assert response["statusCode"] == 400
        assert response["result"] == "error"
        
        body = json.loads(response["body"])
        assert body["message"] == message
        assert body["data"] == data
        assert "timestamp" in body
    
    def test_error_response_custom_status_code(self):
        """Test error response with custom status code."""
        response = LambdaResponse.error(status_code=500)
        
        assert response["statusCode"] == 500
        assert response["result"] == "error"
    
    def test_error_response_custom_timestamp(self):
        """Test error response with custom timestamp."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        response = LambdaResponse.error(ts=custom_time)
        
        body = json.loads(response["body"])
        assert body["timestamp"] == custom_time.isoformat()
    
    def test_response_body_is_valid_json(self):
        """Test that response body is valid JSON."""
        success_response = LambdaResponse.success(message="test", data={"key": "value"})
        error_response = LambdaResponse.error(message="error", data={"error": "details"})
        
        # Should not raise exception
        json.loads(success_response["body"])
        json.loads(error_response["body"])
    
    def test_timestamp_format(self):
        """Test timestamp format is ISO format."""
        response = LambdaResponse.success()
        body = json.loads(response["body"])
        
        # Should be able to parse the timestamp
        timestamp = datetime.fromisoformat(body["timestamp"].replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)
        assert timestamp.tzinfo is not None