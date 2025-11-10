"""
Unit tests for transcribe_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from common.utils_methods.transcribe_utils import TranscribeUtils


class TestTranscribeUtils:
    
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
        mock_client.get_transcription_job.assert_called_once_with("test-job")
    
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
        mock_client.get_transcription_job.assert_called_once_with("test-job")
    
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
        mock_client.get_transcription_job.assert_called_once_with("test-job")
    
    @patch('common.utils_methods.transcribe_utils.transcribe_client')
    def test_check_transcription_status_error(self, mock_transcribe_client):
        """Test check_transcription_status with exception."""
        mock_client = MagicMock()
        mock_transcribe_client.return_value = mock_client
        mock_client.get_transcription_job.side_effect = Exception("Test error")
        
        utils = TranscribeUtils('us-east-1')
        with pytest.raises(Exception, match="Test error"):
            utils.check_transcription_status("test-job")