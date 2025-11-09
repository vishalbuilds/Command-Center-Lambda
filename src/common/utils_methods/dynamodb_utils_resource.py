"""
DynamoDBUtils: A comprehensive utility class for DynamoDB CRUD and batch operations.

This class provides low-level, descriptive methods for common and advanced DynamoDB operations,
including single and batch CRUD, attribute-based queries, existence checks, and more.
All methods include logging and error handling for robust production use.
"""

from common.client_record.dynamodb_resource import (
    dynamoDB_resource,
    dynamoDB_condition_Expression,
)
from common.models.logger import Logger


TABLE_NAME = "tableName"
KEY_NAME = "keyName"
KEY_VALUE = "keyValue"


logger = Logger(__name__)


class DynamoDBUtilsResource:

    def __init__(self, region_name: str, table_name: str):
        self.region_name = region_name
        self.table_name = table_name
        self.dynamodb_table = dynamoDB_resource(region_name).Table(self.table_name)

    def _buid_dynamoDB_update_expression(
        self, update_data: dict
    ) -> tuple[str, dict, dict]:
        """
        build dynamoDB update expression for update_single_item_by_pk
        arg:
            update_data: data need to update in key and value pair {status:active, count:42}
        return:
            "SET #exp_status_key=new_status_value,#exp_count_key=new_count_value",

            {"#exp_status_key:status,
            #exp_count_key:count
            },

            {
            new_status_value:active,
            new_count_value:42
            }
        """
        update_parts = []
        expression_attr_name = {}
        expression_attr_values = {}
        for name, value in update_data.items():
            name_exp = f"#exp_{name}_key"
            value_exp = f":new_{name}_value"
            update_parts.append(f"{name_exp}={value_exp}")
            expression_attr_name[name_exp] = name
            expression_attr_values[value_exp] = value
        update_expression = "SET " + ", ".join(update_parts)
        return update_expression, expression_attr_name, expression_attr_values

    def get_single_item_by_pk(self, key_name: str, key_value: str) -> set:
        """
        Fetch a single item from a DynamoDB table by its primery key.
        Args:
            primary key_name (str: The primary key name of the item to fetch.
            primary key_value (str): The primary key value of the item to fetch.

        Returns:
            dict: The response from DynamoDB get_item.
        Raises:
            Exception: If the operation fails.
        """
        logger.info(
            f"Fetching item from {self.table_name} with key {key_name}:{key_value}"
        )
        try:
            response = self.dynamodb_table.get_item(key={key_name: key_value})

            if "item" in response:
                return response["item"]

        except Exception as e:
            logger.error(f"Error fetching item: {e}")
            raise

    def query_items_by_key_eq(
        self,
        index_name: str,
        key_name: str,
        key_value: str,
    ) -> set:
        """
        Fetch all items from a DynamoDB table where a given attribute matches a value.
        Args:
            primary key_name (str: The primary key name of the item to fetch.
            primary key_value (str): The primary key value of the item to fetch.
            index_name: name of key index within specified table
        Returns:
            dict: The response from DynamoDB scan.
        Raises:
            Exception: If the operation fails.
        """
        logger.info(
            f"Fetching item from {self.table_name} with key {key_name}:{key_value}"
        )
        try:
            response = self.dynamodb_table.query(
                IndexName=index_name,
                KeyConditionExpression=dynamoDB_condition_Expression()
                .Key(key_name)
                .eq(key_value),
            )

            if "item" in response:
                return response["item"]

        except Exception as e:
            logger.error(f"Error fetching item: {e}")
            raise

    def update_single_item_by_pk(
        self,
        update_data: dict,
        key_name: str,
        key_value: str,
    ) -> None:
        """
        Save (put) an item into a DynamoDB table. Optionally use a condition expression.
        Args:
            update_data (dict): The data to update in given table.
            key_name: primary key name
            key_value: primary key value
        Returns:
            dict: The response from DynamoDB put_item.
        Raises:
            Exception: If the operation fails.
        """
        logger.info(
            f"update data in {self.table_name} with primary key{key_name}:{key_value} and data{update_data}"
        )
        try:
            update_expression, expression_attr_name, expression_attr_values = (
                self._buid_dynamoDB_update_expression(update_data)
            )
            self.dynamodb_table.update_item(
                Key={key_name: key_value},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attr_name,
                ExpressionAttributeValues=expression_attr_values,
            )
        except Exception as e:
            logger.error(
                f"error in updating data in {self.table_name} with primary key{key_name}:{key_value} and data{update_data}"
            )
            raise

    def put_item(self, item: dict) -> None:
        logger.info(f"Putting data in {self.table_name} with item: {item}")
        try:
            self.dynamodb_table.put_item(Item=item)
        except Exception as e:
            logger.error(
                f"Error in putting data in {self.table_name} with item: {item}"
            )
            raise
