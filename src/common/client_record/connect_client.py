import boto3
from common.logger import Logger
logger = Logger(__name__)

def connect_client(region_name:str="us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
         amazon connect client
    """
    logger.info(f"Initating amazon connect client api with region:{region_name}")
    return boto3.client('connect', region_name=region_name)

