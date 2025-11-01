import boto3
from common.logger import Logger
logger = Logger(__name__)

def s3_client(region_name:str="us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
        s3 client
    """
    logger.info(f"Initating s3 client api with region:{region_name}")
    return boto3.client('s3', region_name=region_name)
