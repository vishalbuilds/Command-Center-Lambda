"""
Unit tests for secretsmanager_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.secretsmanager_utils import get_secret


class TestSecretsManagerUtils:
    
    @patch('common.utils_methods.secretsmanager_utils.secretsmanager_client')
    def test_get_secret_success(self, mock_secretsmanager_client):
        """Test successful secret retrieval."""
        mock_client = MagicMock()
        mock_secretsmanager_client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': 'my-secret-value',
            'ARN': 'arn:aws:secretsmanager:us-east-1:123456789012:secret:test-secret'
        }
        
        result = get_secret('test-secret', 'us-east-1')
        
        assert result['SecretString'] == 'my-secret-value'
        mock_client.get_secret_value.assert_called_once_with(SecretId='test-secret')
    
    @patch('common.utils_methods.secretsmanager_utils.secretsmanager_client')
    def test_get_secret_exception(self, mock_secretsmanager_client):
        """Test get_secret with exception."""
        mock_client = MagicMock()
        mock_secretsmanager_client.return_value = mock_client
        mock_client.get_secret_value.side_effect = Exception("Secret not found")
        
        with pytest.raises(Exception, match="Secret not found"):
            get_secret('non-existent-secret', 'us-east-1')
