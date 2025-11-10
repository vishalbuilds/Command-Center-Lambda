"""
Unit tests for sqs_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.sqs_utils import SQSUtils

class TestSQSUtils:
    
    @patch('common.utils_methods.sqs_utils.sqs_client')
    def test_init(self, mock_sqs_client):
        """Test SQSUtils initialization."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        
        utils = SQSUtils('test-queue', 'us-east-1')
        
        assert utils.queue_url == 'test-queue'
        assert utils.region_name == 'us-east-1'
        assert utils.sqs_client == mock_client
        mock_sqs_client.assert_called_once_with('us-east-1')
    
    @patch('common.utils_methods.sqs_utils.sqs_client')
    def test_create_message_attributes_empty(self, mock_sqs_client):
        """Test creating message attributes with None."""
        utils = SQSUtils('test-queue', 'us-east-1')
        result = utils._create_message_attributes(None)
        assert result == {}
    
    @patch('common.utils_methods.sqs_utils.sqs_client')
    def test_create_message_attributes(self, mock_sqs_client):
        """Test creating message attributes."""
        utils = SQSUtils('test-queue', 'us-east-1')
        message_attr = {
            "key1": "value1",
            "key2": 123,
            "key3": True
        }
        result = utils._create_message_attributes(message_attr)
        
        assert result == {
            "key1": {"StringValue": "value1", "DataType": "String"},
            "key2": {"StringValue": "123", "DataType": "String"},
            "key3": {"StringValue": "True", "DataType": "String"}
        }
    
    @patch('common.utils_methods.sqs_utils.sqs_client')
    def test_send_message_success(self, mock_sqs_client):
        """Test successful message sending."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.send_message.return_value = {"MessageId": "test-id"}
        
        utils = SQSUtils('test-queue', 'us-east-1')
        result = utils.send_message(
            message="test message",
            message_attr={"key": "value"}
        )
        
        assert result == {"MessageId": "test-id"}
        mock_client.send_message.assert_called_once()
    
    @patch('common.utils_methods.sqs_utils.sqs_client')
    def test_receive_message_success(self, mock_sqs_client):
        """Test successful message receiving."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        mock_client.receive_message.return_value = {
            "Messages": [{
                "MessageId": "test-id",
                "ReceiptHandle": "test-receipt",
                "Body": "test message",
                "MessageAttributes": {
                    "test_attr": {"StringValue": "test_value"}
                }
            }]
        }
        
        utils = SQSUtils('test-queue', 'us-east-1')
        result = utils.receive_message(
            message_ids={"test_attr": "test_value"}
        )
        
        assert result["MessageId"] == "test-id"
        assert result["Body"] == "test message"
    
    @patch('common.utils_methods.sqs_utils.sqs_client')
    def test_delete_message_success(self, mock_sqs_client):
        """Test successful message deletion."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        
        utils = SQSUtils('test-queue', 'us-east-1')
        utils.delete_message("test-receipt")
        
        mock_client.delete_message.assert_called_once_with(
            QueueUrl="test-queue",
            ReceiptHandle="test-receipt"
        )
    
    @patch('common.utils_methods.sqs_utils.sqs_client')
    def test_change_message_visibility_success(self, mock_sqs_client):
        """Test successful message visibility change."""
        mock_client = MagicMock()
        mock_sqs_client.return_value = mock_client
        
        utils = SQSUtils('test-queue', 'us-east-1')
        utils.change_message_visibility(
            receipt_handle="test-receipt",
            visibility_timeout=30
        )
        
        mock_client.change_message_visibility.assert_called_once_with(
            QueueUrl="test-queue",
            ReceiptHandle="test-receipt",
            VisibilityTimeout=30
        )