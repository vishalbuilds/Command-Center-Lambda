"""
Unit tests for dynamodb_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from utils.dynamodb_utils import (get_single_item_by_pk, query_items_by_key_eq, 
                                update_single_item_by_pk, _buid_dynamoDB_update_expression)

@pytest.fixture
def mock_dynamodb_table():
    with patch('utils.dynamodb_utils._dynamoDB_table') as mock:
        mock_table = MagicMock()
        mock.return_value = mock_table
        yield mock_table

def test_get_single_item_by_pk(mock_dynamodb_table):
    mock_dynamodb_table.get_item.return_value = {"item": {"id": "123", "data": "test"}}
    result = get_single_item_by_pk("test-table", "id", "123", "us-east-1")
    assert result == {"id": "123", "data": "test"}
    mock_dynamodb_table.get_item.assert_called_once_with(
        key={"id": "123"}
    )

def test_get_single_item_by_pk_error(mock_dynamodb_table):
    mock_dynamodb_table.get_item.side_effect = Exception("Test error")
    with pytest.raises(Exception, match="Test error"):
        get_single_item_by_pk("test-table", "id", "123", "us-east-1")

def test_query_items_by_key_eq(mock_dynamodb_table):
    mock_dynamodb_table.query.return_value = {"item": [{"id": "123", "data": "test"}]}
    result = query_items_by_key_eq("test-table", "test-index", "id", "123", "us-east-1")
    assert result == [{"id": "123", "data": "test"}]
    mock_dynamodb_table.query.assert_called_once()

def test_buid_dynamoDB_update_expression():
    update_data = {
        "status": "active",
        "count": 42
    }
    update_expression, expr_names, expr_values = _buid_dynamoDB_update_expression(update_data)
    
    assert update_expression.startswith("SET ")
    assert "#exp_status_key=:new_status_value" in update_expression
    assert "#exp_count_key=:new_count_value" in update_expression
    assert expr_names == {
        "#exp_status_key": "status",
        "#exp_count_key": "count"
    }
    assert expr_values == {
        ":new_status_value": "active",
        ":new_count_value": 42
    }

def test_update_single_item_by_pk(mock_dynamodb_table):
    update_data = {"status": "active"}
    update_single_item_by_pk("test-table", update_data, "id", "123", "us-east-1")
    
    mock_dynamodb_table.update_item.assert_called_once()
    call_args = mock_dynamodb_table.update_item.call_args[1]
    
    assert call_args["Key"] == {"id": "123"}
    assert call_args["UpdateExpression"].startswith("SET ")
    assert "#exp_status_key=:new_status_value" in call_args["UpdateExpression"]