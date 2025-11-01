import boto3
from common.models.logger import Logger
logger = Logger(__name__)

def secretsmanager_client(region_name:str="us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
         amazon secretsmanager client
    """
    logger.info(f"Initating amazon secretsmanager client api with region:{region_name}")
    return boto3.client('secretsmanager', region_name=region_name)

