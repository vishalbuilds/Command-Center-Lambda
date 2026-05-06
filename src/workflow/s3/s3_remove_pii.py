"""
s3_remove_pii.py: Strategy for removing PII from S3 audio files using AWS Transcribe.
"""

import uuid
import os
from aws_lambda_powertools import Logger
from common.models.default_strategy import DefaultStrategy
from common.utils_methods.transcribe_utils import TranscribeUtils

logger = Logger()


class S3RemovePii(DefaultStrategy):
    """
    Strategy for removing PII from S3 audio files using AWS Transcribe.
    Event must contain 's3_bucket', 's3_key'.
    """

    def __init__(self, event: dict):
        self.event = event
        self.target_output_bucket = os.environ.get(
            "TARGET_OUTPUT_BUCKET", "recordings-pii-redacted"
        )
        self.region = os.environ.get("AWS_REGION", "us-east-1")

    def do_validate(self):
        errors = []
        if not self.event.get("s3_bucket"):
            errors.append("Missing required parameter: s3_bucket")
        if not self.event.get("s3_key"):
            errors.append("Missing required parameter: s3_key")
        return (False, errors) if errors else (True, [])

    def do_operation(self):
        source_bucket = self.event["s3_bucket"]
        source_key = self.event["s3_key"]
        media_file_uri = f"s3://{source_bucket}/{source_key}"
        transcription_job_name = f"Transcription_Job_Name-{uuid.uuid4()}"
        transcribe = TranscribeUtils(self.region)

        try:
            transcription_start = transcribe.start_transcription_job(
                transcription_job_name, media_file_uri, self.target_output_bucket
            )
            status = transcription_start["TranscriptionJob"]["TranscriptionJobStatus"]

            if status in ("IN_PROGRESS", "QUEUED"):
                status = transcribe.check_transcription_status(transcription_job_name)
                logger.info(
                    f"Transcription job processing completed with status: {status}"
                )

            if status == "COMPLETED":
                return {
                    "statusCode": 200,
                    "message": "Transcription job processing completed",
                    "media_file_uri": media_file_uri,
                    "Status": status,
                }
            elif status == "FAILED":
                logger.error(f"Transcription job failed: {status}")
                return {
                    "statusCode": 400,
                    "message": "Transcription job processing failed",
                    "media_file_uri": media_file_uri,
                    "Status": status,
                }
            else:
                logger.error("Transcription job unknown status")
                return {
                    "statusCode": 400,
                    "message": "Transcription job processing not found",
                    "media_file_uri": media_file_uri,
                    "Status": "UNKNOWN",
                }
        except Exception as e:
            logger.exception(
                f"Error processing file {media_file_uri}: {e}",
                extra={"media_file_uri": media_file_uri},
            )
            raise
