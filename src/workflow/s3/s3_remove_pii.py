"""
s3_remove_pii.py: Strategy for removing PII from S3 audio files using AWS Transcribe.
"""

import uuid
import time
import os
from aws_lambda_powertools import Logger
from common.models.default_strategy import DefaultStrategy
from common.utils_methods.transcribe_utils import TranscribeUtils
from common.utils_methods.s3_utils import S3Utils

logger = Logger()


class S3RemovePii(DefaultStrategy):
    """
    Strategy for removing PII from S3 audio files using AWS Transcribe.
    Event must contain 's3_bucket', 's3_key'.
    """

    def __init__(self, event: dict):
        self.event = event
        self.target_output_bucket = os.environ.get(
            "TARGET_OUTPUT_BUCKET", "new-recording-with-pii"
        )
        self.region = os.environ.get("AWS_REGION", "us-east-1")

    def do_validate(self):
        errors = []
        if not self.event.get("s3_bucket"):
            errors.append("Missing required parameter: s3_bucket")
        if not self.event.get("s3_key"):
            errors.append("Missing required parameter: s3_key")
        return (False, errors) if errors else (True, None)

    def _generate_random_id(self):
        try:
            return str(uuid.uuid4())
        except Exception as e:
            logger.exception(f"Error generating random ID: {e}")
            raise

    def _start_transcription_job(
        self, transcription_job_name, media_file_uri, target_output_bucket
    ):
        # NOTE: Not yet implemented — requires a TranscribeUtils.start_transcription_job method
        raise NotImplementedError(
            "start_transcription_job must be implemented in TranscribeUtils."
        )

    def do_operation(self):
        source_bucket = self.event.get("s3_bucket")
        source_key = self.event.get("s3_key")
        media_file_uri = f"s3://{source_bucket}/{source_key}"
        transcription_job_name = f"Transcription_Job_Name-{self._generate_random_id()}"
        try:
            transcription_start = self._start_transcription_job(
                transcription_job_name, media_file_uri, self.target_output_bucket
            )
            transcription_start_status = transcription_start["TranscriptionJob"][
                "TranscriptionJobStatus"
            ]
            if transcription_start_status in ["IN_PROGRESS", "QUEUED"]:
                time.sleep(5)
                transcribe = TranscribeUtils(self.region)
                check_status = transcribe.check_transcription_status(
                    transcription_job_name
                )
                logger.info(
                    f"Transcription job processing completed with status: {check_status}"
                )
                return {
                    "statusCode": 200,
                    "message": "Transcription job processing completed",
                    "media_file_uri": media_file_uri,
                    "Status": check_status,
                }
            elif transcription_start_status == "COMPLETED":
                logger.info(
                    f"Transcription job already completed: {transcription_start_status}"
                )
                return {
                    "statusCode": 200,
                    "message": "Transcription job processing completed",
                    "media_file_uri": media_file_uri,
                    "Status": transcription_start_status,
                }
            elif transcription_start_status == "FAILED":
                logger.error(
                    f"Transcription job failed: {transcription_start_status}"
                )
                return {
                    "statusCode": 400,
                    "message": "Transcription job processing failed",
                    "media_file_uri": media_file_uri,
                    "Status": transcription_start_status,
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
