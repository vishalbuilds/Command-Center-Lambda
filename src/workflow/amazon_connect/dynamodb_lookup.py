from common.utils_methods.dynamodb_utils_resource import (
    DynamoDBUtilsResource,
    TABLE_NAME,
    KEY_NAME,
    KEY_VALUE,
)
from common.models.default_strategy import DefaultStrategy
from aws_lambda_powertools import Logger
import os

logger = Logger()


class DynamodbLookup(DefaultStrategy):
    def __init__(self, event):
        self.event = event
        table_name = self.event.get("TABLE_NAME")
        if not table_name:
            raise ValueError("TABLE_NAME must be provided in event")

        region = os.environ.get("REGION")
        self.DynamoDB_Utils_Resource = DynamoDBUtilsResource(region, table_name)

    def do_validate(self):
        error = []

        if not self.event.get("KEY_NAME"):
            logger.error(f"Missing required parameter: KEY_NAME")
            error.append(f"Missing required parameter: KEY_NAME")

        if not self.event.get("KEY_VALUE"):
            logger.error(f"Missing required parameter: KEY_VALUE")
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

            logger.info(
                f"Successfully found item value {item_attr} in table {table_name}"
            )
            return item_attr
        except Exception as e:
            logger.info("Error occurred in DynamoDB lookup", extra={"error": str(e)})
            logger.exception(f"DynamoDB lookup operation failed: {str(e)}")
            raise
