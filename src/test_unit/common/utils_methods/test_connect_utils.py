"""
Unit tests for connect_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.connect_utils import (
    list_contact_flow, list_routing_profile, list_queues, 
    describe_contact, start_outbound_voice_contact, stop_contact, tag_contact
)


class TestConnectUtils:
    
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
        
        result = list_contact_flow("us-east-1", "instance-id")
        
        assert result == [{"Id": "cf1", "Name": "Flow1"}]
        mock_client.get_paginator.assert_called_once_with('list_contact_flows')
    
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
        
        result = list_routing_profile("us-east-1", "instance-id")
        
        assert result == [{"Id": "rp1", "Name": "Profile1"}]
        mock_client.get_paginator.assert_called_once_with('list_routing_profiles')
    
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
        
        result = list_queues("us-east-1", "instance-id")
        
        assert result == [{"Id": "q1", "Name": "Queue1"}]
        mock_client.get_paginator.assert_called_once_with('list_queues')
    
    @patch('common.utils_methods.connect_utils.connect_client')
    def test_stop_contact_success(self, mock_connect_client):
        """Test successful contact stopping."""
        mock_client = MagicMock()
        mock_connect_client.return_value = mock_client
        
        stop_contact("us-east-1", "instance-id", "contact-id")
        
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
        
        tags = {"Department": "Sales", "Priority": "High"}
        tag_contact("us-east-1", "instance-id", "contact-id", tags)
        
        mock_client.tag_contact.assert_called_once_with(
            instanceId="instance-id",
            ContactId="contact-id",
            Tags=tags
        )
