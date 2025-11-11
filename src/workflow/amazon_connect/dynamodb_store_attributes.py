from common.utils_methods.dynamodb_utils_resource import DynamoDBUtilsResource
from common.models.default_strategy import DefaultStrategy
from common.models.logger import Logger
import os

LOGGER = Logger(__name__)
REGION = os.environ.get("REGION")


class DynamoDBStoreAttributes(DefaultStrategy):
    """
    Strategy: Store Amazon Connect Contact Event details into DynamoDB.

    This strategy expects the event to contain:
        - TABLE_NAME : DynamoDB table name to store record
        - KEY_NAME   : Primary key attribute name in table
        - KEY_VALUE  : Primary key value

    The event coming from Connect flow must contain `detail.contactData` object.
    Data will be customized and stored as single item in DynamoDB table.
    """

    def __init__(self, event: dict):
        self.event = event
        table_name = self.event.get("TABLE_NAME")
        if not table_name:
            raise ValueError("TABLE_NAME must be provided in event")

        self.dynamodb_resource = DynamoDBUtilsResource(REGION, table_name)

    def _customise_data_from_connect_event(self, event: dict) -> dict:
        """
        Extract and reshape useful subset of event data.
        Modify this based on requirement / schema.
        """
        contact_data = event.get("detail", {}).get("contactData", {})

        return {
            self.event.get("KEY_NAME"): self.event.get(
                "KEY_VALUE"
            ),  # required primary key
            "phone_number": contact_data.get("phoneNumber"),
            "status": contact_data.get("status"),
            "timestamp": contact_data.get("timestamp"),
            "type": contact_data.get("type"),
            "direction": contact_data.get("direction"),
        }

    def do_validate(self):
        """
        Check if required event parameters exist.
        """
        missing_fields = []

        for key in ["TABLE_NAME", "KEY_NAME", "KEY_VALUE"]:
            if not self.event.get(key):
                LOGGER.error(f"Missing required parameter: {key}")
                missing_fields.append(f"Missing required parameter: {key}")

        return (False, missing_fields) if missing_fields else (True, None)

    def do_operation(self):
        """
        Perform the actual DynamoDB insert operation.
        """
        try:
            payload = self._customise_data_from_connect_event(self.event)
            self.dynamodb_resource.put_item(payload)

            LOGGER.info(f"Record saved successfully in DynamoDB. Payload: {payload}")

        except Exception as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.error(f"DynamoDB operation failed: {str(e)}")
            raise
