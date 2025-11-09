import boto3
from common.models.logger import Logger

logger = Logger(__name__)


def transcribe_client(region_name: str = "us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
        transcribe client
    """
    logger.info(f"Initating transcribe api with region:{region_name}")
    return boto3.client("transcribe", region_name=region_name)
