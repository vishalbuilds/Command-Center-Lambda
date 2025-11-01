import boto3
from common.logger import Logger
logger = Logger(__name__)

def sqs_client(region_name:str="us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
         amazon sqs client
    """
    logger.info(f"Initating Amazon Simple Queue Service (SQS) api with region:{region_name}")
    return boto3.client('sqs', region_name=region_name)

