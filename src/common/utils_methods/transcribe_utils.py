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

    def check_transcription_status(self, transcription_job_name):
        """
        Poll the status of a transcription job until it completes or fails.
        Args:
            transcription_job_name (str): Name of the transcription job.
        Returns:
            str: Final status ('COMPLETED', 'FAILED', or 'UNKNOWN').
        Raises:
            Exception: If the operation fails.
        """
        logger.info(
            f"Checking transcription job status for: {transcription_job_name}",
            extra={"transcription_job_name": transcription_job_name},
        )
        try:
            while True:
                response = self.transcribe_client.get_transcription_job(
                    TranscriptionJobName=transcription_job_name
                )
                status = response["TranscriptionJob"]["TranscriptionJobStatus"]

                logger.info(
                    f"Transcription job status: {status}", extra={"status": status}
                )
                if status == "COMPLETED":
                    logger.info(
                        f"Transcription job completed with status: {status}",
                        extra={"status": status},
                    )
                    return status
                elif status == "IN_PROGRESS":
                    logger.info("Transcription job in progress...")
                    time.sleep(5)
                elif status == "FAILED":
                    logger.error(
                        f"Transcription job failed: {status}", extra={"status": status}
                    )
                    return status
                else:
                    logger.error(
                        f"Transcription job status not found: {response}",
                        extra={"response": response},
                    )
                    return "UNKNOWN"
        except Exception as e:
            logger.exception(
                f"Error checking transcription job status: {e}",
                extra={"transcription_job_name": transcription_job_name},
            )
            raise
