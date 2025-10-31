import boto3
from common.logger import Logger



def ses_client(region_name:str="us-east-1"):
    """
    Return a Amazon Simple Email Service client
    arg:
        region_name: AWS region name of the amazon connect (default:us-east-1 )
    """
    Logger.info(f"Initating Amazon Simple Email Service client api with region:{region_name}")
    return boto3.client('sesv2')

