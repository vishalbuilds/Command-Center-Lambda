"""
Unit tests for dynamodb_client module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.client_record.dynamodb_client import dynamoDB_client


class TestDynamoDBClient:
    
    @patch('common.client_record.dynamodb_client.boto3.client')
    def test_dynamodb_client_success(self, mock_boto3_client):
        """Test successful DynamoDB client creation."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        client = dynamoDB_client()
        
        assert client == mock_client
        mock_boto3_client.assert_called_once_with('dynamodb', region_name='us-east-1')
    
    @patch('common.client_record.dynamodb_client.boto3.client')
    def test_dynamodb_client_with_region(self, mock_boto3_client):
        """Test DynamoDB client creation with specific region."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        client = dynamoDB_client(region_name='eu-west-1')
        
        assert client == mock_client
        mock_boto3_client.assert_called_once_with('dynamodb', region_name='eu-west-1')
    
    @patch('common.client_record.dynamodb_client.boto3.client')
    def test_dynamodb_client_exception(self, mock_boto3_client):
        """Test DynamoDB client creation with exception."""
        mock_boto3_client.side_effect = Exception("Service unavailable")
        
        with pytest.raises(Exception, match="Service unavailable"):
            dynamoDB_client()