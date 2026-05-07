import os
from aws_lambda_powertools import Logger
from common.models.default_strategy import DefaultStrategy
from common.utils_methods.s3_utils import S3Utils

logger = Logger(child=True)


class S3GetFile(DefaultStrategy):
    """
    Strategy for retrieving a file from S3.
    Event must contain 'bucket' and 'key'.
    """

    def __init__(self, event: dict):
        self.event = event
        self.bucket = event.get("bucket")
        self.key = event.get("key")

    def do_validate(self):
        errors = []
        if not self.bucket:
            errors.append("Missing required parameter: bucket")
        if not self.key:
            errors.append("Missing required parameter: key")
        return (False, errors) if errors else (True, None)

    def do_operation(self):
        try:
            s3 = S3Utils(self.bucket)
            obj = s3.get_object(self.key)
            body = obj["Body"].read().decode("utf-8")
            content_type = obj.get("ContentType", "")
            logger.info(f"Successfully retrieved object from {self.bucket}/{self.key}")
            return {
                "statusCode": 200,
                "message": "Successfully retrieved object",
                "bucket": self.bucket,
                "key": self.key,
                "content_type": content_type,
                "body": body,
            }
        except Exception as e:
            logger.exception(
                f"Error retrieving object: {e}",
                extra={"bucket": self.bucket, "key": self.key},
            )
            raise
