"""
Utilities for AWS SQS (Simple Queue Service) operations used by the strategies package.

This module provides low-level, descriptive methods for common and advanced
SQS operations, including sending messages, receiving messages (with long polling support),
deleting messages, and managing message attributes.

All methods include logging and error handling for robust production use.
"""

from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError, BotoCoreError
from common.client_record.sqs_client import sqs_client


logger = Logger(child=True)

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
            message: The body text of the message
            message_attr: Custom attributes of the message (key-value pairs)

        Returns:
            The response from SQS that contains the assigned message ID
        """
        message_attributes = self._create_message_attributes(message_attr)
        try:
            logger.info(
                "Sending message to SQS",
                extra={
                    "queue_url": self.queue_url,
                    "message": message,
                    "message_attributes": message_attributes,
                },
            )

            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message,
                MessageAttributes=message_attributes,
            )

            logger.info(
                "Message sent successfully",
                extra={"message_id": response.get("MessageId", "unknown")},
            )
            return response

        except ClientError as e:
            logger.exception(
                "AWS ClientError sending message to SQS",
                extra={
                    "queue_url": self.queue_url,
                    "message": message,
                    "message_attributes": message_attributes,
                    "error_code": e.response["Error"]["Code"],
                    "error_message": e.response["Error"]["Message"],
                },
            )
            raise
        except BotoCoreError:
            logger.exception(
                "BotoCoreError sending message to SQS",
                extra={
                    "queue_url": self.queue_url,
                    "message": message,
                    "message_attributes": message_attributes,
                },
            )
            raise
        except Exception:
            logger.exception(
                "Error sending message to SQS",
                extra={
                    "queue_url": self.queue_url,
                    "message": message,
                    "message_attributes": message_attributes,
                },
            )
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
            message_ids: Dictionary of message attribute keys and values to match
            max_messages: Maximum messages to retrieve per request (1-10)
            visibility_timeout: How long the message stays invisible after retrieval (seconds)
            wait_time: Long polling wait time in seconds (0-20)
            auto_delete: If True, automatically delete the message after retrieval
            max_polling_attempts: Maximum number of polling attempts

        Returns:
            The matching message or None if not found
        """
        polling_attempt = 0
        checked_receipt_handles = set()

        try:
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
                        "No messages found in queue",
                        extra={
                            "attempt": polling_attempt + 1,
                            "max_attempts": max_polling_attempts,
                        },
                    )
                    polling_attempt += 1
                    continue

                for message in response["Messages"]:
                    receipt_handle = message["ReceiptHandle"]

                    if receipt_handle in checked_receipt_handles:
                        logger.info(
                            "Skipping already-checked message",
                            extra={"receipt_handle": receipt_handle},
                        )
                        continue

                    checked_receipt_handles.add(receipt_handle)

                    message_attr = message.get("MessageAttributes", {})
                    is_match = all(
                        key in message_attr
                        and message_attr[key].get("StringValue") == value
                        for key, value in message_ids.items()
                    )

                    if is_match:
                        logger.info(
                            "Found matching message",
                            extra={
                                "message_ids": message_ids,
                                "receipt_handle": receipt_handle,
                            },
                        )

                        if auto_delete:
                            self.delete_message(receipt_handle)
                            logger.info(
                                "Matching message auto-deleted from queue",
                                extra={"message_ids": message_ids},
                            )

                        return message

                    else:
                        self.change_message_visibility(
                            receipt_handle, visibility_timeout=0
                        )
                        logger.info(
                            "Returned non-matching message to queue",
                            extra={"receipt_handle": receipt_handle},
                        )

                polling_attempt += 1

            logger.info(
                "Message not found after max polling attempts",
                extra={
                    "message_ids": message_ids,
                    "max_polling_attempts": max_polling_attempts,
                    "total_unique_checked": len(checked_receipt_handles),
                    "checked_receipt_handles": list(checked_receipt_handles),
                },
            )
            return None

        except ClientError as e:
            logger.exception(
                "AWS ClientError receiving message from SQS",
                extra={
                    "queue_url": self.queue_url,
                    "message_ids": message_ids,
                    "error_code": e.response["Error"]["Code"],
                    "error_message": e.response["Error"]["Message"],
                },
            )
            raise
        except BotoCoreError:
            logger.exception(
                "BotoCoreError receiving message from SQS",
                extra={
                    "queue_url": self.queue_url,
                    "message_ids": message_ids,
                },
            )
            raise
        except Exception:
            logger.exception(
                "Error receiving message from SQS",
                extra={
                    "queue_url": self.queue_url,
                    "message_ids": message_ids,
                    "max_messages": max_messages,
                    "visibility_timeout": visibility_timeout,
                    "wait_time": wait_time,
                    "auto_delete": auto_delete,
                    "max_polling_attempts": max_polling_attempts,
                    "checked_receipt_handles": list(checked_receipt_handles),
                },
            )
            raise

    def change_message_visibility(
        self, receipt_handle: str, visibility_timeout: int = 0
    ):
        """
        Change the visibility timeout of a message in the queue.

        Args:
            receipt_handle: Receipt handle from receive_message
            visibility_timeout: New visibility timeout in seconds (0 = immediate reappearance)
        """
        try:
            self.sqs_client.change_message_visibility(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
                VisibilityTimeout=visibility_timeout,
            )
            logger.debug(
                "Changed message visibility",
                extra={
                    "receipt_handle": receipt_handle,
                    "visibility_timeout": visibility_timeout,
                },
            )

        except ClientError as e:
            logger.exception(
                "AWS ClientError changing message visibility",
                extra={
                    "receipt_handle": receipt_handle,
                    "visibility_timeout": visibility_timeout,
                    "queue_url": self.queue_url,
                    "error_code": e.response["Error"]["Code"],
                    "error_message": e.response["Error"]["Message"],
                },
            )
            raise
        except BotoCoreError:
            logger.exception(
                "BotoCoreError changing message visibility",
                extra={
                    "receipt_handle": receipt_handle,
                    "visibility_timeout": visibility_timeout,
                    "queue_url": self.queue_url,
                },
            )
            raise
        except Exception:
            logger.exception(
                "Error changing message visibility",
                extra={
                    "receipt_handle": receipt_handle,
                    "visibility_timeout": visibility_timeout,
                    "queue_url": self.queue_url,
                },
            )
            raise

    def delete_message(self, receipt_handle: str):
        """
        Delete a message from the queue.

        Args:
            receipt_handle: The receipt handle from receive_message

        Returns:
            None
        """
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url, ReceiptHandle=receipt_handle
            )
            logger.info(
                "Message deleted successfully",
                extra={"receipt_handle": receipt_handle},
            )

        except ClientError as e:
            logger.exception(
                "AWS ClientError deleting message from SQS",
                extra={
                    "receipt_handle": receipt_handle,
                    "queue_url": self.queue_url,
                    "error_code": e.response["Error"]["Code"],
                    "error_message": e.response["Error"]["Message"],
                },
            )
            raise
        except BotoCoreError:
            logger.exception(
                "BotoCoreError deleting message from SQS",
                extra={
                    "receipt_handle": receipt_handle,
                    "queue_url": self.queue_url,
                },
            )
            raise
        except Exception:
            logger.exception(
                "Error deleting message from SQS",
                extra={
                    "receipt_handle": receipt_handle,
                    "queue_url": self.queue_url,
                },
            )
            raise
