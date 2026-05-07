import pytest
from unittest.mock import patch, MagicMock
from workflow.s3.s3_get_file import S3GetFile


class TestS3GetFile:

    def test_init(self):
        event = {"bucket": "my-bucket", "key": "my-key"}
        obj = S3GetFile(event)
        assert obj.bucket == "my-bucket"
        assert obj.key == "my-key"

    def test_do_validate_success(self):
        obj = S3GetFile({"bucket": "b", "key": "k"})
        result, errors = obj.do_validate()
        assert result is True
        assert errors is None

    def test_do_validate_missing_bucket(self):
        obj = S3GetFile({"key": "k"})
        result, errors = obj.do_validate()
        assert result is False
        assert any("bucket" in e for e in errors)

    def test_do_validate_missing_key(self):
        obj = S3GetFile({"bucket": "b"})
        result, errors = obj.do_validate()
        assert result is False
        assert any("key" in e for e in errors)

    def test_do_validate_missing_both(self):
        obj = S3GetFile({})
        result, errors = obj.do_validate()
        assert result is False
        assert len(errors) == 2

    @patch("workflow.s3.s3_get_file.S3Utils")
    def test_do_operation_success(self, mock_s3_utils):
        mock_body = MagicMock()
        mock_body.read.return_value = b"file content"
        mock_s3_utils.return_value.get_object.return_value = {
            "Body": mock_body,
            "ContentType": "text/plain",
        }

        obj = S3GetFile({"bucket": "my-bucket", "key": "my-key"})
        result = obj.do_operation()

        assert result["statusCode"] == 200
        assert result["body"] == "file content"
        assert result["bucket"] == "my-bucket"
        assert result["key"] == "my-key"
        assert result["content_type"] == "text/plain"

    @patch("workflow.s3.s3_get_file.S3Utils")
    def test_do_operation_missing_content_type(self, mock_s3_utils):
        mock_body = MagicMock()
        mock_body.read.return_value = b"data"
        mock_s3_utils.return_value.get_object.return_value = {"Body": mock_body}

        obj = S3GetFile({"bucket": "b", "key": "k"})
        result = obj.do_operation()

        assert result["statusCode"] == 200
        assert result["content_type"] == ""

    @patch("workflow.s3.s3_get_file.S3Utils")
    def test_do_operation_raises_on_exception(self, mock_s3_utils):
        mock_s3_utils.return_value.get_object.side_effect = Exception("S3 error")

        obj = S3GetFile({"bucket": "b", "key": "k"})
        with pytest.raises(Exception, match="S3 error"):
            obj.do_operation()
