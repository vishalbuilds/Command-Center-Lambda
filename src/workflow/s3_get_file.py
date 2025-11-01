from utils import s3_utils
from common.logger import Logger
import os
LOGGER = Logger(__name__)

class S3GetFile:
    """
    Handler for getting files from S3.
    Uses s3_utils for AWS S3 operations.
    """
    def __init__(self, event=None):
        self.event = event
        self.region_name = os.environ.get('AWS_REGION', 'us-east-1')
        self.logger = Logger(__name__)

    def handle(self, event, context):
        """
        Lambda entry point for getting files from S3.
        Args:
            event (dict): Lambda event payload.
            context: Lambda context object.
        Returns:
            dict: Lambda response with status and message.
        """
        self.logger.info('Lambda handler function for S3GetFile')
        bucket = event.get("input").get('bucket')
        key = event.get("input").get('key')
        if not bucket or not key:
            raise ValueError("Event must contain 'bucket' and 'key'")
        
        try:
            obj = s3_utils.get_object(bucket, key, self.region_name)
            self.logger.info(f"Successfully retrieved object from {bucket}/{key}")
            return {
                'statusCode': 200,
                'message': 'Successfully retrieved object',
                'object': obj
            }
        except Exception as e:
            self.logger.error(f"Error retrieving object: {e}")
            return {
                'statusCode': 500,
                'message': f"Error retrieving object: {e}"
            }