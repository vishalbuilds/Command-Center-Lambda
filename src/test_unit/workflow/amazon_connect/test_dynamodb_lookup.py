"""
Unit tests for dynamodb_lookup module.
"""
import pytest
from unittest.mock import patch, MagicMock
from workflow.amazon_connect.dynamodb_lookup import DynamodbLookup


class TestDynamodbLookup:
    
    @patch('workflow.amazon_connect.dynamodb_lookup.REGION', 'us-east-1')
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_init_success(self, mock_dynamodb_utils):
        """Test successful initialization."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id",
            "KEY_VALUE": "123"
        }
        
        instance = DynamodbLookup(event)
        
        assert instance.event == event
        mock_dynamodb_utils.assert_called_once_with('us-east-1', 'test-table')
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_init_missing_table_name(self, mock_dynamodb_utils):
        """Test initialization with missing TABLE_NAME."""
        event = {
            "KEY_NAME": "id",
            "KEY_VALUE": "123"
        }
        
        with pytest.raises(ValueError, match="TABLE_NAME must be provided in event"):
            DynamodbLookup(event)
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_do_validate_success(self, mock_dynamodb_utils):
        """Test successful validation."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id",
            "KEY_VALUE": "123"
        }
        
        instance = DynamodbLookup(event)
        result, error = instance.do_validate()
        
        assert result is True
        assert error is None
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_do_validate_missing_table_name(self, mock_dynamodb_utils):
        """Test validation with missing TABLE_NAME."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id"
        }
        
        instance = DynamodbLookup(event)
        instance.event = {"KEY_NAME": "id", "KEY_VALUE": "123"}  # Remove TABLE_NAME
        
        result, error = instance.do_validate()
        
        assert result is False
        assert "TABLE_NAME" in str(error)
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_do_validate_missing_key_name(self, mock_dynamodb_utils):
        """Test validation with missing KEY_NAME."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_VALUE": "123"
        }
        
        instance = DynamodbLookup(event)
        result, error = instance.do_validate()
        
        assert result is False
        assert "KEY_NAME" in str(error)
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_do_validate_missing_key_value(self, mock_dynamodb_utils):
        """Test validation with missing KEY_VALUE."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id"
        }
        
        instance = DynamodbLookup(event)
        result, error = instance.do_validate()
        
        assert result is False
        assert "KEY_VALUE" in str(error)
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.dynamodb_lookup.DynamoDBUtilsResource')
    def test_do_operation_success(self, mock_dynamodb_utils):
        """Test successful do_operation."""
        event = {
            "TABLE_NAME": "test-table",
            "KEY_NAME": "id",
            "KEY_VALUE": "123"
        }
        
        mock_utils_instance = MagicMock()
        mock_utils_instance.get_single_item_by_pk.return_value = {"id": "123", "name": "test"}
        mock_dynamodb_utils.return_value = mock_utils_instance
        
        instance = DynamodbLookup(event)
        result = instance.do_operation()
        
        assert result == {"id": "123", "name": "test"}
        mock_utils_instance.get_single_item_by_pk.assert_called_once_with("id", "123")
    
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
        
        instance = DynamodbLookup(event)
        
        with pytest.raises(Exception, match="DynamoDB error"):
            instance.do_operation()
