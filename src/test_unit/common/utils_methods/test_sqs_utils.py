"""
Unit tests for sqs_utils module.
"""

import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.sqs_utils import SQSUtils


class TestSQSUtils:

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_init(self, mock_sqs_client):
        """Test SQSUtils initialization."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client

        utils = SQSUtils("test-queue", "us-east-1")

        assert utils.queue_url == "test-queue"
        assert utils.region_name == "us-east-1"
        assert utils.sqs_client == mock_client
        mock_sqs_client.assert_called_once_with("us-east-1")

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_create_message_attributes_empty(self, mock_sqs_client):
        """Test creating message attributes with None."""
        utils = SQSUtils("test-queue", "us-east-1")
        result = utils._create_message_attributes(None)
        assert result == {}

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_create_message_attributes(self, mock_sqs_client):
        """Test creating message attributes."""
        utils = SQSUtils("test-queue", "us-east-1")
        message_attr = {"key1": "value1", "key2": 123, "key3": True}
        result = utils._create_message_attributes(message_attr)

        assert result == {
            "key1": {"StringValue": "value1", "DataType": "String"},
            "key2": {"StringValue": "123", "DataType": "String"},
            "key3": {"StringValue": "True", "DataType": "String"},
        }

    @patch("common.utils_methods.sqs_utils.logger")
    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_send_message_success(self, mock_sqs_client, mock_logger):
        """Test successful message sending."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.send_message.return_value = {"MessageId": "test-id"}

        # Patch logger.info and logger.exception to accept any kwargs (avoid KeyError)
        mock_logger.info.side_effect = lambda *args, **kwargs: None
        mock_logger.exception.side_effect = lambda *args, **kwargs: None

        utils = SQSUtils("test-queue", "us-east-1")
        result = utils.send_message(
            message="test message", message_attr={"key": "value"}
        )

        assert result == {"MessageId": "test-id"}
        mock_client.send_message.assert_called_once()

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_receive_message_success(self, mock_sqs_client):
        """Test successful message receiving."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.receive_message.return_value = {
            "Messages": [
                {
                    "MessageId": "test-id",
                    "ReceiptHandle": "test-receipt",
                    "Body": "test message",
                    "MessageAttributes": {"test_attr": {"StringValue": "test_value"}},
                }
            ]
        }

        utils = SQSUtils("test-queue", "us-east-1")
        result = utils.receive_message(message_ids={"test_attr": "test_value"})

        assert result["MessageId"] == "test-id"
        assert result["Body"] == "test message"

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_delete_message_success(self, mock_sqs_client):
        """Test successful message deletion."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client

        utils = SQSUtils("test-queue", "us-east-1")
        utils.delete_message("test-receipt")

        mock_client.delete_message.assert_called_once_with(
            QueueUrl="test-queue", ReceiptHandle="test-receipt"
        )

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_change_message_visibility_success(self, mock_sqs_client):
        """Test successful message visibility change."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client

        utils = SQSUtils("test-queue", "us-east-1")
        utils.change_message_visibility(
            receipt_handle="test-receipt", visibility_timeout=30
        )

        mock_client.change_message_visibility.assert_called_once_with(
            QueueUrl="test-queue", ReceiptHandle="test-receipt", VisibilityTimeout=30
        )

    # --- send_message error handling ---

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_send_message_client_error(self, mock_sqs_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.send_message.side_effect = ClientError(
            {'Error': {'Code': 'QueueDoesNotExist', 'Message': 'Queue not found'}}, 'send_message'
        )

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(ClientError):
            utils.send_message("test message")

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_send_message_botocore_error(self, mock_sqs_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.send_message.side_effect = BotoCoreError()

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(BotoCoreError):
            utils.send_message("test message")

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_send_message_generic_error(self, mock_sqs_client):
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.send_message.side_effect = Exception("fail")

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(Exception):
            utils.send_message("test message")

    # --- receive_message edge cases ---

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_receive_message_no_messages_exhausts_polling(self, mock_sqs_client):
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.receive_message.return_value = {}

        utils = SQSUtils("test-queue", "us-east-1")
        result = utils.receive_message(message_ids={"key": "val"}, max_polling_attempts=2)

        assert result is None
        assert mock_client.receive_message.call_count == 2

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_receive_message_skips_already_checked_receipt(self, mock_sqs_client):
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        msg = {
            "MessageId": "id1",
            "ReceiptHandle": "same-handle",
            "Body": "body",
            "MessageAttributes": {"key": {"StringValue": "wrong"}},
        }
        mock_client.receive_message.return_value = {"Messages": [msg]}
        mock_client.change_message_visibility.return_value = {}

        utils = SQSUtils("test-queue", "us-east-1")
        result = utils.receive_message(message_ids={"key": "val"}, max_polling_attempts=2)

        assert result is None

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_receive_message_auto_delete(self, mock_sqs_client):
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.receive_message.return_value = {
            "Messages": [{
                "MessageId": "id1",
                "ReceiptHandle": "handle1",
                "Body": "body",
                "MessageAttributes": {"key": {"StringValue": "val"}},
            }]
        }

        utils = SQSUtils("test-queue", "us-east-1")
        result = utils.receive_message(
            message_ids={"key": "val"}, auto_delete=True
        )

        assert result["MessageId"] == "id1"
        mock_client.delete_message.assert_called_once_with(
            QueueUrl="test-queue", ReceiptHandle="handle1"
        )

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_receive_message_client_error(self, mock_sqs_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.receive_message.side_effect = ClientError(
            {'Error': {'Code': 'QueueDoesNotExist', 'Message': 'Not found'}}, 'receive_message'
        )

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(ClientError):
            utils.receive_message(message_ids={"key": "val"})

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_receive_message_botocore_error(self, mock_sqs_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.receive_message.side_effect = BotoCoreError()

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(BotoCoreError):
            utils.receive_message(message_ids={"key": "val"})

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_receive_message_generic_error(self, mock_sqs_client):
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.receive_message.side_effect = Exception("fail")

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(Exception):
            utils.receive_message(message_ids={"key": "val"})

    # --- change_message_visibility error handling ---

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_change_message_visibility_client_error(self, mock_sqs_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.change_message_visibility.side_effect = ClientError(
            {'Error': {'Code': 'ReceiptHandleIsInvalid', 'Message': 'Invalid'}},
            'change_message_visibility'
        )

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(ClientError):
            utils.change_message_visibility("bad-handle")

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_change_message_visibility_botocore_error(self, mock_sqs_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.change_message_visibility.side_effect = BotoCoreError()

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(BotoCoreError):
            utils.change_message_visibility("handle")

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_change_message_visibility_generic_error(self, mock_sqs_client):
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.change_message_visibility.side_effect = Exception("fail")

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(Exception):
            utils.change_message_visibility("handle")

    # --- delete_message error handling ---

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_delete_message_client_error(self, mock_sqs_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.delete_message.side_effect = ClientError(
            {'Error': {'Code': 'ReceiptHandleIsInvalid', 'Message': 'Invalid'}}, 'delete_message'
        )

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(ClientError):
            utils.delete_message("bad-handle")

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_delete_message_botocore_error(self, mock_sqs_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.delete_message.side_effect = BotoCoreError()

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(BotoCoreError):
            utils.delete_message("handle")

    @patch("common.utils_methods.sqs_utils.sqs_client")
    def test_delete_message_generic_error(self, mock_sqs_client):
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.delete_message.side_effect = Exception("fail")

        utils = SQSUtils("test-queue", "us-east-1")
        with pytest.raises(Exception):
            utils.delete_message("handle")
