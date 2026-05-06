"""
TranscribeUtils: A comprehensive utility class for AWS Transcribe operations.

This class provides high-level, descriptive methods for starting, getting, and checking transcription jobs.
All methods include logging and error handling for robust production use.
"""

import time
from aws_lambda_powertools import Logger
from common.client_record.transcribe_client import transcribe_client


logger = Logger()


class TranscribeUtils:

    def __init__(self, region_name):
        self.region_name = region_name
        self.transcribe_client = transcribe_client(region_name)

    def start_transcription_job(
        self, transcription_job_name: str, media_file_uri: str, output_bucket: str
    ):
        """
        Start an AWS Transcribe job with PII redaction enabled.
        Args:
            transcription_job_name: Unique name for the job.
            media_file_uri: S3 URI of the source audio file.
            output_bucket: S3 bucket for the redacted output.
        Returns:
            dict: The AWS Transcribe start_transcription_job response.
        Raises:
            Exception: If the API call fails.
        """
        logger.info(
            f"Starting transcription job: {transcription_job_name}",
            extra={
                "transcription_job_name": transcription_job_name,
                "media_file_uri": media_file_uri,
                "output_bucket": output_bucket,
            },
        )
        try:
            response = self.transcribe_client.start_transcription_job(
                TranscriptionJobName=transcription_job_name,
                Media={"MediaFileUri": media_file_uri},
                OutputBucketName=output_bucket,
                IdentifyLanguage=True,
                ContentRedaction={"RedactionType": "PII", "RedactionOutput": "redacted"},
            )
            logger.info(
                f"Transcription job started: {transcription_job_name}",
                extra={"transcription_job_name": transcription_job_name},
            )
            return response
        except Exception as e:
            logger.exception(
                f"Error starting transcription job {transcription_job_name}: {e}",
                extra={"transcription_job_name": transcription_job_name},
            )
            raise

    def check_transcription_status(self, transcription_job_name, max_attempts=60):
        """
        Poll the status of a transcription job until it completes or fails.
        Args:
            transcription_job_name (str): Name of the transcription job.
            max_attempts (int): Maximum polling iterations (default 60 × 5s = 5 min).
        Returns:
            str: Final status ('COMPLETED', 'FAILED', or 'UNKNOWN').
        Raises:
            TimeoutError: If the job does not finish within max_attempts.
            Exception: If the API call fails.
        """
        logger.info(
            f"Checking transcription job status for: {transcription_job_name}",
            extra={"transcription_job_name": transcription_job_name},
        )
        for _ in range(max_attempts):
            try:
                response = self.transcribe_client.get_transcription_job(
                    TranscriptionJobName=transcription_job_name
                )
            except Exception as e:
                logger.exception(
                    f"Error polling transcription job status: {e}",
                    extra={"transcription_job_name": transcription_job_name},
                )
                raise

            status = response["TranscriptionJob"]["TranscriptionJobStatus"]
            logger.info(
                f"Transcription job status: {status}", extra={"status": status}
            )

            if status == "COMPLETED":
                logger.info(
                    f"Transcription job completed",
                    extra={"transcription_job_name": transcription_job_name},
                )
                return status
            elif status in ("IN_PROGRESS", "QUEUED"):
                logger.info("Transcription job in progress, polling again...")
                time.sleep(5)
            elif status == "FAILED":
                logger.error(
                    f"Transcription job failed",
                    extra={"transcription_job_name": transcription_job_name, "status": status},
                )
                return status
            else:
                logger.error(
                    f"Transcription job returned unexpected status",
                    extra={"transcription_job_name": transcription_job_name, "status": status},
                )
                return "UNKNOWN"

        logger.error(
            f"Transcription job timed out after {max_attempts} attempts",
            extra={"transcription_job_name": transcription_job_name},
        )
        raise TimeoutError(
            f"Transcription job {transcription_job_name} did not complete after {max_attempts} attempts"
        )
