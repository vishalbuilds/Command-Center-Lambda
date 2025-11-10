"""
Unit tests for secretsmanager_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.secretsmanager_utils import SecretsManagerUtils


class TestSecretsManagerUtils:
    
    @patch('common.utils_methods.secretsmanager_utils.secretsmanager_client')
    def test_init(self, mock_secretsmanager_client):
        """Test SecretsManagerUtils initialization."""
        mock_client = MagicMock()
        mock_secretsmanager_client.return_value = mock_client
        
        utils = SecretsManagerUtils('us-east-1')
        
        assert utils.secretsmanager_client == mock_client
        mock_secretsmanager_client.assert_called_once_with('us-east-1')
    
    @patch('common.utils_methods.secretsmanager_utils.secretsmanager_client')
    def test_get_secret_success(self, mock_secretsmanager_client):
        """Test successful secret retrieval."""
        mock_client = MagicMock()
        mock_secretsmanager_client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': 'my-secret-value',
            'ARN': 'arn:aws:secretsmanager:us-east-1:123456789012:secret:test-secret'
        }
        
        utils = SecretsManagerUtils('us-east-1')
        result = utils.get_secret('test-secret')
        
        assert result['SecretString'] == 'my-secret-value'
        mock_client.get_secret_value.assert_called_once_with(SecretId='test-secret')
    
    @patch('common.utils_methods.secretsmanager_utils.secretsmanager_client')
    def test_get_secret_exception(self, mock_secretsmanager_client):
        """Test get_secret with exception."""
        mock_client = MagicMock()
        mock_secretsmanager_client.return_value = mock_client
        mock_client.get_secret_value.side_effect = Exception("Secret not found")
        
        utils = SecretsManagerUtils('us-east-1')
        with pytest.raises(Exception, match="Secret not found"):
            utils.get_secret('non-existent-secret')
