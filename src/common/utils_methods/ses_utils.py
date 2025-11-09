"""
Utilities for AWS SES (Simple Email Service) operations used by the strategies package.

This module provides low-level, descriptive methods for common and advanced
email operations, including sending emails with To, CC, and BCC addresses,
validating email addresses, and formatting email content.

All methods include logging and error handling for robust production use.
"""

from typing import List, Optional, Dict, Any
from common.client_record import ses_client
from common.models.logger import Logger
import re

logger = Logger(__name__)


class SESUtils:
    def __init__(self, region_name: str):
        self.region_name = region_name
        self.ses_client = ses_client(region_name)

    def _validate_email_address(self, email: str) -> bool:
        """
        Validate email address format using regex.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(email, str):
            return False

        # More robust email validation pattern
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _prepare_email_addresses(
        self,
        from_email: str,
        to_email: Optional[List[str]] = None,
        cc_email: Optional[List[str]] = None,
        bcc_email: Optional[List[str]] = None,
    ) -> tuple[str, List[str], List[str], List[str]]:
        """
        Validate and prepare email addresses for sending.

        Args:
            from_email: Sender email address
            to_email: List of recipient email addresses
            cc_email: List of CC email addresses
            bcc_email: List of BCC email addresses

        Returns:
            Tuple of (from_email, to_emails, cc_emails, bcc_emails)

        Raises:
            ValueError: If any email address is invalid
        """
        if not self._validate_email_address(from_email):
            raise ValueError(f"Invalid from_email address: {from_email}")

        to_email = to_email or []
        cc_email = cc_email or []
        bcc_email = bcc_email or []

        # Validate to_email addresses
        for email in to_email:
            if not self._validate_email_address(email):
                raise ValueError(f"Invalid to_email address: {email}")

        # Validate cc_email addresses
        for email in cc_email:
            if not self._validate_email_address(email):
                raise ValueError(f"Invalid cc_email address: {email}")

        # Validate bcc_email addresses
        for email in bcc_email:
            if not self._validate_email_address(email):
                raise ValueError(f"Invalid bcc_email address: {email}")

        return from_email, to_email, cc_email, bcc_email

    def send_email(
        self,
        from_email: str,
        to_email: Optional[List[str]] = None,
        cc_email: Optional[List[str]] = None,
        bcc_email: Optional[List[str]] = None,
        region_name: str = "us-east-1",
        subject: str = "",
        body_html: str = "",
    ) -> Dict[str, Any]:
        """
        Send an email using AWS SESv2.

        Args:
            from_email: Sender email address (string)
            to_email: List of recipient email addresses
            cc_email: List of CC email addresses (optional)
            bcc_email: List of BCC email addresses (optional)
            subject: Email subject
            body_html: Email body in HTML format

        Returns:
            SES send_email response dict

        Raises:
            ValueError: If email validation fails
            Exception: If SES send operation fails
        """
        try:
            _from_email, _to_email, _cc_email, _bcc_email = (
                self._prepare_email_addresses(from_email, to_email, cc_email, bcc_email)
            )

            logger.info(
                f"Sending email to {_to_email} with cc: {_cc_email} and bcc: {_bcc_email}"
            )
            logger.info(f"Email subject: {subject}")
            logger.debug(
                f"Email body: {body_html[:100]}..."
            )  # Log only first 100 chars

            response = self.ses_client.send_email(
                FromEmailAddress=_from_email,
                Destination={
                    "ToAddresses": _to_email,
                    "CcAddresses": _cc_email,
                    "BccAddresses": _bcc_email,
                },
                Content={
                    "Simple": {
                        "Subject": {"Data": subject, "Charset": "UTF-8"},
                        "Body": {"Html": {"Data": body_html, "Charset": "UTF-8"}},
                    }
                },
            )

            logger.info(
                f"Email sent successfully. MessageId: {response.get('MessageId')}"
            )
            return response

        except ValueError as ve:
            logger.error(f"Email validation error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error sending email via SES: {e}")
            raise
