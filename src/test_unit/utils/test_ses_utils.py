"""
Unit tests for ses_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from utils.ses_utils import send_email, _validate_email_address, _prepare_email_addresses

def test_validate_email_address_valid():
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "user+tag@example.com",
        "123@domain.com"
    ]
    for email in valid_emails:
        assert _validate_email_address(email) is True

def test_validate_email_address_invalid():
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
        assert _validate_email_address(email) is False

def test_prepare_email_addresses_valid():
    from_email = "sender@example.com"
    to_email = ["recipient1@example.com", "recipient2@example.com"]
    cc_email = ["cc@example.com"]
    bcc_email = ["bcc@example.com"]
    
    result = _prepare_email_addresses(from_email, to_email, cc_email, bcc_email)
    
    assert result[0] == from_email
    assert result[1] == to_email
    assert result[2] == cc_email
    assert result[3] == bcc_email

def test_prepare_email_addresses_invalid_from():
    with pytest.raises(ValueError, match="Invalid from_email address"):
        _prepare_email_addresses("invalid_email")

def test_prepare_email_addresses_invalid_to():
    with pytest.raises(ValueError, match="Invalid to_email address"):
        _prepare_email_addresses(
            "valid@example.com",
            ["valid@example.com", "invalid_email"]
        )

@patch('utils.ses_utils.ses_client')
def test_send_email_success(mock_ses_client):
    mock_client = MagicMock()
    mock_ses_client.return_value = mock_client
    mock_client.send_email.return_value = {"MessageId": "test-id"}
    
    result = send_email(
        from_email="sender@example.com",
        to_email=["recipient@example.com"],
        subject="Test Subject",
        body_html="<p>Test Body</p>"
    )
    
    assert result == {"MessageId": "test-id"}
    mock_client.send_email.assert_called_once()

@patch('utils.ses_utils.ses_client')
def test_send_email_error(mock_ses_client):
    mock_client = MagicMock()
    mock_ses_client.return_value = mock_client
    mock_client.send_email.side_effect = Exception("Test error")
    
    with pytest.raises(Exception, match="Test error"):
        send_email(
            from_email="sender@example.com",
            to_email=["recipient@example.com"],
            subject="Test Subject",
            body_html="<p>Test Body</p>"
        )