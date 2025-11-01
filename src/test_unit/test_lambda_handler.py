"""
Unit tests for lambda_handler module.
"""
import pytest
from unittest.mock import patch, MagicMock
from lambda_handler import lambda_handler

@pytest.fixture
def mock_event_sanitizer():
    with patch('lambda_handler.EventSanitizer') as mock:
        mock_sanitizer = MagicMock()
        mock.return_value = mock_sanitizer
        mock_sanitizer.data = {"sanitized": "event"}
        yield mock_sanitizer

@pytest.fixture
def mock_strategy_factory():
    with patch('lambda_handler.StrategyFactory') as mock:
        mock_factory = MagicMock()
        mock.return_value = mock_factory
        mock_factory.execute.return_value = {"result": "success"}
        yield mock_factory

def test_lambda_handler(mock_event_sanitizer, mock_strategy_factory):
    event = {"test": "event"}
    context = {}
    
    result = lambda_handler(event, context)
    
    assert isinstance(result, dict)
    assert "statusCode" in result
    assert "result" in result
    assert "headers" in result
    assert "body" in result

def test_lambda_handler_error(mock_event_sanitizer, mock_strategy_factory):
    mock_strategy_factory.execute.side_effect = Exception("Test error")
    
    event = {"test": "event"}
    context = {}
    
    result = lambda_handler(event, context)
    
    assert isinstance(result, dict)
    assert result["statusCode"] != 200  # Should be an error status code
    assert "error" in str(result["body"]).lower()  # Error should be mentioned in the response