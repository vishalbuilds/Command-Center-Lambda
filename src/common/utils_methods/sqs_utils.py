"""
Utilities for AWS SQS (Simple Queue Service) operations used by the strategies package.

This module provides low-level, descriptive methods for common and advanced
SQS operations, including sending messages, receiving messages (with long polling support),
deleting messages, and managing message attributes.

All methods include logging and error handling for robust production use.
"""

from common.client_record.sqs_client import sqs_client
from common.models.logger import Logger

logger = Logger(__name__)


MAX_POLLING_ATTEMPTS = 10


class SQSUtils:
    def __init__(self, queue_url: str, region_name: str):
        self.region_name = region_name
        self.queue_url = queue_url
        self.sqs_client = sqs_client(region_name)

    def _create_message_attributes(self, message_attr: dict) -> dict:
        """
        Convert a dictionary to SQS message attribute format.

        Args:
            message_attr: Dictionary of key-value pairs to convert

        Returns:
            Dictionary formatted for SQS MessageAttributes
        """
        if not message_attr:
            return {}

        message_attr_str = {
            key if isinstance(key, str) else str(key): (
                value if isinstance(value, str) else str(value)
            )
            for key, value in message_attr.items()
        }

        return {
            key: {"StringValue": value, "DataType": "String"}
            for key, value in message_attr_str.items()
        }

    def send_message(self, message: str, message_attr: dict = None):
        """
        Send a message to an Amazon SQS queue.

        Args:
            queue: The queue URL that receives the message
            message: The body text of the message
            region: AWS region name
            message_attr: Custom attributes of the message (key-value pairs)

        Returns:
            The response from SQS that contains the assigned message ID
        """
        try:
            message_attributes = self._create_message_attributes(message_attr)
            logger.info(
                f"Sending message to {self.queue_url} with body: {message} and attributes: {message_attributes}"
            )

            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message,
                MessageAttributes=message_attributes,
            )

            message_id = response.get("MessageId", "unknown")
            logger.info(f"Sent message with id {message_id}")
            return response

        except Exception as e:
            logger.error(f"Error sending message to SQS: {e}")
            raise

    def receive_message(
        self,
        message_ids: dict[str, str],
        max_messages: int = 10,
        visibility_timeout: int = 30,
        wait_time: int = 5,
        auto_delete: bool = False,
        max_polling_attempts: int = MAX_POLLING_ATTEMPTS,
    ):
        """
        Receive a specific message by its custom message attributes.

        Args:
            queue: SQS queue URL
            message_ids: Dictionary of message attribute keys and values to match
            region_name: AWS region name
            max_messages: Maximum messages to retrieve per request (1-10)
            visibility_timeout: How long the message stays invisible after retrieval (seconds)
            wait_time: Long polling wait time in seconds (0-20)
            auto_delete: If True, automatically delete the message after retrieval
            max_polling_attempts: Maximum number of polling attempts

        Returns:
            The matching message or None if not found
        """
        try:
            polling_attempt = 0
            checked_receipt_handles = set()

            while polling_attempt < max_polling_attempts:
                response = self.sqs_client.receive_message(
                    QueueUrl=self.queue_url,
                    MessageAttributeNames=(
                        list(message_ids.keys()) if message_ids else ["All"]
                    ),
                    MaxNumberOfMessages=max_messages,
                    VisibilityTimeout=visibility_timeout,
                    WaitTimeSeconds=wait_time,
                )

                if "Messages" not in response:
                    logger.info(
                        f"No messages found in queue (attempt {polling_attempt + 1}/{max_polling_attempts})"
                    )
                    polling_attempt += 1
                    continue

                for message in response["Messages"]:
                    receipt_handle = message["ReceiptHandle"]

                    # Skip already-checked messages
                    if receipt_handle in checked_receipt_handles:
                        logger.debug(
                            f"Skipping already-checked message with receipt handle: {receipt_handle}"
                        )
                        continue

                    checked_receipt_handles.add(receipt_handle)

                    # Check if message attributes match
                    message_attr = message.get("MessageAttributes", {})
                    if all(
                        key in message_attr
                        and message_attr[key].get("StringValue") == value
                        for key, value in message_ids.items()
                    ):
                        logger.info(
                            f"Found matching message for attributes {message_ids}"
                        )

                        if auto_delete:
                            self.delete_message(receipt_handle)
                            logger.info(
                                f"Message with attributes {message_ids} auto-deleted from queue"
                            )

                        return message
                    else:
                        # Return non-matching message to queue immediately
                        self.change_message_visibility(
                            receipt_handle, visibility_timeout=0
                        )
                        logger.debug(f"Returned non-matching message to queue")

                polling_attempt += 1

            logger.warning(
                f"Message with attributes {message_ids} not found after {max_polling_attempts} attempts"
            )
            logger.info(
                f"Total unique messages checked: {len(checked_receipt_handles)}"
            )
            return None

        except Exception as e:
            logger.error(f"Error receiving message from SQS: {e}")
            raise

    def change_message_visibility(
        self, receipt_handle: str, visibility_timeout: int = 0
    ):
        """
        Change the visibility timeout of a message in the queue.

        Args:
            queue: SQS queue URL
            receipt_handle: Receipt handle from receive_message
            region_name: AWS region name
            visibility_timeout: New visibility timeout in seconds (0 = immediate reappearance)
        """
        try:
            self.sqs_client.change_message_visibility(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
                VisibilityTimeout=visibility_timeout,
            )
            logger.debug(f"Changed message visibility to {visibility_timeout}s")

        except Exception as e:
            logger.error(f"Error changing message visibility in SQS: {e}")
            raise

    def delete_message(self, receipt_handle: str):
        """
        Delete a message from the queue.

        Args:
            receipt_handle: The receipt handle from receive_message
            queue_url: SQS queue URL
            region_name: AWS region name

        Returns:
            None
        """
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url, ReceiptHandle=receipt_handle
            )
            logger.info(
                f"Message deleted successfully with receipt_handle: {receipt_handle}"
            )

        except Exception as e:
            logger.error(f"Error deleting message from SQS: {e}")
            raise
