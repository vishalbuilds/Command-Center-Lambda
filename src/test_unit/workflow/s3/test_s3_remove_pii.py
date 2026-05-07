import pytest
from unittest.mock import patch, MagicMock
from workflow.s3.s3_remove_pii import S3RemovePii


class TestS3RemovePii:

    def test_init_defaults(self):
        obj = S3RemovePii({"s3_bucket": "b", "s3_key": "k"})
        assert obj.target_output_bucket == "recordings-pii-redacted"
        assert obj.region == "us-east-1"

    def test_init_env_override(self, monkeypatch):
        monkeypatch.setenv("TARGET_OUTPUT_BUCKET", "custom-bucket")
        monkeypatch.setenv("AWS_REGION", "eu-west-1")
        obj = S3RemovePii({"s3_bucket": "b", "s3_key": "k"})
        assert obj.target_output_bucket == "custom-bucket"
        assert obj.region == "eu-west-1"

    def test_do_validate_success(self):
        obj = S3RemovePii({"s3_bucket": "b", "s3_key": "k"})
        result, errors = obj.do_validate()
        assert result is True
        assert errors == []

    def test_do_validate_missing_bucket(self):
        obj = S3RemovePii({"s3_key": "k"})
        result, errors = obj.do_validate()
        assert result is False
        assert any("s3_bucket" in e for e in errors)

    def test_do_validate_missing_key(self):
        obj = S3RemovePii({"s3_bucket": "b"})
        result, errors = obj.do_validate()
        assert result is False
        assert any("s3_key" in e for e in errors)

    def test_do_validate_missing_both(self):
        obj = S3RemovePii({})
        result, errors = obj.do_validate()
        assert result is False
        assert len(errors) == 2

    @patch("workflow.s3.s3_remove_pii.TranscribeUtils")
    def test_do_operation_completed(self, mock_transcribe_cls):
        mock_transcribe = MagicMock()
        mock_transcribe.start_transcription_job.return_value = {
            "TranscriptionJob": {"TranscriptionJobStatus": "COMPLETED"}
        }
        mock_transcribe_cls.return_value = mock_transcribe

        obj = S3RemovePii({"s3_bucket": "b", "s3_key": "k"})
        result = obj.do_operation()

        assert result["statusCode"] == 200
        assert result["Status"] == "COMPLETED"

    @patch("workflow.s3.s3_remove_pii.TranscribeUtils")
    def test_do_operation_in_progress_then_completed(self, mock_transcribe_cls):
        mock_transcribe = MagicMock()
        mock_transcribe.start_transcription_job.return_value = {
            "TranscriptionJob": {"TranscriptionJobStatus": "IN_PROGRESS"}
        }
        mock_transcribe.check_transcription_status.return_value = "COMPLETED"
        mock_transcribe_cls.return_value = mock_transcribe

        obj = S3RemovePii({"s3_bucket": "b", "s3_key": "k"})
        result = obj.do_operation()

        assert result["statusCode"] == 200
        assert result["Status"] == "COMPLETED"
        mock_transcribe.check_transcription_status.assert_called_once()

    @patch("workflow.s3.s3_remove_pii.TranscribeUtils")
    def test_do_operation_queued_then_failed(self, mock_transcribe_cls):
        mock_transcribe = MagicMock()
        mock_transcribe.start_transcription_job.return_value = {
            "TranscriptionJob": {"TranscriptionJobStatus": "QUEUED"}
        }
        mock_transcribe.check_transcription_status.return_value = "FAILED"
        mock_transcribe_cls.return_value = mock_transcribe

        obj = S3RemovePii({"s3_bucket": "b", "s3_key": "k"})
        result = obj.do_operation()

        assert result["statusCode"] == 400
        assert result["Status"] == "FAILED"

    @patch("workflow.s3.s3_remove_pii.TranscribeUtils")
    def test_do_operation_failed_immediately(self, mock_transcribe_cls):
        mock_transcribe = MagicMock()
        mock_transcribe.start_transcription_job.return_value = {
            "TranscriptionJob": {"TranscriptionJobStatus": "FAILED"}
        }
        mock_transcribe_cls.return_value = mock_transcribe

        obj = S3RemovePii({"s3_bucket": "b", "s3_key": "k"})
        result = obj.do_operation()

        assert result["statusCode"] == 400
        assert result["Status"] == "FAILED"

    @patch("workflow.s3.s3_remove_pii.TranscribeUtils")
    def test_do_operation_unknown_status(self, mock_transcribe_cls):
        mock_transcribe = MagicMock()
        mock_transcribe.start_transcription_job.return_value = {
            "TranscriptionJob": {"TranscriptionJobStatus": "SOMETHING_ELSE"}
        }
        mock_transcribe_cls.return_value = mock_transcribe

        obj = S3RemovePii({"s3_bucket": "b", "s3_key": "k"})
        result = obj.do_operation()

        assert result["statusCode"] == 400
        assert result["Status"] == "UNKNOWN"

    @patch("workflow.s3.s3_remove_pii.TranscribeUtils")
    def test_do_operation_raises_on_exception(self, mock_transcribe_cls):
        mock_transcribe = MagicMock()
        mock_transcribe.start_transcription_job.side_effect = Exception("Transcribe error")
        mock_transcribe_cls.return_value = mock_transcribe

        obj = S3RemovePii({"s3_bucket": "b", "s3_key": "k"})
        with pytest.raises(Exception, match="Transcribe error"):
            obj.do_operation()
