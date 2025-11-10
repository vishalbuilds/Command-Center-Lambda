"""
Unit tests for dynamodb_utils module.
"""

import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.dynamodb_utils_resource import DynamoDBUtilsResource


class TestDynamoDBUtils:

    @patch("common.utils_methods.dynamodb_utils_resource.dynamoDB_resource")
    def test_init(self, mock_dynamodb_resource):
        """Test DynamoDBUtilsResource initialization."""
        mock_resource = MagicMock()
        mock_table = MagicMock()
        mock_resource.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_resource

        utils = DynamoDBUtilsResource("us-east-1", "test-table")

        assert utils.region_name == "us-east-1"
        assert utils.table_name == "test-table"
        assert utils.dynamodb_table == mock_table
        mock_dynamodb_resource.assert_called_once_with("us-east-1")

    @patch("common.utils_methods.dynamodb_utils_resource.dynamoDB_resource")
    def test_get_single_item_by_pk_success(self, mock_dynamodb_resource):
        """Test successful get_single_item_by_pk operation."""
        mock_resource = MagicMock()
        mock_table = MagicMock()
        mock_resource.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_resource

        mock_table.get_item.return_value = {
            "item": {"id": "test-id", "name": "test-name"}
        }

        utils = DynamoDBUtilsResource("us-east-1", "test-table")
        result = utils.get_single_item_by_pk("id", "test-id")

        assert result == {"id": "test-id", "name": "test-name"}
        mock_table.get_item.assert_called_once_with(key={"id": "test-id"})

    @patch("common.utils_methods.dynamodb_utils_resource.dynamoDB_resource")
    def test_get_single_item_by_pk_exception(self, mock_dynamodb_resource):
        """Test get_single_item_by_pk with exception."""
        mock_resource = MagicMock()
        mock_table = MagicMock()
        mock_resource.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_resource

        mock_table.get_item.side_effect = Exception("Table not found")

        utils = DynamoDBUtilsResource("us-east-1", "test-table")
        with pytest.raises(Exception, match="Table not found"):
            utils.get_single_item_by_pk("id", "test-id")

    @patch("common.utils_methods.dynamodb_utils_resource.dynamoDB_resource")
    def test_build_dynamodb_update_expression_single_field(
        self, mock_dynamodb_resource
    ):
        """Test _buid_dynamoDB_update_expression with single field."""
        mock_resource = MagicMock()
        mock_table = MagicMock()
        mock_resource.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_resource

        utils = DynamoDBUtilsResource("us-east-1", "test-table")
        update_data = {"status": "active"}

        (
            update_expression,
            attr_names,
            attr_values,
        ) = utils._buid_dynamoDB_update_expression(update_data)

        assert update_expression == "SET #exp_status_key=:new_status_value"
        assert attr_names == {"#exp_status_key": "status"}
        assert attr_values == {":new_status_value": "active"}

    @patch("common.utils_methods.dynamodb_utils_resource.dynamoDB_resource")
    def test_build_dynamodb_update_expression_multiple_fields(
        self, mock_dynamodb_resource
    ):
        """Test _buid_dynamoDB_update_expression with multiple fields."""
        mock_resource = MagicMock()
        mock_table = MagicMock()
        mock_resource.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_resource

        utils = DynamoDBUtilsResource("us-east-1", "test-table")
        update_data = {"status": "active", "count": 42}

        (
            update_expression,
            attr_names,
            attr_values,
        ) = utils._buid_dynamoDB_update_expression(update_data)

        assert update_expression.startswith("SET ")
        assert "#exp_status_key=:new_status_value" in update_expression
        assert "#exp_count_key=:new_count_value" in update_expression

        assert attr_names["#exp_status_key"] == "status"
        assert attr_names["#exp_count_key"] == "count"

        assert attr_values[":new_status_value"] == "active"
        assert attr_values[":new_count_value"] == 42

    @patch("common.utils_methods.dynamodb_utils_resource.dynamoDB_resource")
    def test_update_single_item_by_pk_success(self, mock_dynamodb_resource):
        """Test successful update_single_item_by_pk operation."""
        mock_resource = MagicMock()
        mock_table = MagicMock()
        mock_resource.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_resource

        utils = DynamoDBUtilsResource("us-east-1", "test-table")
        update_data = {"status": "inactive", "count": 42}

        utils.update_single_item_by_pk(update_data, "id", "test-id")

        mock_table.update_item.assert_called_once()
        call_args = mock_table.update_item.call_args

        assert call_args[1]["Key"] == {"id": "test-id"}
        assert "UpdateExpression" in call_args[1]
        assert "ExpressionAttributeNames" in call_args[1]
        assert "ExpressionAttributeValues" in call_args[1]

    @patch("common.utils_methods.dynamodb_utils_resource.dynamoDB_resource")
    def test_put_item_success(self, mock_dynamodb_resource):
        """Test successful put_item operation."""
        mock_resource = MagicMock()
        mock_table = MagicMock()
        mock_resource.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_resource

        utils = DynamoDBUtilsResource("us-east-1", "test-table")
        item = {"id": "test-id", "name": "test-name"}

        utils.put_item(item)

        mock_table.put_item.assert_called_once_with(Item=item)
