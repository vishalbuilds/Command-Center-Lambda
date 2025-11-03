"""
Utilities for AWS Secrets Manager operations used by the strategies package.

This module provides low-level, descriptive methods for common and advanced 
Secrets Manager operations, including retrieving, creating, updating, and 
deleting secrets.

All methods include logging and error handling for robust production use.
"""

from common.client_record import secretsmanager_client
from common.models.logger import Logger

logger = Logger(__name__)


def get_secret(secret_name: str,region_name:str) -> str:
    """
    Retrieve a secret string from AWS Secrets Manager.

    :param secret_name: The name of the secret.
    :return: The secret string value.
    """
    try:
        logger.info(f'getting secreate from secretsmanager:{secret_name} from region:{region_name}')
        return secretsmanager_client(region_name).get_secret_value(SecretId=secret_name)
    except Exception as e:
        logger.error(f"Error in getting paginator: {e}")
        raise
