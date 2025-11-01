import pytest
from unittest.mock import patch, MagicMock
from common.client_record.dynamodb_resource import dynamoDB_resource, dynamoDB_condition_Expression


@patch("common.client_record.dynamodb_resource.boto3") 
def test_dynamodb_resource_default_region(mock_boto3):
    mock_resource_obj = MagicMock()
    mock_boto3.resource.return_value = mock_resource_obj

    client = dynamoDB_resource()

    mock_boto3.resource.assert_called_once_with("dynamodb", region_name="us-east-1")
    assert client is mock_resource_obj


@patch("common.client_record.dynamodb_resource.boto3") 
def test_dynamodb_resource_custom_region(mock_boto3):
    mock_resource_obj = MagicMock()
    mock_boto3.resource.return_value = mock_resource_obj

    region = "ap-south-1"
    client = dynamoDB_resource(region_name=region)

    mock_boto3.resource.assert_called_once_with("dynamodb", region_name=region)
    assert client is mock_resource_obj


@patch("common.client_record.dynamodb_resource.dynamodb_conditions")  
def test_dynamoDB_condition_Expression(mock_conditions):
    result = dynamoDB_condition_Expression()

    assert result is mock_conditions