import boto3
from aws_lambda_powertools import Logger


logger = Logger(child=True)


def sns_client(region_name: str = "us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
         amazon sns client
    """
    logger.info(
        f"Initating Amazon Simple Notification Service (SNS) client api with region:{region_name}"
    )
    return boto3.client("sns", region_name=region_name)
