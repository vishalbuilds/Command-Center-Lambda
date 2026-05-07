import boto3
from aws_lambda_powertools import Logger


logger = Logger(child=True)


def s3_client():
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
        s3 client
    """
    logger.info(f"Initating s3 client api")
    return boto3.client("s3")
