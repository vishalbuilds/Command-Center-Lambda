import boto3
from common.logger import Logger
logger = Logger(__name__)

def dynamoDB_client(region_name:str="us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
        dynamodb client
    """
    logger.info(f"Initating dynamodb client api with region:{region_name}")
    return boto3.client('dynamodb', region_name=region_name)

