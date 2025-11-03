"""
Unit tests for lambda_handler module.
"""
import pytest
from unittest.mock import patch, MagicMock
from lambda_handler import lambda_handler


class TestLambdaHandler:
    
    @pytest.fixture
    def mock_context(self):
        """Mock AWS Lambda context."""
        context = MagicMock()
        context.aws_request_id = "test-request-id"
        context.function_name = "test-function"
        context.function_version = "1"
        return context
    
    @pytest.fixture
    def sample_event(self):
        """Sample event for testing."""
        return {
            "request_type": "StatusCheckerConnect",
            "data": {"test": "value"}
        }
    
    @patch('lambda_handler.Logger')
    @patch('lambda_handler.TraceId')
    @patch('lambda_handler.get_invocation_source')
    @patch('lambda_handler.extract_event_data')
    @patch('lambda_handler.EventSanitizer')
    @patch('lambda_handler.StrategyFactory')
    def test_lambda_handler_success(self, mock_strategy_factory, mock_event_sanitizer, 
                                  mock_extract_event_data, mock_get_invocation_source,
                                  mock_trace_id, mock_logger, mock_context, sample_event):
        """Test successful lambda handler execution."""
        # Setup mocks
        mock_get_invocation_source.return_value = "AMAZON_CONNECT"
        mock_extract_event_data.return_value = sample_event
        
        mock_sanitizer = MagicMock()
        mock_sanitizer.get_sanitized_data.return_value = sample_event
        mock_event_sanitizer.return_value = mock_sanitizer
        
        mock_factory = MagicMock()
        mock_factory.execute.return_value = {"result": "success"}
        mock_strategy_factory.return_value = mock_factory
        
        # Execute
        result = lambda_handler(sample_event, mock_context)
        
        # Assertions
        assert isinstance(result, dict)
        assert result["statusCode"] == 200
        assert result["result"] == "success"
        assert "body" in result
        
        # Verify mocks were called
        mock_trace_id.init.assert_called_once_with(mock_context)
        mock_get_invocation_source.assert_called_once()
        mock_event_sanitizer.assert_called_once()
        mock_strategy_factory.assert_called_once()
    
    @patch('lambda_handler.Logger')
    @patch('lambda_handler.TraceId')
    def test_lambda_handler_trace_id_error(self, mock_trace_id, mock_logger, mock_context, sample_event):
        """Test lambda handler with trace ID initialization error."""
        mock_trace_id.init.side_effect = Exception("Trace ID error")
        
        result = lambda_handler(sample_event, mock_context)
        
        assert isinstance(result, dict)
        assert result["statusCode"] == 400
        assert result["result"] == "error"
    
    @patch('lambda_handler.Logger')
    @patch('lambda_handler.TraceId')
    @patch('lambda_handler.get_invocation_source')
    def test_lambda_handler_invocation_source_error(self, mock_get_invocation_source,
                                                   mock_trace_id, mock_logger, 
                                                   mock_context, sample_event):
        """Test lambda handler with invocation source error."""
        mock_get_invocation_source.side_effect = Exception("Invocation source error")
        
        result = lambda_handler(sample_event, mock_context)
        
        assert isinstance(result, dict)
        assert result["statusCode"] == 400
        assert result["result"] == "error"
    
    @patch('lambda_handler.Logger')
    @patch('lambda_handler.TraceId')
    @patch('lambda_handler.get_invocation_source')
    @patch('lambda_handler.extract_event_data')
    @patch('lambda_handler.EventSanitizer')
    def test_lambda_handler_sanitizer_error(self, mock_event_sanitizer, mock_extract_event_data,
                                          mock_get_invocation_source, mock_trace_id, 
                                          mock_logger, mock_context, sample_event):
        """Test lambda handler with event sanitizer error."""
        mock_get_invocation_source.return_value = "AMAZON_CONNECT"
        mock_extract_event_data.return_value = sample_event
        mock_event_sanitizer.side_effect = Exception("Sanitizer error")
        
        result = lambda_handler(sample_event, mock_context)
        
        assert isinstance(result, dict)
        assert result["statusCode"] == 400
        assert result["result"] == "error"