"""
Unit tests for strategy_factory module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.models.strategy_factory import StrategyFactory

def test_strategy_factory_missing_request_type():
    with pytest.raises(Exception, match="Event must contain 'request_type'"):
        StrategyFactory({})

def test_strategy_factory_invalid_strategy():
    with pytest.raises(Exception, match="Invalid strategy: invalid_strategy"):
        StrategyFactory({"request_type": "invalid_strategy"})

def test_strategy_factory_status_checker():
    event = {
        "request_type": "StatusChecker",
        "call": "check_status",
        "input": {"key": "123"}
    }
    
    factory = StrategyFactory(event)
    result = factory.execute()
    
    assert result["status"] == "OK"
    assert result["message"] == "Lambda function is up and running"
    assert result["event"] == "check_status"
    assert result["key"] == "123"

def test_strategy_factory_s3_get_file():
    with patch('workflow.s3_get_file.S3GetFile') as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        mock_instance.handle.return_value = {"statusCode": 200}
        
        event = {
            "request_type": "S3GetFile",
            "input": {
                "bucket": "test-bucket",
                "key": "test-key"
            }
        }
        
        factory = StrategyFactory(event)
        result = factory.execute()
        
        assert result["statusCode"] == 200
        mock_instance.handle.assert_called_once_with(event)

def test_strategy_factory_s3_remove_pii():
    with patch('workflow.s3_remove_pii.S3RemovePii') as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        mock_instance.handle.return_value = {"statusCode": 200}
        
        event = {
            "request_type": "s3_remove_pii",
            "Records": [{
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "test-key"}
                }
            }]
        }
        
        factory = StrategyFactory(event)
        result = factory.execute()
        
        assert result["statusCode"] == 200
        mock_instance.handle.assert_called_once_with(event)