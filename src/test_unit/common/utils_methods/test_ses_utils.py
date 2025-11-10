"""
Unit tests for ses_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.ses_utils import SESUtils

class TestSESUtils:
    
    @patch('common.utils_methods.ses_utils.ses_client')
    def test_init(self, mock_ses_client):
        """Test SESUtils initialization."""
        mock_client = MagicMock()
        mock_ses_client.return_value = mock_client
        
        utils = SESUtils('us-east-1')
        
        assert utils.region_name == 'us-east-1'
        assert utils.ses_client == mock_client
        mock_ses_client.assert_called_once_with('us-east-1')
    
    @patch('common.utils_methods.ses_utils.ses_client')
    def test_validate_email_address_valid(self, mock_ses_client):
        """Test email validation with valid emails."""
        utils = SESUtils('us-east-1')
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.com",
            "123@domain.com"
        ]
        for email in valid_emails:
            assert utils._validate_email_address(email) is True
    
    @patch('common.utils_methods.ses_utils.ses_client')
    def test_validate_email_address_invalid(self, mock_ses_client):
        """Test email validation with invalid emails."""
        utils = SESUtils('us-east-1')
        
        invalid_emails = [
            "invalid",
            "@domain.com",
            "user@",
            "user@.com",
            None,
            123,
            "user@domain",
            "@",
            "user name@domain.com"
        ]
        for email in invalid_emails:
            assert utils._validate_email_address(email) is False
    
    @patch('common.utils_methods.ses_utils.ses_client')
    def test_prepare_email_addresses_valid(self, mock_ses_client):
        """Test email address preparation with valid addresses."""
        utils = SESUtils('us-east-1')
        
        from_email = "sender@example.com"
        to_email = ["recipient1@example.com", "recipient2@example.com"]
        cc_email = ["cc@example.com"]
        bcc_email = ["bcc@example.com"]
        
        result = utils._prepare_email_addresses(from_email, to_email, cc_email, bcc_email)
        
        assert result[0] == from_email
        assert result[1] == to_email
        assert result[2] == cc_email
        assert result[3] == bcc_email
    
    @patch('common.utils_methods.ses_utils.ses_client')
    def test_prepare_email_addresses_invalid_from(self, mock_ses_client):
        """Test email address preparation with invalid from address."""
        utils = SESUtils('us-east-1')
        
        with pytest.raises(ValueError, match="Invalid from_email address"):
            utils._prepare_email_addresses("invalid_email")
    
    @patch('common.utils_methods.ses_utils.ses_client')
    def test_prepare_email_addresses_invalid_to(self, mock_ses_client):
        """Test email address preparation with invalid to address."""
        utils = SESUtils('us-east-1')
        
        with pytest.raises(ValueError, match="Invalid to_email address"):
            utils._prepare_email_addresses(
                "valid@example.com",
                ["valid@example.com", "invalid_email"]
            )
    
    @patch('common.utils_methods.ses_utils.ses_client')
    def test_send_email_success(self, mock_ses_client):
        """Test successful email sending."""
        mock_client = MagicMock()
        mock_ses_client.return_value = mock_client
        mock_client.send_email.return_value = {"MessageId": "test-id"}
        
        utils = SESUtils('us-east-1')
        result = utils.send_email(
            from_email="sender@example.com",
            to_email=["recipient@example.com"],
            subject="Test Subject",
            body_html="<p>Test Body</p>"
        )
        
        assert result == {"MessageId": "test-id"}
        mock_client.send_email.assert_called_once()
    
    @patch('common.utils_methods.ses_utils.ses_client')
    def test_send_email_error(self, mock_ses_client):
        """Test email sending with error."""
        mock_client = MagicMock()
        mock_ses_client.return_value = mock_client
        mock_client.send_email.side_effect = Exception("Test error")
        
        utils = SESUtils('us-east-1')
        with pytest.raises(Exception, match="Test error"):
            utils.send_email(
                from_email="sender@example.com",
                to_email=["recipient@example.com"],
                subject="Test Subject",
                body_html="<p>Test Body</p>"
            )