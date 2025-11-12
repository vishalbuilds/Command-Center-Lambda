"""
Unit tests for trace_id module.
"""
import pytest
from unittest.mock import MagicMock
from common.models.trace_id import TraceId


class TestTraceId:
    
    def setup_method(self):
        """Reset trace ID cache before each test."""
        TraceId.set(None)
    
    def test_init_with_aws_request_id(self):
        """Test TraceId initialization with AWS request ID."""
        context = {"aws_request_id": "test-request-id-123"}
        TraceId.init(context)
        
        assert TraceId.get() == "test-request-id-123"
    
    def test_init_without_aws_request_id(self):
        """Test TraceId initialization without AWS request ID."""
        context = {}
        TraceId.init(context)
        
        trace_id = TraceId.get()
        assert trace_id is not None
        assert len(trace_id) > 0
        # Should be a UUID format
        assert "-" in trace_id
    
    def test_init_with_empty_aws_request_id(self):
        """Test TraceId initialization with empty AWS request ID."""
        context = {"aws_request_id": ""}
        TraceId.init(context)
        
        trace_id = TraceId.get()
        assert trace_id is not None
        assert len(trace_id) > 0
        assert "-" in trace_id
    
    def test_get_before_init(self):
        """Test getting trace ID before initialization."""
        # Should return None if not initialized
        assert TraceId.get() is None
    
    def test_set_custom_trace_id(self):
        """Test setting a custom trace ID."""
        custom_id = "custom-trace-id-456"
        TraceId.set(custom_id)
        
        assert TraceId.get() == custom_id
    
    def test_multiple_init_calls(self):
        """Test multiple initialization calls."""
        context1 = {"aws_request_id": "first-id"}
        context2 = {"aws_request_id": "second-id"}
        
        TraceId.init(context1)
        first_id = TraceId.get()
        
        TraceId.init(context2)
        second_id = TraceId.get()
        
        assert first_id == "first-id"
        assert second_id == "second-id"
        assert first_id != second_id
    
    def test_init_with_lambda_context_object(self):
        """Test TraceId initialization with Lambda context object (not dict)."""
        # Mock a Lambda context object
        context = MagicMock()
        context.aws_request_id = "lambda-context-request-id"
        
        TraceId.init(context)
        
        assert TraceId.get() == "lambda-context-request-id"
    
    def test_init_with_lambda_context_object_no_request_id(self):
        """Test TraceId initialization with Lambda context object without request ID."""
        # Mock a Lambda context object without aws_request_id attribute
        context = MagicMock(spec=[])  # Empty spec means no attributes
        
        TraceId.init(context)
        
        trace_id = TraceId.get()
        assert trace_id is not None
        assert len(trace_id) > 0
        assert "-" in trace_id