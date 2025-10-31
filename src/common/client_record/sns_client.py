import boto3
from common.logger import Logger



def sns_client(region_name:str="us-east-1"):
    """
    Return a Amazon Simple Notification Service (SNS).
    arg:
        region_name: AWS region name of the amazon connect (default:us-east-1 )
    """
    Logger.info(f"Initating Amazon Simple Notification Service (SNS) client api with region:{region_name}")
    return boto3.client('sns', region_name=region_name)

