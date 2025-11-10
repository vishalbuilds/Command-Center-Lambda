"""
Unit tests for connect_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.connect_utils import ConnectUtils


class TestConnectUtils:
    
    @patch('common.utils_methods.connect_utils.connect_client')
    def test_init(self, mock_connect_client):
        """Test ConnectUtils initialization."""
        mock_client = MagicMock()
        mock_connect_client.return_value = mock_client
        
        utils = ConnectUtils("us-east-1", "instance-id")
        
        assert utils.region_name == "us-east-1"
        assert utils.instanceId == "instance-id"
        assert utils.connect_client == mock_client
        mock_connect_client.assert_called_once_with("us-east-1")
    
    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_contact_flow_success(self, mock_connect_client):
        """Test successful contact flow listing."""
        mock_client = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {"ContactFlowSummaryList": [{"Id": "cf1", "Name": "Flow1"}]}
        ]
        mock_client.get_paginator.return_value = mock_paginator
        mock_connect_client.return_value = mock_client
        
        utils = ConnectUtils("us-east-1", "instance-id")
        result = utils.list_contact_flow()
        
        assert result == [{"Id": "cf1", "Name": "Flow1"}]
    
    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_routing_profile_success(self, mock_connect_client):
        """Test successful routing profile listing."""
        mock_client = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {"RoutingProfileSummaryList": [{"Id": "rp1", "Name": "Profile1"}]}
        ]
        mock_client.get_paginator.return_value = mock_paginator
        mock_connect_client.return_value = mock_client
        
        utils = ConnectUtils("us-east-1", "instance-id")
        result = utils.list_routing_profile()
        
        assert result == [{"Id": "rp1", "Name": "Profile1"}]
    
    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_queues_success(self, mock_connect_client):
        """Test successful queue listing."""
        mock_client = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {"QueueSummaryList": [{"Id": "q1", "Name": "Queue1"}]}
        ]
        mock_client.get_paginator.return_value = mock_paginator
        mock_connect_client.return_value = mock_client
        
        utils = ConnectUtils("us-east-1", "instance-id")
        result = utils.list_queues()
        
        assert result == [{"Id": "q1", "Name": "Queue1"}]
    
    @patch('common.utils_methods.connect_utils.connect_client')
    def test_stop_contact_success(self, mock_connect_client):
        """Test successful contact stopping."""
        mock_client = MagicMock()
        mock_connect_client.return_value = mock_client
        
        utils = ConnectUtils("us-east-1", "instance-id")
        utils.stop_contact("contact-id")
        
        mock_client.stop_contact.assert_called_once_with(
            instanceId="instance-id",
            ContactId="contact-id",
            DisconnectReason={'Code': 'OTHERS'}
        )
    
    @patch('common.utils_methods.connect_utils.connect_client')
    def test_tag_contact_success(self, mock_connect_client):
        """Test successful contact tagging."""
        mock_client = MagicMock()
        mock_connect_client.return_value = mock_client
        
        utils = ConnectUtils("us-east-1", "instance-id")
        tags = {"Department": "Sales", "Priority": "High"}
        utils.tag_contact("contact-id", tags)
        
        mock_client.tag_contact.assert_called_once_with(
            instanceId="instance-id",
            ContactId="contact-id",
            Tags=tags
        )
    
    @patch('common.utils_methods.connect_utils.connect_client')
    def test_describe_contact_success(self, mock_connect_client):
        """Test successful contact description."""
        mock_client = MagicMock()
        mock_client.describe_contact.return_value = {"ContactId": "contact-id"}
        mock_connect_client.return_value = mock_client
        
        utils = ConnectUtils("us-east-1", "instance-id")
        result = utils.describe_contact("contact-id")
        
        assert result == {"ContactId": "contact-id"}
        mock_client.describe_contact.assert_called_once()
    
    @patch('common.utils_methods.connect_utils.connect_client')
    def test_get_current_user_data_success(self, mock_connect_client):
        """Test successful get current user data."""
        mock_client = MagicMock()
        mock_client.get_current_user_data.return_value = {"UserData": "data"}
        mock_connect_client.return_value = mock_client
        
        utils = ConnectUtils("us-east-1", "instance-id")
        filters = {"Queues": ["queue-id"]}
        result = utils.get_current_user_data(filters)
        
        assert result == {"UserData": "data"}
        mock_client.get_current_user_data.assert_called_once()
