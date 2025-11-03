"""
Unit tests for find_invocation_source module.
"""
import pytest
from common.models.find_invocation_source import (
    get_invocation_source, 
    extract_event_data,
    _is_amazon_connect,
    _is_s3_event,
    _is_eventbridge,
    _is_function_url,
    _is_api_gateway_http,
    _is_api_gateway_rest
)


class TestFindInvocationSource:
    
    def test_is_amazon_connect_with_contact_data(self):
        """Test Amazon Connect detection with ContactData."""
        event = {
            "Details": {
                "ContactData": {
                    "ContactId": "test-contact-id"
                }
            }
        }
        assert _is_amazon_connect(event) is True
    
    def test_is_amazon_connect_with_name_contact(self):
        """Test Amazon Connect detection with contact in name."""
        event = {"Name": "ContactFlowEvent"}
        assert _is_amazon_connect(event) is True
        
        event = {"Name": "ConnectEvent"}
        assert _is_amazon_connect(event) is True
    
    def test_is_amazon_connect_false(self):
        """Test Amazon Connect detection returns false."""
        event = {"Name": "SomeOtherEvent"}
        assert _is_amazon_connect(event) is False
        
        event = {"Details": {"SomeOtherData": {}}}
        assert _is_amazon_connect(event) is False
    
    def test_is_s3_event_true(self):
        """Test S3 event detection."""
        event = {
            "Records": [
                {
                    "eventSource": "aws:s3",
                    "s3": {
                        "bucket": {"name": "test-bucket"}
                    }
                }
            ]
        }
        assert _is_s3_event(event) is True
    
    def test_is_s3_event_false(self):
        """Test S3 event detection returns false."""
        event = {"Records": [{"eventSource": "aws:sns"}]}
        assert _is_s3_event(event) is False
        
        event = {"Records": []}
        assert _is_s3_event(event) is False
        
        event = {"data": "no records"}
        assert _is_s3_event(event) is False
    
    def test_is_eventbridge_true(self):
        """Test EventBridge detection."""
        event = {
            "detail-type": "EC2 Instance State-change Notification",
            "source": "aws.ec2",
            "detail": {}
        }
        assert _is_eventbridge(event) is True
    
    def test_is_eventbridge_false(self):
        """Test EventBridge detection returns false."""
        event = {"detail-type": "test", "Records": []}  # Has Records, so not EventBridge
        assert _is_eventbridge(event) is False
        
        event = {"source": "aws.ec2"}  # Missing detail-type
        assert _is_eventbridge(event) is False
    
    def test_is_function_url_true(self):
        """Test Function URL detection."""
        request_context = {"domainName": "abc123.lambda-url.us-east-1.on.aws"}
        assert _is_function_url(request_context) is True
    
    def test_is_function_url_false(self):
        """Test Function URL detection returns false."""
        request_context = {"domainName": "api.example.com"}
        assert _is_function_url(request_context) is False
        
        request_context = {}
        assert _is_function_url(request_context) is False
    
    def test_is_api_gateway_http_true(self):
        """Test API Gateway HTTP detection."""
        request_context = {"http": {"method": "GET"}}
        assert _is_api_gateway_http(request_context) is True
    
    def test_is_api_gateway_http_false(self):
        """Test API Gateway HTTP detection returns false."""
        request_context = {"apiId": "test"}
        assert _is_api_gateway_http(request_context) is False
    
    def test_is_api_gateway_rest_true(self):
        """Test API Gateway REST detection."""
        request_context = {"apiId": "test123", "stage": "prod"}
        assert _is_api_gateway_rest(request_context) is True
        
        request_context = {"stage": "dev"}
        assert _is_api_gateway_rest(request_context) is True
    
    def test_is_api_gateway_rest_false_function_url(self):
        """Test API Gateway REST detection returns false for function URL."""
        request_context = {
            "apiId": "test123", 
            "domainName": "abc123.lambda-url.us-east-1.on.aws"
        }
        assert _is_api_gateway_rest(request_context) is False 
    
    def test_get_invocation_source_amazon_connect(self):
        """Test get_invocation_source for Amazon Connect."""
        event = {
            "Details": {
                "ContactData": {
                    "ContactId": "test-contact-id"
                }
            }
        }
        assert get_invocation_source(event) == "AMAZON_CONNECT"
    
    def test_get_invocation_source_s3(self):
        """Test get_invocation_source for S3."""
        event = {
            "Records": [
                {
                    "eventSource": "aws:s3",
                    "s3": {"bucket": {"name": "test-bucket"}}
                }
            ]
        }
        assert get_invocation_source(event) == "S3"
    
    def test_get_invocation_source_eventbridge(self):
        """Test get_invocation_source for EventBridge."""
        event = {
            "detail-type": "EC2 Instance State-change Notification",
            "source": "aws.ec2",
            "detail": {}
        }
        assert get_invocation_source(event) == "EVENTBRIDGE"
    
    def test_get_invocation_source_function_url(self):
        """Test get_invocation_source for Function URL."""
        event = {
            "headers": {},
            "requestContext": {
                "domainName": "abc123.lambda-url.us-east-1.on.aws"
            }
        }
        assert get_invocation_source(event) == "FUNCTION_URL"
    
    def test_get_invocation_source_api_gateway_http(self):
        """Test get_invocation_source for API Gateway HTTP."""
        event = {
            "headers": {},
            "requestContext": {
                "http": {"method": "GET"}
            }
        }
        assert get_invocation_source(event) == "API_GATEWAY_HTTP"
    
    def test_get_invocation_source_api_gateway_rest(self):
        """Test get_invocation_source for API Gateway REST."""
        event = {
            "headers": {},
            "requestContext": {
                "apiId": "test123",
                "stage": "prod"
            }
        }
        assert get_invocation_source(event) == "API_GATEWAY_REST"
    
    def test_get_invocation_source_direct_invoke(self):
        """Test get_invocation_source for direct invoke."""
        event = {"data": "some data"}
        assert get_invocation_source(event) == "DIRECT_INVOKE"
    
    def test_extract_event_data_amazon_connect(self):
        """Test extract_event_data for Amazon Connect."""
        event = {
            "Details": {
                "ContactData": {
                    "Attributes": {
                        "key1": "value1",
                        "key2": "value2"
                    }
                }
            }
        }
        result = extract_event_data(event, "AMAZON_CONNECT")
        assert result == {"key1": "value1", "key2": "value2"}
    
    def test_extract_event_data_api_gateway(self):
        """Test extract_event_data for API Gateway."""
        event = {
            "requestContext": {
                "apiId": "test123",
                "stage": "prod"
            }
        }
        result = extract_event_data(event, "API_GATEWAY_REST")
        assert result == {"apiId": "test123", "stage": "prod"}
        
        result = extract_event_data(event, "API_GATEWAY_HTTP")
        assert result == {"apiId": "test123", "stage": "prod"}
        
        result = extract_event_data(event, "FUNCTION_URL")
        assert result == {"apiId": "test123", "stage": "prod"}
    
    def test_extract_event_data_s3(self):
        """Test extract_event_data for S3."""
        event = {
            "Records": [
                {"s3": {"bucket": {"name": "test-bucket"}}}
            ]
        }
        result = extract_event_data(event, "S3")
        assert result == [{"s3": {"bucket": {"name": "test-bucket"}}}]
    
    def test_extract_event_data_eventbridge(self):
        """Test extract_event_data for EventBridge."""
        event = {
            "detail": {
                "state": "running",
                "instance-id": "i-1234567890abcdef0"
            }
        }
        result = extract_event_data(event, "EVENTBRIDGE")
        assert result == {"state": "running", "instance-id": "i-1234567890abcdef0"}
    
    def test_extract_event_data_direct_invoke(self):
        """Test extract_event_data for direct invoke."""
        event = {"data": "some data", "key": "value"}
        result = extract_event_data(event, "DIRECT_INVOKE")
        assert result == {"data": "some data", "key": "value"}
    
    def test_extract_event_data_missing_keys(self):
        """Test extract_event_data with missing keys."""
        event = {}
        
        result = extract_event_data(event, "AMAZON_CONNECT")
        assert result == {}
        
        result = extract_event_data(event, "API_GATEWAY_REST")
        assert result == {}
        
        result = extract_event_data(event, "S3")
        assert result == []
        
        result = extract_event_data(event, "EVENTBRIDGE")
        assert result == {}