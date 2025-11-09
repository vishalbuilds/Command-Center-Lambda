import boto3
from common.models.logger import Logger

logger = Logger(__name__)


def ses_client(region_name: str = "us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
         amazon sesv2 client
    """
    logger.info(
        f"Initating Amazon Simple Email Service client v2 api with region:{region_name}"
    )
    return boto3.client("sesv2", region_name=region_name)
