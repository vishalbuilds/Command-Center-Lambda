import boto3
from common.logger import Logger



def connect_client(region_name:str="us-east-1"):
    """
    Return a Amazon Simple Queue Service (SQS)
    arg:
        region_name: AWS region name of the amazon connect (default:us-east-1 )
    """
    Logger.info(f"Initating Amazon Simple Queue Service (SQS) api with region:{region_name}")
    return boto3.client('sqs', region_name=region_name)

