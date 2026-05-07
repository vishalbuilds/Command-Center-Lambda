import pytest
from unittest.mock import patch, MagicMock
from workflow.amazon_connect.dynamodb_store_attributes import DynamoDBStoreAttributes


BASE_EVENT = {
    "TABLE_NAME": "test-table",
    "KEY_NAME": "contactId",
    "KEY_VALUE": "abc-123",
}


class TestDynamoDBStoreAttributes:

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_init_success(self, mock_dynamodb_cls):
        obj = DynamoDBStoreAttributes(BASE_EVENT)
        mock_dynamodb_cls.assert_called_once()

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_init_missing_table_name_raises(self, mock_dynamodb_cls):
        with pytest.raises(ValueError, match="TABLE_NAME"):
            DynamoDBStoreAttributes({"KEY_NAME": "id", "KEY_VALUE": "1"})

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_do_validate_success(self, mock_dynamodb_cls):
        obj = DynamoDBStoreAttributes(BASE_EVENT)
        result, errors = obj.do_validate()
        assert result is True
        assert errors is None

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_do_validate_missing_key_name(self, mock_dynamodb_cls):
        event = {**BASE_EVENT, "KEY_NAME": ""}
        obj = DynamoDBStoreAttributes(event)
        result, errors = obj.do_validate()
        assert result is False
        assert any("KEY_NAME" in e for e in errors)

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_do_validate_missing_key_value(self, mock_dynamodb_cls):
        event = {**BASE_EVENT, "KEY_VALUE": ""}
        obj = DynamoDBStoreAttributes(event)
        result, errors = obj.do_validate()
        assert result is False
        assert any("KEY_VALUE" in e for e in errors)

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_do_validate_missing_both_keys(self, mock_dynamodb_cls):
        event = {**BASE_EVENT, "KEY_NAME": "", "KEY_VALUE": ""}
        obj = DynamoDBStoreAttributes(event)
        result, errors = obj.do_validate()
        assert result is False
        assert len(errors) == 2

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_customise_data_from_connect_event(self, mock_dynamodb_cls):
        obj = DynamoDBStoreAttributes(BASE_EVENT)
        event = {
            **BASE_EVENT,
            "detail": {
                "contactData": {
                    "phoneNumber": "+1234567890",
                    "status": "CONNECTED",
                    "timestamp": "2026-01-01T00:00:00Z",
                    "type": "VOICE",
                    "direction": "INBOUND",
                }
            },
        }
        data = obj._customise_data_from_connect_event(event)
        assert data["contactId"] == "abc-123"
        assert data["phone_number"] == "+1234567890"
        assert data["status"] == "CONNECTED"
        assert data["type"] == "VOICE"
        assert data["direction"] == "INBOUND"

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_customise_data_empty_contact_data(self, mock_dynamodb_cls):
        obj = DynamoDBStoreAttributes(BASE_EVENT)
        data = obj._customise_data_from_connect_event(BASE_EVENT)
        assert data["phone_number"] is None
        assert data["status"] is None

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_do_operation_success(self, mock_dynamodb_cls):
        mock_db = MagicMock()
        mock_dynamodb_cls.return_value = mock_db

        obj = DynamoDBStoreAttributes(BASE_EVENT)
        obj.do_operation()

        mock_db.put_item.assert_called_once()
        call_args = mock_db.put_item.call_args[0][0]
        assert call_args["contactId"] == "abc-123"

    @patch("workflow.amazon_connect.dynamodb_store_attributes.DynamoDBUtilsResource")
    def test_do_operation_raises_on_exception(self, mock_dynamodb_cls):
        mock_db = MagicMock()
        mock_db.put_item.side_effect = Exception("DynamoDB error")
        mock_dynamodb_cls.return_value = mock_db

        obj = DynamoDBStoreAttributes(BASE_EVENT)
        with pytest.raises(Exception, match="DynamoDB error"):
            obj.do_operation()
