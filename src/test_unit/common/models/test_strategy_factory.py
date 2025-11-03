"""
Unit tests for strategy_factory module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.models.strategy_factory import StrategyFactory


class TestStrategyFactory:
    
    def test_init_valid_strategy(self):
        """Test StrategyFactory initialization with valid strategy."""
        event = {"request_type": "StatusCheckerConnect"}
        invoke_type = "AMAZON_CONNECT"
        
        with patch.object(StrategyFactory, '_validate_strategy', return_value=True):
            factory = StrategyFactory(event, invoke_type)
            assert factory.event == event
            assert factory.invoke_type == invoke_type
    
    def test_init_invalid_strategy(self):
        """Test StrategyFactory initialization with invalid strategy."""
        event = {"request_type": "InvalidStrategy"}
        invoke_type = "INVALID_TYPE"
        
        with pytest.raises(Exception, match="Failed in validate strategy"):
            StrategyFactory(event, invoke_type)
    
    def test_validate_strategy_missing_request_type(self):
        """Test validation with missing request_type."""
        event = {"data": "some data"}
        invoke_type = "AMAZON_CONNECT"
        
        factory = StrategyFactory.__new__(StrategyFactory)
        factory.event = event
        factory.invoke_type = invoke_type
        
        assert factory._validate_strategy() is False
    
    @patch('common.models.strategy_factory.ALL_INVOKE_TYPE_LIST', ['StatusCheckerConnect'])
    def test_validate_strategy_invalid_request_type(self):
        """Test validation with invalid request_type."""
        event = {"request_type": "InvalidRequestType"}
        invoke_type = "AMAZON_CONNECT"
        
        factory = StrategyFactory.__new__(StrategyFactory)
        factory.event = event
        factory.invoke_type = invoke_type
        
        assert factory._validate_strategy() is False
    
    @patch('common.models.strategy_factory.globals')
    def test_initiate_strategy_success(self, mock_globals):
        """Test successful strategy initiation."""
        mock_strategy_class = MagicMock()
        mock_globals.return_value.get.return_value = mock_strategy_class
        
        event = {"request_type": "StatusCheckerConnect"}
        
        factory = StrategyFactory.__new__(StrategyFactory)
        factory.event = event
        
        factory._initiate_strategy()
        
        assert factory.strategy_class == mock_strategy_class
    
    @patch('common.models.strategy_factory.globals')
    def test_initiate_strategy_class_not_found(self, mock_globals):
        """Test strategy initiation when class not found."""
        mock_globals.return_value.get.return_value = None
        
        event = {"request_type": "NonExistentStrategy"}
        
        factory = StrategyFactory.__new__(StrategyFactory)
        factory.event = event
        
        with pytest.raises(Exception, match="Failed to initiate strategy"):
            factory._initiate_strategy()
    
    @patch.object(StrategyFactory, '_initiate_strategy')
    @patch.object(StrategyFactory, '_pass_event_to_strategy')
    def test_execute_success(self, mock_pass_event, mock_initiate):
        """Test successful execution."""
        mock_strategy_obj = MagicMock()
        mock_strategy_obj.do_validate.return_value = True
        mock_strategy_obj.do_operation.return_value = {"result": "success"}
        
        event = {"request_type": "StatusCheckerConnect"}
        invoke_type = "AMAZON_CONNECT"
        
        with patch.object(StrategyFactory, '_validate_strategy', return_value=True):
            factory = StrategyFactory(event, invoke_type)
            factory.strategy_class_obj = mock_strategy_obj
            
            result = factory.execute()
            
            assert result == {"result": "success"}
            mock_initiate.assert_called_once()
            mock_pass_event.assert_called_once()
            mock_strategy_obj.do_validate.assert_called_once()
            mock_strategy_obj.do_operation.assert_called_once()
    
    @patch.object(StrategyFactory, '_initiate_strategy')
    @patch.object(StrategyFactory, '_pass_event_to_strategy')
    def test_execute_validation_failure(self, mock_pass_event, mock_initiate):
        """Test execution with validation failure."""
        mock_strategy_obj = MagicMock()
        mock_strategy_obj.do_validate.return_value = False
        
        event = {"request_type": "StatusCheckerConnect"}
        invoke_type = "AMAZON_CONNECT"
        
        with patch.object(StrategyFactory, '_validate_strategy', return_value=True):
            factory = StrategyFactory(event, invoke_type)
            factory.strategy_class_obj = mock_strategy_obj
            
            result = factory.execute()
            
            assert result["statusCode"] == 400
            assert result["result"] == "error"