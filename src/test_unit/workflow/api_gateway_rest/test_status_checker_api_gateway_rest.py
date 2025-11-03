"""
Unit tests for status_checker_api_gateway_rest module.
"""
import pytest
from workflow.api_gateway_rest.status_checker_api_gateway_rest import StatusCheckerAPIGateWayRest


class TestStatusCheckerAPIGateWayRest:
    
    def test_init(self):
        """Test StatusCheckerAPIGateWayRest initialization."""
        event = {"test": "data"}
        checker = StatusCheckerAPIGateWayRest(event)
        assert checker.event == event
    
    def test_do_validate_returns_true(self):
        """Test do_validate always returns True."""
        event = {"test": "data"}
        checker = StatusCheckerAPIGateWayRest(event)
        assert checker.do_validate() is True
    
    def test_do_operation_success(self):
        """Test successful do_operation execution."""
        event = {"test": "data"}
        checker = StatusCheckerAPIGateWayRest(event)
        
        result = checker.do_operation()
        
        assert result['statusCode'] == 200
        assert result['message'] == 'Status check successful'
        assert result['service'] == 'api_gateway_rest'
        assert result['status'] == 'healthy'
    
    def test_do_operation_with_different_events(self):
        """Test do_operation with different event data."""
        events = [
            {},
            {"key": "value"},
            {"complex": {"nested": "data"}}
        ]
        
        for event in events:
            checker = StatusCheckerAPIGateWayRest(event)
            result = checker.do_operation()
            
            assert result['statusCode'] == 200
            assert result['service'] == 'api_gateway_rest'
            assert result['status'] == 'healthy'