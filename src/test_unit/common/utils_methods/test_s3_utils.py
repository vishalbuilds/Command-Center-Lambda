"""
Unit tests for s3_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.s3_utils import S3Utils


class TestS3Utils:
    
    @patch('common.utils_methods.s3_utils.s3_client')
    def test_init(self, mock_s3_client):
        """Test S3Utils initialization."""
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        
        utils = S3Utils('test-bucket')
        
        assert utils.bucket == 'test-bucket'
        assert utils.s3_client == mock_client
        mock_s3_client.assert_called_once()
    
    @patch('common.utils_methods.s3_utils.s3_client')
    def test_get_object_success(self, mock_s3_client):
        """Test successful get_object operation."""
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        mock_client.get_object.return_value = {
            'Body': b'test content',
            'ContentType': 'text/plain'
        }
        
        utils = S3Utils('test-bucket')
        result = utils.get_object('test-key')
        
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
        
        utils = S3Utils('test-bucket')
        with pytest.raises(Exception, match="Object not found"):
            utils.get_object('test-key')
    
    @patch('common.utils_methods.s3_utils.s3_client')
    def test_put_object_success(self, mock_s3_client):
        """Test successful put_object operation."""
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        mock_client.put_object.return_value = {'ETag': '"abc123"'}
        
        utils = S3Utils('test-bucket')
        result = utils.put_object('test-key', 'test content')
        
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
        
        utils = S3Utils('test-bucket')
        result = utils.delete_object('test-key')
        
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
        
        utils = S3Utils('test-bucket')
        result = utils.list_objects('test-prefix')
        
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
        
        utils = S3Utils('test-bucket')
        result = utils.create_presigned_url(
            'test-key', 
            expiration=7200, 
            operation='get_object'
        )
        
        assert result == 'https://test-url.com'
        mock_client.generate_presigned_url.assert_called_once_with(
            ClientMethod='get_object',
            Params={'Bucket': 'test-bucket', 'Key': 'test-key'},
            ExpiresIn=7200
        )