"""
TranscribeUtils: A comprehensive utility class for AWS Transcribe operations.

This class provides high-level, descriptive methods for starting, getting, and checking transcription jobs.
All methods include logging and error handling for robust production use.
"""
from common.client_record import s3_client, transcribe_client
from common.logger import Logger

logger = Logger(__name__)

def check_transcription_status(transcription_job_name,region_name):
    """
    Poll the status of a transcription job until it completes or fails.
    Args:
        transcription_job_name (str): Name of the transcription job.
    Returns:
        str: Final status ('COMPLETED', 'FAILED', or 'UNKNOWN').
    Raises:
        Exception: If the operation fails.
    """
    logger.info(f"Checking transcription job status for: {transcription_job_name}")
    try:
        while True:
            response = s3_client(region_name).get_transcription_job(transcription_job_name)
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            logger.info(f"Transcription job status: {status}")
            if status == 'COMPLETED':
                logger.info(f"Transcription job completed with status: {status}")
                return status
            elif status == 'IN_PROGRESS':
                logger.info("Transcription job in progress...")
                import time
                time.sleep(5)
            elif status == 'FAILED':
                logger.error(f"Transcription job failed: {status}")
                return status
            else:
                logger.error(f"Transcription job status not found: {response}")
                return "UNKNOWN"
    except Exception as e:
        logger.error(f"Error checking transcription job status: {e}")
        raise 