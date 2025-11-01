"""
Unit tests for transcribe_utils module.
"""
import pytest
from unittest.mock import patch, MagicMock
from utils.transcribe_utils import check_transcription_status

@patch('utils.transcribe_utils.s3_client')
def test_check_transcription_status_completed(mock_s3_client):
    mock_client = MagicMock()
    mock_s3_client.return_value = mock_client
    mock_client.get_transcription_job.return_value = {
        "TranscriptionJob": {
            "TranscriptionJobStatus": "COMPLETED"
        }
    }
    
    result = check_transcription_status("test-job", "us-east-1")
    assert result == "COMPLETED"
    mock_client.get_transcription_job.assert_called_once_with("test-job")

@patch('utils.transcribe_utils.s3_client')
def test_check_transcription_status_failed(mock_s3_client):
    mock_client = MagicMock()
    mock_s3_client.return_value = mock_client
    mock_client.get_transcription_job.return_value = {
        "TranscriptionJob": {
            "TranscriptionJobStatus": "FAILED"
        }
    }
    
    result = check_transcription_status("test-job", "us-east-1")
    assert result == "FAILED"
    mock_client.get_transcription_job.assert_called_once_with("test-job")

@patch('utils.transcribe_utils.s3_client')
def test_check_transcription_status_unknown(mock_s3_client):
    mock_client = MagicMock()
    mock_s3_client.return_value = mock_client
    mock_client.get_transcription_job.return_value = {
        "TranscriptionJob": {
            "TranscriptionJobStatus": "UNKNOWN_STATUS"
        }
    }
    
    result = check_transcription_status("test-job", "us-east-1")
    assert result == "UNKNOWN"
    mock_client.get_transcription_job.assert_called_once_with("test-job")

@patch('utils.transcribe_utils.s3_client')
def test_check_transcription_status_error(mock_s3_client):
    mock_client = MagicMock()
    mock_s3_client.return_value = mock_client
    mock_client.get_transcription_job.side_effect = Exception("Test error")
    
    with pytest.raises(Exception, match="Test error"):
        check_transcription_status("test-job", "us-east-1")