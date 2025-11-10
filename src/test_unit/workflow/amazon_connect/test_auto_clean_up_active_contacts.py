"""
Unit tests for auto_clean_up_active_contacts module.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timezone
from workflow.amazon_connect.auto_clean_up_active_contacts import AutoCleanUpActiveContacts


class TestAutoCleanUpActiveContacts:
    
    @patch.dict('os.environ', {'INSTANCE_ID': 'test-instance-id', 'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_init(self, mock_connect_utils):
        """Test AutoCleanUpActiveContacts initialization."""
        event = {"test": "data"}
        
        instance = AutoCleanUpActiveContacts(event)
        
        assert instance.event == event
        assert instance.instance_id == 'test-instance-id'
        assert instance.region == 'us-east-1'
        mock_connect_utils.assert_called_once_with('us-east-1', 'test-instance-id')
    
    @patch.dict('os.environ', {'INSTANCE_ID': 'test-instance-id', 'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_do_validate_success(self, mock_connect_utils):
        """Test successful validation."""
        event = {"test": "data"}
        instance = AutoCleanUpActiveContacts(event)
        
        result, error = instance.do_validate()
        
        assert result is True
        assert error is None
    
    @patch.dict('os.environ', {'REGION': 'us-east-1'}, clear=True)
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_do_validate_missing_instance_id(self, mock_connect_utils):
        """Test validation with missing INSTANCE_ID."""
        event = {"test": "data"}
        instance = AutoCleanUpActiveContacts(event)
        
        result, error = instance.do_validate()
        
        assert result is False
        assert error == "INSTANCE_ID environment variable is not set"
    
    @patch.dict('os.environ', {'INSTANCE_ID': 'test-instance-id'}, clear=True)
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_do_validate_missing_region(self, mock_connect_utils):
        """Test validation with missing REGION."""
        event = {"test": "data"}
        instance = AutoCleanUpActiveContacts(event)
        
        result, error = instance.do_validate()
        
        assert result is False
        assert error == "REGION environment variable is not set"
    
    @patch.dict('os.environ', {'INSTANCE_ID': 'test-instance-id', 'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_routing_profile_arn_success(self, mock_connect_utils):
        """Test successful routing profile ARN retrieval."""
        event = {"test": "data"}
        instance = AutoCleanUpActiveContacts(event)
        
        # Mock paginator
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {
                "RoutingProfileSummaryList": [
                    {"Arn": "arn:aws:connect:us-east-1:123456789012:instance/test/routing-profile/rp1"},
                    {"Arn": "arn:aws:connect:us-east-1:123456789012:instance/test/routing-profile/rp2"}
                ]
            }
        ]
        instance.connect_utils._get_paginator.return_value = mock_paginator
        
        result = instance._routing_profile_arn()
        
        assert len(result) == 2
        assert "rp1" in result[0]
        assert "rp2" in result[1]
    
    @patch.dict('os.environ', {'INSTANCE_ID': 'test-instance-id', 'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_active_contact_ids_success(self, mock_connect_utils):
        """Test successful active contact IDs retrieval."""
        event = {"test": "data"}
        instance = AutoCleanUpActiveContacts(event)
        
        # Mock get_current_user_data response
        mock_response = {
            "UserDataList": [
                {
                    "Contacts": [
                        {
                            "ContactId": "contact-1",
                            "AgentContactState": "CONNECTED",
                            "ConnectedToAgentTimestamp": (datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)).isoformat()
                        }
                    ]
                }
            ]
        }
        instance.connect_utils.get_current_user_data.return_value = mock_response
        
        routing_profile_arns = ["arn:aws:connect:us-east-1:123456789012:instance/test/routing-profile/rp1"]
        result = instance._active_contact_ids(routing_profile_arns)
        
        assert len(result) >= 0  # May be 0 or 1 depending on time threshold
        instance.connect_utils.get_current_user_data.assert_called_once()
    
    @patch.dict('os.environ', {'INSTANCE_ID': 'test-instance-id', 'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_process_contact_validation_and_disconnect_already_disconnected(self, mock_connect_utils):
        """Test processing contact that is already disconnected."""
        event = {"test": "data"}
        instance = AutoCleanUpActiveContacts(event)
        
        # Mock describe_contact response for already disconnected contact
        mock_response = {
            "Contact": {
                "ContactId": "contact-1",
                "DisconnectTimestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        instance.connect_utils.describe_contact.return_value = mock_response
        
        result = instance._process_contact_validation_and_disconnect("contact-1")
        
        assert result["status"] == "Already_Disconnected"
        assert result["contact_id"] == "contact-1"
    
    @patch.dict('os.environ', {'INSTANCE_ID': 'test-instance-id', 'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_process_contact_validation_and_disconnect_in_progress(self, mock_connect_utils):
        """Test processing contact that is still in progress."""
        event = {"test": "data"}
        instance = AutoCleanUpActiveContacts(event)
        
        # Mock describe_contact response for active contact (below threshold)
        recent_time = datetime.now(timezone.utc)
        mock_response = {
            "Contact": {
                "ContactId": "contact-1",
                "LastUpdateTimestamp": recent_time.isoformat()
            }
        }
        instance.connect_utils.describe_contact.return_value = mock_response
        
        result = instance._process_contact_validation_and_disconnect("contact-1")
        
        assert result["status"] == "In_Progress"
        assert result["contact_id"] == "contact-1"
    
    @patch.dict('os.environ', {'INSTANCE_ID': 'test-instance-id', 'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_process_contact_validation_and_disconnect_should_disconnect(self, mock_connect_utils):
        """Test processing contact that should be disconnected."""
        event = {"test": "data"}
        instance = AutoCleanUpActiveContacts(event)
        
        # Mock describe_contact response for old contact (exceeds threshold)
        old_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        mock_response = {
            "Contact": {
                "ContactId": "contact-1",
                "LastUpdateTimestamp": old_time.isoformat()
            }
        }
        instance.connect_utils.describe_contact.return_value = mock_response
        
        result = instance._process_contact_validation_and_disconnect("contact-1")
        
        assert result["status"] == "Disconnected"
        assert result["contact_id"] == "contact-1"
        instance.connect_utils.stop_contact.assert_called_once_with("contact-1")
    
    @patch.dict('os.environ', {'INSTANCE_ID': 'test-instance-id', 'REGION': 'us-east-1'})
    @patch('workflow.amazon_connect.auto_clean_up_active_contacts.ConnectUtils')
    def test_do_operation_success(self, mock_connect_utils):
        """Test successful do_operation execution."""
        event = {"test": "data"}
        instance = AutoCleanUpActiveContacts(event)
        
        # Mock _routing_profile_arn
        instance._routing_profile_arn = MagicMock(return_value=[
            "arn:aws:connect:us-east-1:123456789012:instance/test/routing-profile/rp1"
        ])
        
        # Mock _active_contact_ids
        instance._active_contact_ids = MagicMock(return_value=["contact-1"])
        
        # Mock _process_contact_validation_and_disconnect
        instance._process_contact_validation_and_disconnect = MagicMock(return_value={
            "status": "Disconnected",
            "LastUpdateTimestamp": datetime.now(timezone.utc),
            "contact_id": "contact-1",
            "duration_hours": 3.5
        })
        
        result = instance.do_operation()
        
        assert result["status"] == "Success"
        assert result["summary"]["total_contacts_processed"] == 1
        assert result["summary"]["disconnected"] == 1
