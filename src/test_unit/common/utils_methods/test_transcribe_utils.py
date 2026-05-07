"""
Unit tests for transcribe_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock, call
from common.utils_methods.transcribe_utils import TranscribeUtils


class TestTranscribeUtils:

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_start_transcription_job_success(self, mock_transcribe_client):
        """Test successful start_transcription_job call."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.start_transcription_job.return_value = {
            "TranscriptionJob": {
                "TranscriptionJobName": "test-job",
                "TranscriptionJobStatus": "IN_PROGRESS",
            }
        }

        utils = TranscribeUtils('us-east-1')
        result = utils.start_transcription_job("test-job", "s3://bucket/key.mp3", "output-bucket")

        assert result["TranscriptionJob"]["TranscriptionJobName"] == "test-job"
        mock_client.start_transcription_job.assert_called_once_with(
            TranscriptionJobName="test-job",
            Media={"MediaFileUri": "s3://bucket/key.mp3"},
            OutputBucketName="output-bucket",
            IdentifyLanguage=True,
            ContentRedaction={"RedactionType": "PII", "RedactionOutput": "redacted"},
        )

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_start_transcription_job_api_error(self, mock_transcribe_client):
        """Test start_transcription_job re-raises API errors."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.start_transcription_job.side_effect = Exception("API error")

        utils = TranscribeUtils('us-east-1')
        with pytest.raises(Exception, match="API error"):
            utils.start_transcription_job("test-job", "s3://bucket/key.mp3", "output-bucket")

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_init(self, mock_transcribe_client):
        """Test TranscribeUtils initialization."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client

        utils = TranscribeUtils('us-east-1')

        assert utils.region_name == 'us-east-1'
        assert utils.transcribe_client == mock_client
        mock_transcribe_client.assert_called_once_with('us-east-1')

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_check_transcription_status_completed(self, mock_transcribe_client):
        """Test check_transcription_status with completed status."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.get_transcription_job.return_value = {
            "TranscriptionJob": {
                "TranscriptionJobStatus": "COMPLETED"
            }
        }

        utils = TranscribeUtils('us-east-1')
        result = utils.check_transcription_status("test-job")

        assert result == "COMPLETED"
        mock_client.get_transcription_job.assert_called_once_with(
            TranscriptionJobName="test-job"
        )

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_check_transcription_status_failed(self, mock_transcribe_client):
        """Test check_transcription_status with failed status."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.get_transcription_job.return_value = {
            "TranscriptionJob": {
                "TranscriptionJobStatus": "FAILED"
            }
        }

        utils = TranscribeUtils('us-east-1')
        result = utils.check_transcription_status("test-job")

        assert result == "FAILED"
        mock_client.get_transcription_job.assert_called_once_with(
            TranscriptionJobName="test-job"
        )

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_check_transcription_status_unknown(self, mock_transcribe_client):
        """Test check_transcription_status with unknown status."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.get_transcription_job.return_value = {
            "TranscriptionJob": {
                "TranscriptionJobStatus": "UNKNOWN_STATUS"
            }
        }

        utils = TranscribeUtils('us-east-1')
        result = utils.check_transcription_status("test-job")

        assert result == "UNKNOWN"
        mock_client.get_transcription_job.assert_called_once_with(
            TranscriptionJobName="test-job"
        )

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_check_transcription_status_queued_then_completed(self, mock_transcribe_client):
        """Test check_transcription_status transitions QUEUED → COMPLETED."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.get_transcription_job.side_effect = [
            {"TranscriptionJob": {"TranscriptionJobStatus": "QUEUED"}},
            {"TranscriptionJob": {"TranscriptionJobStatus": "COMPLETED"}},
        ]

        utils = TranscribeUtils('us-east-1')
        with patch('common.utils_methods.transcribe_utils.time') as mock_time:
            result = utils.check_transcription_status("test-job")

        assert result == "COMPLETED"
        assert mock_client.get_transcription_job.call_count == 2
        mock_time.sleep.assert_called_once_with(5)

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_check_transcription_status_in_progress_then_completed(self, mock_transcribe_client):
        """Test check_transcription_status transitions IN_PROGRESS → COMPLETED."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.get_transcription_job.side_effect = [
            {"TranscriptionJob": {"TranscriptionJobStatus": "IN_PROGRESS"}},
            {"TranscriptionJob": {"TranscriptionJobStatus": "COMPLETED"}},
        ]

        utils = TranscribeUtils('us-east-1')
        with patch('common.utils_methods.transcribe_utils.time') as mock_time:
            result = utils.check_transcription_status("test-job")

        assert result == "COMPLETED"
        assert mock_client.get_transcription_job.call_count == 2

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_check_transcription_status_timeout(self, mock_transcribe_client):
        """Test check_transcription_status raises TimeoutError when max_attempts exceeded."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.get_transcription_job.return_value = {
            "TranscriptionJob": {"TranscriptionJobStatus": "IN_PROGRESS"}
        }

        utils = TranscribeUtils('us-east-1')
        with patch('common.utils_methods.transcribe_utils.time'):
            with pytest.raises(TimeoutError):
                utils.check_transcription_status("test-job", max_attempts=3)

        assert mock_client.get_transcription_job.call_count == 3

    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_check_transcription_status_error(self, mock_transcribe_client):
        """Test check_transcription_status with exception."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.get_transcription_job.side_effect = Exception("Test error")

        utils = TranscribeUtils('us-east-1')
        with pytest.raises(Exception, match="Test error"):
            utils.check_transcription_status("test-job")
