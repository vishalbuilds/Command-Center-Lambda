import boto3
from common.models.logger import Logger

logger = Logger(__name__)


def s3_client():
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
        s3 client
    """
    logger.info(f"Initating s3 client api")
    return boto3.client("s3")
