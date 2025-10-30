import boto3
from common.logger import Logger



def connect_client(region_name:str="us-east-1"):
    """
    Return a amazon secretsmanager client
    arg:
        region_name: AWS region name of the amazon connect (default:us-east-1 )
    """
    Logger.info(f"Initating amazon connect client api with region:{region_name}")
    return boto3.client('secretsmanager', region_name=region_name)

