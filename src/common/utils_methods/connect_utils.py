"""
Utilities for Amazon Connect operations used by the strategies package.

This class provides low-level, descriptive methods for common and advanced Amazon Connect operations,
including user, queue, and contact flow management, real-time and historical metric retrieval,
and call control actions.

All methods include logging and error handling for robust production use.
"""

from common.client_record.connect_client import connect_client
from common.models.logger import Logger

logger = Logger(__name__)


class ConnectUtils:
    def __init__(self, region_name: str, instanceId: str):
        self.region_name = region_name
        self.instanceId = instanceId
        self.connect_client = connect_client(region_name)

    def _get_paginator(self, service: str):
        """Return a paginator for the given Amazon Connect service operation.

        Args:
            service: The name of the paginator operation (for example,
                `'list_contact_flows'`, `'list_routing_profiles'`, `'list_queues'`).
            region_name: AWS region name used to build the boto3 Connect client.

        Returns:
            A boto3 Paginator instance for the requested operation.

        Raises:
            Any exception raised by `connect_client(region_name).get_paginator` is
            propagated to the caller. Callers may choose to catch and log.
        """
        try:
            return self.connect_client.get_paginator(service)
        except Exception as e:
            logger.error(f"Error in getting paginator: {e}")
            raise

    def list_contact_flow(self):
        """List contact flow summaries for a Connect instance.

        This returns a flat list of contact flow summary dictionaries by paginating
        the `list_contact_flows` API.

        Args:
            region_name: AWS region where the Connect instance exists.
            instanceId: The Connect InstanceId to query.

        Returns:
            A list of contact flow summary dicts. If no contact flows exist an empty
            list is returned.
        """
        try:
            logger.info(f"Listing all contact flow from region:{self.region_name}")
            response_paginator = self._get_paginator(
                "list_contact_flows"
            ).paginate(
                InstanceId=self.instanceId,
            )
            return [
                contact_flow
                for response in response_paginator
                for contact_flow in response.get("ContactFlowSummaryList", [])
            ]
        except Exception as e:
            logger.error(f"Error in listing contact flows: {e}")
            raise

    def list_routing_profile(self):
        """List routing profile summaries for a Connect instance.

        Args:
            region_name: AWS region where the Connect instance exists.
            instanceId: The Connect InstanceId to query.

        Returns:
            A list of routing profile summary dicts. If no profiles exist an empty
            list is returned.
        """
        try:
            logger.info(f"Listing all routing profile from region:{self.region_name}")
            response_paginator = self._get_paginator(
                "list_routing_profiles"
            ).paginate(
                InstanceId=self.instanceId,
            )
            return [
                routing_profile
                for response in response_paginator
                for routing_profile in response.get("RoutingProfileSummaryList", [])
            ]
        except Exception as e:
            logger.error(f"Error in listing routing profiles: {e}")
            raise

    def list_queues(self):
        """List queue summaries for a Connect instance.

        Args:
            region_name: AWS region where the Connect instance exists.
            instanceId: The Connect InstanceId to query.

        Returns:
            A list of queue summary dicts. If no queues exist an empty list is
            returned.

        Note:
            The repository previously had a duplicate function name that returned
            queues but was named `list_routing_profile`. This function is the
            intended `list_queues` implementation and replaces that duplicate.
        """
        try:
            logger.info(f"Listing all queue from region:{self.region_name}")
            response_paginator = self._get_paginator(
                "list_queues"
            ).paginate(
                InstanceId=self.instanceId,
            )
            return [
                queue
                for response in response_paginator
                for queue in response.get("QueueSummaryList", [])
            ]
        except Exception as e:
            logger.error(f"Error in listing queues: {e}")
            raise

    def describe_contact(self, contactId: str):
        """Retrieve detailed information about a specific contact in Amazon Connect.

        Args:
            region_name: AWS region where the Connect instance exists.
            instanceId: The Connect InstanceId to query.
            contactId: The unique identifier of the contact to describe.

        Returns:
            A dictionary containing the contact's details from the Amazon Connect API.

        Raises:
            Exception: If there's an error retrieving the contact details, with the error
                logged before re-raising.
        """
        try:
            logger.info(
                f"Describing contact id {contactId} from region:{self.region_name}"
            )
            return self.connect_client.describe_contact(
                instanceId=self.instanceId, ContactId=contactId
            )
        except Exception as e:
            logger.error(f"Error in describing contact id {contactId}: {e}")
            raise

    def start_outbound_voice_contact(
        self,
        name: str,
        DestinationPhoneNumber: str,
        ContactFlowId: str,
        SourcePhoneNumber: str = None,
        QueueId: str = None,
    ):
        """Initiate an outbound voice contact through Amazon Connect.

        Args:
            name: The name of the contact.
            DestinationPhoneNumber: The phone number to call (E.164 format).
            ContactFlowId: The ID of the contact flow to use for this call.
            InstanceId: The Connect InstanceId where the call will be placed.
            region_name: AWS region where the Connect instance exists.
            SourcePhoneNumber: Optional. The phone number to use as the caller ID.
                If not provided, uses the instance's default outbound number.
            QueueId: Optional. The queue to place the call in if needed.

        Returns:
            A dictionary containing the contact's information including its ID.

        Raises:
            Exception: If there's an error initiating the outbound contact, with the error
                logged before re-raising.
        """
        try:
            if SourcePhoneNumber and ContactFlowId and QueueId:
                logger.error(
                    "add either queue name or source phone number or contact flow id"
                )
            logger.info(
                f"Inititing outbound voice contact all queue from region:{self.region_name},DestinationPhoneNumber:{DestinationPhoneNumber}"
            )
            return self.connect_client.start_outbound_voice_contact(
                name=name,
                DestinationPhoneNumber=DestinationPhoneNumber,
                ContactFlowId=ContactFlowId,
                InstanceId=self.InstanceId,
                SourcePhoneNumber=SourcePhoneNumber,
                QueueId=QueueId,
            )
        except Exception as e:
            logger.error(
                f"Error in start outbound voice contact with DestinationPhoneNumber{DestinationPhoneNumber} : {e}"
            )
            raise

    def stop_contact(self, contactId: str):
        """Terminate an active contact in Amazon Connect.

        This function forcefully ends the specified contact with a disconnect reason
        of 'OTHERS'. Use this carefully as it will immediately terminate the interaction.

        Args:
            region_name: AWS region where the Connect instance exists.
            instanceId: The Connect InstanceId where the contact exists.
            contactId: The unique identifier of the contact to terminate.

        Raises:
            Exception: If there's an error stopping the contact, with the error
                logged before re-raising.
        """
        try:
            logger.info(
                f"Disconnecting contact id {contactId} from region:{self.region_name}"
            )
            self.connect_client.stop_contact(
                instanceId=self.instanceId,
                ContactId=contactId,
                DisconnectReason={"Code": "OTHERS"},
            )
        except Exception as e:
            logger.error(f"Error in disconnecting contactId{contactId}: {e}")
            raise

    def tag_contact(self, contactId: str, tags: dict):
        """Add tags to a contact in Amazon Connect.

        Tags can be used for categorization, filtering, or tracking purposes.

        Args:
            region_name: AWS region where the Connect instance exists.
            instanceId: The Connect InstanceId where the contact exists.
            contactId: The unique identifier of the contact to tag.
            tags: A dictionary of tag key-value pairs to apply to the contact.
                Example: {'Department': 'Sales', 'Priority': 'High'}

        Raises:
            Exception: If there's an error tagging the contact, with the error
                logged before re-raising.
        """
        try:
            logger.info(f"tag contact id {contactId} from region:{self.region_name}")
            self.connect_client.tag_contact(
                instanceId=self.instanceId, ContactId=contactId, Tags=tags
            )
        except Exception as e:
            logger.error(f"Error in tagging contactId{contactId}: {e}")
            raise

    def get_current_user_data(self, filters: dict[str, list[str]]):
        """Retrieve current user data from Amazon Connect.
        arg:
            region_name: AWS region where the Connect instance exists.
            instanceId: The Connect InstanceId where the contact exists.
            filter:filter to get current user data
        Returns:
            A dictionary containing the current user data from the Amazon Connect API.
        """
        try:
            logger.info(f"Getting current user data from region:{self.region_name}")
            return self.connect_client.get_current_user_data(
                instanceId=self.instanceId, Filters=filters
            )
        except Exception as e:
            logger.error(f"Error in getting current user data: {e}")
            raise
