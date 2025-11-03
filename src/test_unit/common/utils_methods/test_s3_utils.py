"""
Unit tests for s3_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.s3_utils import (
    get_object, put_object, delete_object, 
    list_objects, create_presigned_url
)


class TestS3Utils:
    
    @patch('common.utils_methods.s3_utils.s3_client')
    def test_get_object_success(self, mock_s3_client):
        """Test successful get_object operation."""
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        mock_client.get_object.return_value = {
            'Body': b'test content',
            'ContentType': 'text/plain'
        }
        
        result = get_object('test-bucket', 'test-key', 'us-east-1')
        
        assert result['Body'] == b'test content'
        mock_client.get_object.assert_called_once_with(
            Bucket='test-bucket', 
            Key='test-key'
        )
    
    @patch('common.utils_methods.s3_utils.s3_client')
    def test_get_object_exception(self, mock_s3_client):
        """Test get_object with exception."""
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        mock_client.get_object.side_effect = Exception("Object not found")
        
        with pytest.raises(Exception, match="Object not found"):
            get_object('test-bucket', 'test-key', 'us-east-1')
    
    @patch('common.utils_methods.s3_utils.s3_client')
    def test_put_object_success(self, mock_s3_client):
        """Test successful put_object operation."""
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        mock_client.put_object.return_value = {'ETag': '"abc123"'}
        
        result = put_object('test-bucket', 'test-key', 'test content', 'us-east-1')
        
        assert result['ETag'] == '"abc123"'
        mock_client.put_object.assert_called_once_with(
            Bucket='test-bucket', 
            Key='test-key', 
            Body='test content'
        )
    
    @patch('common.utils_methods.s3_utils.s3_client')
    def test_delete_object_success(self, mock_s3_client):
        """Test successful delete_object operation."""
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        mock_client.delete_object.return_value = {'DeleteMarker': True}
        
        result = delete_object('test-bucket', 'test-key', 'us-east-1')
        
        assert result['DeleteMarker'] is True
        mock_client.delete_object.assert_called_once_with(
            Bucket='test-bucket', 
            Key='test-key'
        )
    
    @patch('common.utils_methods.s3_utils.s3_client')
    def test_list_objects_success(self, mock_s3_client):
        """Test successful list_objects operation."""
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        mock_client.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'test-prefix/file1.txt'},
                {'Key': 'test-prefix/file2.txt'}
            ]
        }
        
        result = list_objects('test-prefix', 'test-bucket', 'us-east-1')
        
        assert len(result['Contents']) == 2
        mock_client.list_objects_v2.assert_called_once_with(
            Bucket='test-bucket', 
            Prefix='test-prefix'
        )
    
    @patch('common.utils_methods.s3_utils.s3_client')
    def test_create_presigned_url_success(self, mock_s3_client):
        """Test successful create_presigned_url operation."""
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        mock_client.generate_presigned_url.return_value = 'https://test-url.com'
        
        result = create_presigned_url(
            'test-bucket', 'test-key', 'us-east-1', 
            expiration=7200, operation='get_object'
        )
        
        assert result == 'https://test-url.com'
        mock_client.generate_presigned_url.assert_called_once_with(
            ClientMethod='get_object',
            Params={'Bucket': 'test-bucket', 'Key': 'test-key'},
            ExpiresIn=7200
        )