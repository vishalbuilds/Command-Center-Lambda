from common.utils_methods.dynamodb_utils_resource import (
    DynamoDBUtilsResource,
    TABLE_NAME,
    KEY_NAME,
    KEY_VALUE,
)
from common.models.default_strategy import DefaultStrategy
from common.models.logger import Logger
import os

LOGGER = Logger(__name__)

REGION = os.environ.get("REGION")


class DynamodbLookup(DefaultStrategy):
    def __init__(self, event):
        self.event = event
        table_name = self.event.get("TABLE_NAME")
        if not table_name:
            raise ValueError("TABLE_NAME must be provided in event")

        self.DynamoDB_Utils_Resource = DynamoDBUtilsResource(REGION, table_name)

    def do_validate(self):
        error = []

        if not self.event.get("TABLE_NAME"):
            LOGGER.error(f"Missing required parameter: TABLE_NAME")
            error.append(f"Missing required parameter: TABLE_NAME")

        if not self.event.get("KEY_NAME"):
            LOGGER.error(f"Missing required parameter: KEY_NAME")
            error.append(f"Missing required parameter: KEY_NAME")

        if not self.event.get("KEY_VALUE"):
            LOGGER.error(f"Missing required parameter: KEY_VALUE")
            error.append(f"Missing required parameter: KEY_VALUE")

        return (False, error) if error else (True, None)

    def do_operation(self):
        try:
            key_name = self.event.get("KEY_NAME")
            key_value = self.event.get("KEY_VALUE")
            table_name = self.event.get("TABLE_NAME")

            item_attr = self.DynamoDB_Utils_Resource.get_single_item_by_pk(
                key_name, key_value
            )

            LOGGER.info(
                f"Successfully found item value {item_attr} in table {table_name}"
            )
            return item_attr
        except Exception as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.error(f"DynamoDB lookup operation failed: {str(e)}")
            raise
