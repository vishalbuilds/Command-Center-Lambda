"""
Unit tests for s3_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from utils.s3_utils import get_object, put_object, delete_object, list_objects, create_presigned_url

@pytest.fixture
def mock_s3_client():
    with patch('utils.s3_utils.s3_client') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client

def test_get_object(mock_s3_client):
    mock_s3_client.get_object.return_value = {"Body": "test content"}
    result = get_object("test-bucket", "test-key", "us-east-1")
    assert result == {"Body": "test content"}
    mock_s3_client.get_object.assert_called_once_with(Bucket="test-bucket", Key="test-key")

def test_get_object_error(mock_s3_client):
    mock_s3_client.get_object.side_effect = Exception("Test error")
    with pytest.raises(Exception, match="Test error"):
        get_object("test-bucket", "test-key", "us-east-1")

def test_put_object(mock_s3_client):
    mock_s3_client.put_object.return_value = {"ETag": "test-etag"}
    result = put_object("test-bucket", "test-key", "test content", "us-east-1")
    assert result == {"ETag": "test-etag"}
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="test-bucket", Key="test-key", Body="test content"
    )

def test_delete_object(mock_s3_client):
    mock_s3_client.delete_object.return_value = {"DeleteMarker": True}
    result = delete_object("test-bucket", "test-key", "us-east-1")
    assert result == {"DeleteMarker": True}
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket="test-bucket", Key="test-key"
    )

def test_list_objects(mock_s3_client):
    mock_s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "test-key"}]
    }
    result = list_objects("test-prefix", "test-bucket", "us-east-1")
    assert result == {"Contents": [{"Key": "test-key"}]}
    mock_s3_client.list_objects_v2.assert_called_once_with(
        Bucket="test-bucket", Prefix="test-prefix"
    )

def test_create_presigned_url(mock_s3_client):
    mock_s3_client.generate_presigned_url.return_value = "https://test-url"
    result = create_presigned_url("test-bucket", "test-key", "us-east-1")
    assert result == "https://test-url"
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod="get_object",
        Params={"Bucket": "test-bucket", "Key": "test-key"},
        ExpiresIn=3600
    )