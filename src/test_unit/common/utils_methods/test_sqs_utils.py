"""
Unit tests for sqs_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.sqs_utils import (send_message, receive_message, delete_message,
                           change_message_visibility, _create_message_attributes)

def test_create_message_attributes_empty():
    result = _create_message_attributes(None)
    assert result == {}

def test_create_message_attributes():
    message_attr = {
        "key1": "value1",
        "key2": 123,
        "key3": True
    }
    result = _create_message_attributes(message_attr)
    
    assert result == {
        "key1": {"StringValue": "value1", "DataType": "String"},
        "key2": {"StringValue": "123", "DataType": "String"},
        "key3": {"StringValue": "True", "DataType": "String"}
    }

@patch('common.utils_methods.sqs_utils.sqs_client')
def test_send_message_success(mock_sqs_client):
    mock_client = MagicMock()
    mock_sqs_client.return_value = mock_client
    mock_client.send_message.return_value = {"MessageId": "test-id"}
    
    result = send_message(
        queue="test-queue",
        message="test message",
        region="us-east-1",
        message_attr={"key": "value"}
    )
    
    assert result == {"MessageId": "test-id"}
    mock_client.send_message.assert_called_once_with(
        QueueUrl="test-queue",
        MessageBody="test message",
        MessageAttributes={"key": {"StringValue": "value", "DataType": "String"}}
    )

@patch('common.utils_methods.sqs_utils.sqs_client')
def test_receive_message_success(mock_sqs_client):
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
    
    result = receive_message(
        queue="test-queue",
        message_ids={"test_attr": "test_value"},
        region_name="us-east-1"
    )
    
    assert result["MessageId"] == "test-id"
    assert result["Body"] == "test message"

@patch('common.utils_methods.sqs_utils.sqs_client')
def test_delete_message_success(mock_sqs_client):
    mock_client = MagicMock()
    mock_sqs_client.return_value = mock_client
    
    delete_message("test-receipt", "test-queue", "us-east-1")
    
    mock_client.delete_message.assert_called_once_with(
        QueueUrl="test-queue",
        ReceiptHandle="test-receipt"
    )

@patch('common.utils_methods.sqs_utils.sqs_client')
def test_change_message_visibility_success(mock_sqs_client):
    mock_client = MagicMock()
    mock_sqs_client.return_value = mock_client
    
    change_message_visibility(
        queue="test-queue",
        receipt_handle="test-receipt",
        region_name="us-east-1",
        visibility_timeout=30
    )
    
    mock_client.change_message_visibility.assert_called_once_with(
        QueueUrl="test-queue",
        ReceiptHandle="test-receipt",
        VisibilityTimeout=30
    )