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
            InstanceId="instance-id",
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
            InstanceId="instance-id",
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

    # --- _get_paginator error handling ---

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_get_paginator_client_error(self, mock_connect_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Denied'}}, 'get_paginator'
        )
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ClientError):
            utils._get_paginator("list_contact_flows")

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_get_paginator_botocore_error(self, mock_connect_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = BotoCoreError()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(BotoCoreError):
            utils._get_paginator("list_contact_flows")

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_get_paginator_generic_error(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = Exception("unexpected")
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(Exception, match="unexpected"):
            utils._get_paginator("list_contact_flows")

    # --- list_contact_flow error handling ---

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_contact_flow_client_error(self, mock_connect_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Denied'}}, 'get_paginator'
        )
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ClientError):
            utils.list_contact_flow()

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_contact_flow_botocore_error(self, mock_connect_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = BotoCoreError()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(BotoCoreError):
            utils.list_contact_flow()

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_contact_flow_generic_error(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = Exception("fail")
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(Exception):
            utils.list_contact_flow()

    # --- list_routing_profile error handling ---

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_routing_profile_client_error(self, mock_connect_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Denied'}}, 'get_paginator'
        )
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ClientError):
            utils.list_routing_profile()

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_routing_profile_botocore_error(self, mock_connect_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = BotoCoreError()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(BotoCoreError):
            utils.list_routing_profile()

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_routing_profile_generic_error(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = Exception("fail")
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(Exception):
            utils.list_routing_profile()

    # --- list_queues error handling ---

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_queues_client_error(self, mock_connect_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Denied'}}, 'get_paginator'
        )
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ClientError):
            utils.list_queues()

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_queues_botocore_error(self, mock_connect_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = BotoCoreError()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(BotoCoreError):
            utils.list_queues()

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_list_queues_generic_error(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.get_paginator.side_effect = Exception("fail")
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(Exception):
            utils.list_queues()

    # --- describe_contact error handling ---

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_describe_contact_client_error(self, mock_connect_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.describe_contact.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Not found'}}, 'describe_contact'
        )
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ClientError):
            utils.describe_contact("contact-id")

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_describe_contact_botocore_error(self, mock_connect_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_client.describe_contact.side_effect = BotoCoreError()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(BotoCoreError):
            utils.describe_contact("contact-id")

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_describe_contact_generic_error(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.describe_contact.side_effect = Exception("fail")
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(Exception):
            utils.describe_contact("contact-id")

    # --- start_outbound_voice_contact ---

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_start_outbound_voice_contact_success(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.start_outbound_voice_contact.return_value = {"ContactId": "new-contact"}
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        result = utils.start_outbound_voice_contact(
            "Test", "+10000000001", "flow-id", SourcePhoneNumber="+10000000000"
        )

        assert result == {"ContactId": "new-contact"}
        mock_client.start_outbound_voice_contact.assert_called_once()

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_start_outbound_voice_contact_with_queue(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.start_outbound_voice_contact.return_value = {"ContactId": "new-contact"}
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        result = utils.start_outbound_voice_contact(
            "Test", "+10000000001", "flow-id", QueueId="queue-id"
        )

        assert result == {"ContactId": "new-contact"}

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_start_outbound_voice_contact_both_source_and_queue_raises(self, mock_connect_client):
        mock_client = MagicMock()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ValueError, match="Provide either SourcePhoneNumber or QueueId"):
            utils.start_outbound_voice_contact(
                "Test", "+10000000001", "flow-id",
                SourcePhoneNumber="+10000000000", QueueId="queue-id"
            )

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_start_outbound_voice_contact_client_error(self, mock_connect_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.start_outbound_voice_contact.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Denied'}},
            'start_outbound_voice_contact'
        )
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ClientError):
            utils.start_outbound_voice_contact("Test", "+10000000001", "flow-id")

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_start_outbound_voice_contact_botocore_error(self, mock_connect_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_client.start_outbound_voice_contact.side_effect = BotoCoreError()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(BotoCoreError):
            utils.start_outbound_voice_contact("Test", "+10000000001", "flow-id")

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_start_outbound_voice_contact_generic_error(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.start_outbound_voice_contact.side_effect = Exception("fail")
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(Exception):
            utils.start_outbound_voice_contact("Test", "+10000000001", "flow-id")

    # --- stop_contact error handling ---

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_stop_contact_client_error(self, mock_connect_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.stop_contact.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Not found'}}, 'stop_contact'
        )
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ClientError):
            utils.stop_contact("contact-id")

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_stop_contact_botocore_error(self, mock_connect_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_client.stop_contact.side_effect = BotoCoreError()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(BotoCoreError):
            utils.stop_contact("contact-id")

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_stop_contact_generic_error(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.stop_contact.side_effect = Exception("fail")
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(Exception):
            utils.stop_contact("contact-id")

    # --- tag_contact error handling ---

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_tag_contact_client_error(self, mock_connect_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.tag_contact.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Denied'}}, 'tag_contact'
        )
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ClientError):
            utils.tag_contact("contact-id", {"key": "val"})

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_tag_contact_botocore_error(self, mock_connect_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_client.tag_contact.side_effect = BotoCoreError()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(BotoCoreError):
            utils.tag_contact("contact-id", {"key": "val"})

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_tag_contact_generic_error(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.tag_contact.side_effect = Exception("fail")
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(Exception):
            utils.tag_contact("contact-id", {"key": "val"})

    # --- get_current_user_data error handling ---

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_get_current_user_data_client_error(self, mock_connect_client):
        from botocore.exceptions import ClientError
        mock_client = MagicMock()
        mock_client.get_current_user_data.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Denied'}}, 'get_current_user_data'
        )
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(ClientError):
            utils.get_current_user_data({"Queues": ["q1"]})

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_get_current_user_data_botocore_error(self, mock_connect_client):
        from botocore.exceptions import BotoCoreError
        mock_client = MagicMock()
        mock_client.get_current_user_data.side_effect = BotoCoreError()
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(BotoCoreError):
            utils.get_current_user_data({"Queues": ["q1"]})

    @patch('common.utils_methods.connect_utils.connect_client')
    def test_get_current_user_data_generic_error(self, mock_connect_client):
        mock_client = MagicMock()
        mock_client.get_current_user_data.side_effect = Exception("fail")
        mock_connect_client.return_value = mock_client

        utils = ConnectUtils("us-east-1", "instance-id")
        with pytest.raises(Exception):
            utils.get_current_user_data({"Queues": ["q1"]})
