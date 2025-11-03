"""
Unit tests for s3_client module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.client_record.s3_client import s3_client


class TestS3Client:
    
    @patch('common.client_record.s3_client.boto3.client')
    def test_s3_client_success(self, mock_boto3_client):
        """Test successful S3 client creation."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        client = s3_client()
        
        assert client == mock_client
        mock_boto3_client.assert_called_once_with('s3', region_name='us-east-1')
    
    @patch('common.client_record.s3_client.boto3.client')
    def test_s3_client_with_region(self, mock_boto3_client):
        """Test S3 client creation with specific region."""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        client = s3_client(region_name='us-west-2')
        
        assert client == mock_client
        mock_boto3_client.assert_called_once_with('s3', region_name='us-west-2')
    
    @patch('common.client_record.s3_client.boto3.client')
    def test_s3_client_exception(self, mock_boto3_client):
        """Test S3 client creation with exception."""
        mock_boto3_client.side_effect = Exception("AWS credentials not found")
        
        with pytest.raises(Exception, match="AWS credentials not found"):
            s3_client()