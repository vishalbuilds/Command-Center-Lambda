"""
Utilities for AWS Secrets Manager operations used by the strategies package.

This module provides low-level, descriptive methods for common and advanced
Secrets Manager operations, including retrieving, creating, updating, and
deleting secrets.

All methods include logging and error handling for robust production use.
"""

from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError, BotoCoreError
from common.client_record.secretsmanager_client import secretsmanager_client


logger = Logger(child=True)


class SecretsManagerUtils:

    def __init__(self, region_name: str):
        self.region_name = region_name
        self.secretsmanager_client = secretsmanager_client(region_name)

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve a secret string from AWS Secrets Manager.

        :param secret_name: The name of the secret.
        :return: The secret string value.
        """
        try:
            logger.info(
                f"getting secreate from secretsmanager:{secret_name} from region:{self.region_name}",
                extra={"secret_name": secret_name},
            )
            return self.secretsmanager_client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            logger.exception(
                f"AWS ClientError retrieving secret: {secret_name}",
                extra={
                    "secret_name": secret_name,
                    "error_code": e.response["Error"]["Code"],
                    "error_message": e.response["Error"]["Message"],
                },
            )
            raise
        except BotoCoreError:
            logger.exception(
                f"BotoCoreError retrieving secret: {secret_name}",
                extra={"secret_name": secret_name},
            )
            raise
        except Exception:
            logger.exception(
                f"Error retrieving secret: {secret_name}",
                extra={"secret_name": secret_name},
            )
            raise
