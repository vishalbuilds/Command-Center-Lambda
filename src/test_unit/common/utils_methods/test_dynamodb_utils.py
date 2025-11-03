"""
Unit tests for dynamodb_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.dynamodb_utils import (
    get_single_item_by_pk, 
    query_items_by_key_eq, 
    update_single_item_by_pk,
    _buid_dynamoDB_update_expression
)


class TestDynamoDBUtils:
    
    @patch('common.utils_methods.dynamodb_utils._dynamoDB_table')
    def test_get_single_item_by_pk_success(self, mock_dynamodb_table):
        """Test successful get_single_item_by_pk operation."""
        mock_table = MagicMock()
        mock_dynamodb_table.return_value = mock_table
        mock_table.get_item.return_value = {
            'item': {'id': 'test-id', 'name': 'test-name'}
        }
        
        result = get_single_item_by_pk('test-table', 'id', 'test-id', 'us-east-1')
        
        assert result == {'id': 'test-id', 'name': 'test-name'}
        mock_table.get_item.assert_called_once_with(
            key={'id': 'test-id'}
        )
    
    @patch('common.utils_methods.dynamodb_utils._dynamoDB_table')
    def test_get_single_item_by_pk_not_found(self, mock_dynamodb_table):
        """Test get_single_item_by_pk when item not found."""
        mock_table = MagicMock()
        mock_dynamodb_table.return_value = mock_table
        mock_table.get_item.return_value = {}
        
        result = get_single_item_by_pk('test-table', 'id', 'test-id', 'us-east-1')
        
        assert result is None
    
    @patch('common.utils_methods.dynamodb_utils._dynamoDB_table')
    def test_get_single_item_by_pk_exception(self, mock_dynamodb_table):
        """Test get_single_item_by_pk with exception."""
        mock_table = MagicMock()
        mock_dynamodb_table.return_value = mock_table
        mock_table.get_item.side_effect = Exception("Table not found")
        
        with pytest.raises(Exception, match="Table not found"):
            get_single_item_by_pk('test-table', 'id', 'test-id', 'us-east-1')
    
    @patch('common.utils_methods.dynamodb_utils._dynamoDB_table')
    @patch('common.utils_methods.dynamodb_utils._dynamoDB_condition_Expression_key')
    def test_query_items_by_key_eq_success(self, mock_condition_expr, mock_dynamodb_table):
        """Test successful query_items_by_key_eq operation."""
        mock_table = MagicMock()
        mock_dynamodb_table.return_value = mock_table
        mock_condition = MagicMock()
        mock_condition_expr.return_value = mock_condition
        
        mock_table.query.return_value = {
            'item': [
                {'id': 'test-id-1', 'status': 'active'},
                {'id': 'test-id-2', 'status': 'active'}
            ]
        }
        
        result = query_items_by_key_eq('test-table', 'status-index', 'status', 'active', 'us-east-1')
        
        assert len(result) == 2
        assert result[0]['status'] == 'active'
        mock_table.query.assert_called_once_with(
            IndexName='status-index',
            KeyConditionExpression=mock_condition
        )
    
    def test_build_dynamodb_update_expression_single_field(self):
        """Test _buid_dynamoDB_update_expression with single field."""
        update_data = {'status': 'active'}
        
        update_expression, attr_names, attr_values = _buid_dynamoDB_update_expression(update_data)
        
        assert update_expression == 'SET #exp_status_key=:new_status_value'
        assert attr_names == {'#exp_status_key': 'status'}
        assert attr_values == {':new_status_value': 'active'}
    
    def test_build_dynamodb_update_expression_multiple_fields(self):
        """Test _buid_dynamoDB_update_expression with multiple fields."""
        update_data = {'status': 'active', 'count': 42}
        
        update_expression, attr_names, attr_values = _buid_dynamoDB_update_expression(update_data)
        
        assert update_expression.startswith('SET ')
        assert '#exp_status_key=:new_status_value' in update_expression
        assert '#exp_count_key=:new_count_value' in update_expression
        
        assert attr_names['#exp_status_key'] == 'status'
        assert attr_names['#exp_count_key'] == 'count'
        
        assert attr_values[':new_status_value'] == 'active'
        assert attr_values[':new_count_value'] == 42
    
    @patch('common.utils_methods.dynamodb_utils._dynamoDB_table')
    def test_update_single_item_by_pk_success(self, mock_dynamodb_table):
        """Test successful update_single_item_by_pk operation."""
        mock_table = MagicMock()
        mock_dynamodb_table.return_value = mock_table
        
        update_data = {'status': 'inactive', 'count': 42}
        
        update_single_item_by_pk('test-table', update_data, 'id', 'test-id', 'us-east-1')
        
        mock_table.update_item.assert_called_once()
        call_args = mock_table.update_item.call_args
        
        assert call_args[1]['Key'] == {'id': 'test-id'}
        assert 'UpdateExpression' in call_args[1]
        assert 'ExpressionAttributeNames' in call_args[1]
        assert 'ExpressionAttributeValues' in call_args[1]