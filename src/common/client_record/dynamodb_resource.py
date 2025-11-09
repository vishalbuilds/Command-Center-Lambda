import boto3
import boto3.dynamodb.conditions as dynamodb_conditions
from common.models.logger import Logger

logger = Logger(__name__)


def dynamoDB_resource(region_name: str = "us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
        dynamodb resource
    """
    logger.info(f"Initating dynamodb resource api region:{region_name}")
    return boto3.resource("dynamodb", region_name=region_name)


def dynamoDB_condition_Expression():
    """
    arg:
        N/A
    Return:
        dynamodb conditions expression
    """
    return dynamodb_conditions
