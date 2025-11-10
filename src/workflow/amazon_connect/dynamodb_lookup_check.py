from workflow.amazon_connect.dynamodb_lookup import DynamodbLookup
from common.models.logger import Logger

LOGGER = Logger(__name__)


class DynamoDBLookupCheck(DynamodbLookup):

    def do_operation(self):
        try:
            key_name = self.event.get("KEY_NAME")
            key_value = self.event.get("KEY_VALUE")
            table_name = self.event.get("TABLE_NAME")

            item_attr = self.DynamoDB_Utils_Resource.get_single_item_by_pk(
                key_name, key_value
            )

            if item_attr:
                message = f"Item found in table: {table_name}"
                LOGGER.info(message)
                return {"exists": True, "message": message, "item": item_attr}
            else:
                message = f"Item not found in table: {table_name}"
                LOGGER.info(message)
                return {"exists": False, "message": message, "item": None}

        except Exception as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.error(f"DynamoDB lookup operation failed: {str(e)}")
            raise
