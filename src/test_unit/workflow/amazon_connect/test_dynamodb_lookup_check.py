"""
Unit tests for dynamodb_lookup_check module.
"""
import pytest
from unittest.mock import patch, MagicMock
from workflow.amazon_connect.dynamodb_lookup_check import DynamoDBLookupCheck


class TestDynamoDBLookupCheck:
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_init(self, mock_dynamodb_utils):
        """Test DynamoDBLookupCheck initialization."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id",
            "KEY_VALUE": "123"
        }
        
        instance = DynamoDBLookupCheck(event)
        
        assert instance.event == event
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_do_operation_item_found(self, mock_dynamodb_utils):
        """Test do_operation when item is found."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id",
            "KEY_VALUE": "123"
        }
        
        mock_utils_instance = MagicMock()
        mock_utils_instance.get_single_item_by_pk.return_value = {"id": "123", "name": "test"}
        mock_dynamodb_utils.return_value = mock_utils_instance
        
        instance = DynamoDBLookupCheck(event)
        result = instance.do_operation()
        
        assert result["exists"] is True
        assert "Item found in table" in result["message"]
        assert result["item"] == {"id": "123", "name": "test"}
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_do_operation_item_not_found(self, mock_dynamodb_utils):
        """Test do_operation when item is not found."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id",
            "KEY_VALUE": "999"
        }
        
        mock_utils_instance = MagicMock()
        mock_utils_instance.get_single_item_by_pk.return_value = None
        mock_dynamodb_utils.return_value = mock_utils_instance
        
        instance = DynamoDBLookupCheck(event)
        result = instance.do_operation()
        
        assert result["exists"] is False
        assert "Item not found in table" in result["message"]
        assert result["item"] is None
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_do_operation_exception(self, mock_dynamodb_utils):
        """Test do_operation with exception."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id",
            "KEY_VALUE": "123"
        }
        
        mock_utils_instance = MagicMock()
        mock_utils_instance.get_single_item_by_pk.side_effect = Exception("DynamoDB error")
        mock_dynamodb_utils.return_value = mock_utils_instance
        
        instance = DynamoDBLookupCheck(event)
        
        with pytest.raises(Exception, match="DynamoDB error"):
            instance.do_operation()
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_do_operation_empty_item(self, mock_dynamodb_utils):
        """Test do_operation when item is empty dict."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id",
            "KEY_VALUE": "123"
        }
        
        mock_utils_instance = MagicMock()
        mock_utils_instance.get_single_item_by_pk.return_value = {}
        mock_dynamodb_utils.return_value = mock_utils_instance
        
        instance = DynamoDBLookupCheck(event)
        result = instance.do_operation()
        
        # Empty dict is falsy, so should be treated as not found
        assert result["exists"] is False
        assert result["item"] is None
