import boto3
import boto3.dynamodb
import boto3.dynamodb.conditions
from common.logger import Logger
logger = Logger(__name__)


def dynamoDB_resource(region_name:str="us-east-1"):
    """
    Return a dynamoDB table resource
    arg:
        table_name: DynamoDB table name to query (default:us-east-1 )
        region_name: AWS region name of the dynamoDB table
    """
    Logger.info(f"Initating dynamodb resource api region:{region_name}")
    return boto3.resource('dynamodb', region_name=region_name)

def dynamoDB_condition_Expression():
    return boto3.dynamodb.conditions

