import pytest
from unittest.mock import patch, MagicMock

from common.client_record.transcribe_client import transcribe_client


@patch("common.client_record.transcribe_client.boto3")  # Patch boto3 in the transcribe_client module
def test_transcribe_client_default_region(mock_boto3):
    mock_client_obj = MagicMock()
    mock_boto3.client.return_value = mock_client_obj

    client = transcribe_client()

    mock_boto3.client.assert_called_once_with("transcribe", region_name="us-east-1")
    assert client is mock_client_obj


@patch("common.client_record.transcribe_client.boto3")  # Patch boto3 in the transcribe_client module
def test_transcribe_client_custom_region(mock_boto3):
    mock_client_obj = MagicMock()
    mock_boto3.client.return_value = mock_client_obj

    region = "ap-south-1"
    client = transcribe_client(region_name=region)

    mock_boto3.client.assert_called_once_with("transcribe", region_name=region)
    assert client is mock_client_obj