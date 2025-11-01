import pytest
from unittest.mock import patch, MagicMock

from common.client_record.s3_client import s3_client


@patch("common.client_record.s3_client.boto3")  # Patch boto3 in the s3_client module
def test_s3_client_default_region(mock_boto3):
    mock_client_obj = MagicMock()
    mock_boto3.client.return_value = mock_client_obj

    client = s3_client()

    mock_boto3.client.assert_called_once_with("s3", region_name="us-east-1")
    assert client is mock_client_obj


@patch("common.client_record.s3_client.boto3")  # Patch boto3 in the s3_client module
def test_s3_client_custom_region(mock_boto3):
    mock_client_obj = MagicMock()
    mock_boto3.client.return_value = mock_client_obj

    region = "ap-south-1"
    client = s3_client(region_name=region)

    mock_boto3.client.assert_called_once_with("s3", region_name=region)
    assert client is mock_client_obj