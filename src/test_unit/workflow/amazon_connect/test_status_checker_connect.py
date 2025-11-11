"""
Unit tests for status_checker_connect module.
"""
import pytest
from workflow.amazon_connect.status_checker_connect import StatusCheckerConnect


class TestStatusCheckerConnect:
    
    def test_init(self):
        """Test StatusCheckerConnect initialization."""
        event = {"test": "data"}
        checker = StatusCheckerConnect(event)
        assert checker.event == event
    
    def test_do_validate_returns_true(self):
        """Test do_validate always returns True."""
        event = {"test": "data"}
        checker = StatusCheckerConnect(event)
        assert checker.do_validate() == (True, None)
    
    def test_do_operation_success(self):
        """Test successful do_operation execution."""
        event = {"test": "data"}
        checker = StatusCheckerConnect(event)
        
        result = checker.do_operation()
        
        assert result['statusCode'] == 200
        assert result['message'] == 'Status check successful'
        assert result['service'] == 'amazon_connect'
        assert result['status'] == 'healthy'
    
    def test_do_operation_with_different_events(self):
        """Test do_operation with different event data."""
        events = [
            {},
            {"key": "value"},
            {"complex": {"nested": "data"}}
        ]
        
        for event in events:
            checker = StatusCheckerConnect(event)
            result = checker.do_operation()
            
            assert result['statusCode'] == 200
            assert result['service'] == 'amazon_connect'
            assert result['status'] == 'healthy'