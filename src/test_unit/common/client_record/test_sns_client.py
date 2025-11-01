import pytest
from unittest.mock import patch, MagicMock

from common.client_record.sns_client import sns_client


@patch("common.client_record.sns_client.boto3")  # Patch boto3 in the sns_client module
def test_sns_client_default_region(mock_boto3):
    mock_client_obj = MagicMock()
    mock_boto3.client.return_value = mock_client_obj

    client = sns_client()

    mock_boto3.client.assert_called_once_with("sns", region_name="us-east-1")
    assert client is mock_client_obj


@patch("common.client_record.sns_client.boto3")  # Patch boto3 in the sns_client module
def test_sns_client_custom_region(mock_boto3):
    mock_client_obj = MagicMock()
    mock_boto3.client.return_value = mock_client_obj

    region = "ap-south-1"
    client = sns_client(region_name=region)

    mock_boto3.client.assert_called_once_with("sns", region_name=region)
    assert client is mock_client_obj