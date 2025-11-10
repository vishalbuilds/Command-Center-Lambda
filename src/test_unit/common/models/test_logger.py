"""
Unit tests for logger module.
"""
import pytest
import json
import logging
import os
from unittest.mock import patch, MagicMock
from common.models.logger import Logger


class TestLogger:
    
    def setup_method(self):
        """Reset Logger singleton state before each test."""
        Logger._instance = None
        Logger._initialized = False
    
    def test_logger_initialization_first_time(self):
        """Test Logger initialization for the first time."""
        logger = Logger("test_logger")
        
        assert hasattr(logger, 'logger')
        assert logger.logger.name == "test_logger"
        assert logger.logger.level == logging.INFO
        assert logger._initialized is True
        assert isinstance(logger._metadata, dict)
        assert isinstance(logger._tempdata, dict)
    
    def test_logger_initialization_with_default_name(self):
        """Test Logger initialization with default name."""
        logger = Logger()
        
        assert logger.logger.name == "app_logger"
        assert logger._initialized is True
    
    def test_singleton_behavior(self):
        """Test that Logger is a singleton."""
        logger1 = Logger("logger1")
        logger2 = Logger("logger2")
        
        assert logger1 is logger2
        # Second initialization should not change the logger name
        assert logger1.logger.name == "logger1"
    
    def test_singleton_prevents_reinitialization(self):
        """Test that singleton prevents reinitialization."""
        logger1 = Logger("first_logger")
        initial_metadata = {"key": "value"}
        logger1.set_metadata(initial_metadata)
        
        # Try to create another instance
        logger2 = Logger("second_logger")
        
        # Should be the same instance with same metadata
        assert logger1 is logger2
        assert logger2._metadata == initial_metadata
    
    def test_debug_log(self):
        """Test debug logging."""
        logger = Logger("test_logger")
        
        try:
            logger.debug("Debug message")
            assert True
        except Exception as e:
            pytest.fail(f"Debug logging should not raise exception: {e}")
    
    def test_info_log(self):
        """Test info logging."""
        logger = Logger("test_logger")
        
        try:
            logger.info("Info message")
            assert True
        except Exception as e:
            pytest.fail(f"Info logging should not raise exception: {e}")
    
    def test_warning_log(self):
        """Test warning logging."""
        logger = Logger("test_logger")
        
        try:
            logger.warning("Warning message")
            assert True
        except Exception as e:
            pytest.fail(f"Warning logging should not raise exception: {e}")
    
    def test_error_log(self):
        """Test error logging."""
        logger = Logger("test_logger")
        
        try:
            logger.error("Error message")
            assert True
        except Exception as e:
            pytest.fail(f"Error logging should not raise exception: {e}")
    
    def test_critical_log(self):
        """Test critical logging."""
        logger = Logger("test_logger")
        
        try:
            logger.critical("Critical message")
            assert True
        except Exception as e:
            pytest.fail(f"Critical logging should not raise exception: {e}")
    
    def test_log_with_special_characters(self):
        """Test logging with special characters."""
        logger = Logger("test_logger")
        
        try:
            logger.info("Message with special chars: @#$%^&*()")
            logger.info("Message with unicode: 你好世界")
            logger.info("Message with newline\nand tab\there")
            assert True
        except Exception as e:
            pytest.fail(f"Logging with special characters should not raise exception: {e}")
    
    def test_log_with_non_string_message(self):
        """Test logging with non-string messages."""
        logger = Logger("test_logger")
        
        try:
            logger.info(123)
            logger.info({"key": "value"})
            logger.info([1, 2, 3])
            logger.info(None)
            assert True
        except Exception as e:
            pytest.fail(f"Logging with non-string should not raise exception: {e}")
    
    def test_set_metadata_with_dict(self):
        """Test setting metadata with dictionary."""
        logger = Logger("test_logger")
        
        metadata = {"app": "test_app", "env": "production", "version": "1.0"}
        logger.set_metadata(metadata)
        
        assert logger._metadata["app"] == "test_app"
        assert logger._metadata["env"] == "production"
        assert logger._metadata["version"] == "1.0"
    
    def test_set_metadata_with_none(self):
        """Test setting metadata with None."""
        logger = Logger("test_logger")
        
        # First set some metadata
        logger.set_metadata({"key": "value"})
        assert logger._metadata == {"key": "value"}
        
        # Then set to None
        logger.set_metadata(None)
        assert logger._metadata == {}
    
    def test_set_metadata_replaces_existing(self):
        """Test that set_metadata replaces existing metadata."""
        logger = Logger("test_logger")
        
        logger.set_metadata({"old_key": "old_value"})
        assert "old_key" in logger._metadata
        
        logger.set_metadata({"new_key": "new_value"})
        assert "old_key" not in logger._metadata
        assert "new_key" in logger._metadata
    
    def test_add_metadata_single_key(self):
        """Test adding single metadata key-value pair."""
        logger = Logger("test_logger")
        
        logger.add_metadata("user_id", "12345")
        assert logger._metadata["user_id"] == "12345"
    
    def test_add_metadata_multiple_keys(self):
        """Test adding multiple metadata keys."""
        logger = Logger("test_logger")
        
        logger.add_metadata("key1", "value1")
        logger.add_metadata("key2", "value2")
        logger.add_metadata("key3", "value3")
        
        assert logger._metadata["key1"] == "value1"
        assert logger._metadata["key2"] == "value2"
        assert logger._metadata["key3"] == "value3"
    
    def test_add_metadata_with_none_key(self):
        """Test adding metadata with None key."""
        logger = Logger("test_logger")
        
        initial_metadata = logger._metadata.copy()
        logger.add_metadata(None, "value")
        
        # Metadata should not change
        assert logger._metadata == initial_metadata
    
    def test_add_metadata_overwrites_existing(self):
        """Test that add_metadata overwrites existing key."""
        logger = Logger("test_logger")
        
        logger.add_metadata("key", "old_value")
        assert logger._metadata["key"] == "old_value"
        
        logger.add_metadata("key", "new_value")
        assert logger._metadata["key"] == "new_value"
    
    def test_add_metadata_with_various_types(self):
        """Test adding metadata with various value types."""
        logger = Logger("test_logger")
        
        logger.add_metadata("string", "value")
        logger.add_metadata("number", 123)
        logger.add_metadata("float", 45.67)
        logger.add_metadata("bool", True)
        logger.add_metadata("list", [1, 2, 3])
        logger.add_metadata("dict", {"nested": "value"})
        
        assert logger._metadata["string"] == "value"
        assert logger._metadata["number"] == 123
        assert logger._metadata["float"] == 45.67
        assert logger._metadata["bool"] is True
        assert logger._metadata["list"] == [1, 2, 3]
        assert logger._metadata["dict"] == {"nested": "value"}
    
    def test_add_tempdata_stores_temporarily(self):
        """Test that add_tempdata stores data temporarily."""
        logger = Logger("test_logger")
        
        # add_tempdata should log immediately and clear tempdata
        logger.add_tempdata("request_id", "temp-123")
        
        # After logging, tempdata should be cleared
        assert logger._tempdata == {}
    
    def test_add_tempdata_with_none_key(self):
        """Test add_tempdata with None key."""
        logger = Logger("test_logger")
        
        initial_tempdata = logger._tempdata.copy()
        logger.add_tempdata(None, "value")
        
        # Tempdata should be cleared after logging
        assert logger._tempdata == {}
    
    def test_add_tempdata_multiple_calls(self):
        """Test multiple add_tempdata calls."""
        logger = Logger("test_logger")
        
        logger.add_tempdata("key1", "value1")
        assert logger._tempdata == {}
        
        logger.add_tempdata("key2", "value2")
        assert logger._tempdata == {}
    
    def test_init_context_with_aws_request_id(self):
        """Test context initialization with AWS request ID."""
        logger = Logger("test_logger")
        
        class MockContext:
            aws_request_id = "test-request-id-123"
        
        context = MockContext()
        logger.init_context(context)
        
        assert logger._metadata.get("aws_request_id") == "test-request-id-123"
    
    def test_init_context_without_aws_request_id(self):
        """Test context initialization without AWS request ID."""
        logger = Logger("test_logger")
        
        class MockContext:
            pass
        
        context = MockContext()
        logger.init_context(context)
        
        assert "aws_request_id" not in logger._metadata
    
    def test_init_context_with_none(self):
        """Test context initialization with None."""
        logger = Logger("test_logger")
        
        logger.init_context(None)
        
        # Should not raise exception and metadata should be empty or contain only env vars
        assert isinstance(logger._metadata, dict)
    
    @patch.dict(os.environ, {
        'AWS_LAMBDA_FUNCTION_NAME': 'test-function',
        'AWS_REGION': 'us-east-1',
        'AWS_LAMBDA_FUNCTION_VERSION': '1'
    })
    def test_init_context_with_environment_variables(self):
        """Test context initialization with environment variables."""
        logger = Logger("test_logger")
        
        class MockContext:
            aws_request_id = "test-request-id"
        
        context = MockContext()
        logger.init_context(context)
        
        assert logger._metadata.get("aws_request_id") == "test-request-id"
        assert logger._metadata.get("function_name") == "test-function"
        assert logger._metadata.get("region") == "us-east-1"
        assert logger._metadata.get("version") == "1"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_init_context_without_environment_variables(self):
        """Test context initialization without environment variables."""
        logger = Logger("test_logger")
        
        class MockContext:
            aws_request_id = "test-request-id"
        
        context = MockContext()
        logger.init_context(context)
        
        assert logger._metadata.get("aws_request_id") == "test-request-id"
        assert "function_name" not in logger._metadata
        assert "region" not in logger._metadata
        assert "version" not in logger._metadata
    
    def test_metadata_persists_across_logs(self):
        """Test that metadata persists across multiple log calls."""
        logger = Logger("test_logger")
        
        logger.set_metadata({"persistent": "value"})
        
        logger.info("First log")
        logger.info("Second log")
        logger.error("Third log")
        
        # Metadata should still be there
        assert logger._metadata["persistent"] == "value"
    
    def test_tempdata_cleared_after_log(self):
        """Test that tempdata is cleared after logging."""
        logger = Logger("test_logger")
        
        # add_tempdata logs immediately and clears
        logger.add_tempdata("temp", "value")
        assert logger._tempdata == {}
    
    @patch('common.models.logger.inspect.currentframe')
    def test_log_with_no_frame(self, mock_frame):
        """Test logging when frame inspection fails."""
        mock_frame.return_value = None
        
        logger = Logger("test_logger")
        
        try:
            logger.info("Test message with no frame")
            assert True
        except Exception as e:
            pytest.fail(f"Logging should handle missing frame gracefully: {e}")
    
    @patch('common.models.logger.inspect.currentframe')
    def test_log_with_no_caller_frame(self, mock_frame):
        """Test logging when caller frame is missing."""
        mock_current_frame = MagicMock()
        mock_current_frame.f_back = None
        mock_frame.return_value = mock_current_frame
        
        logger = Logger("test_logger")
        
        try:
            logger.info("Test message with no caller frame")
            assert True
        except Exception as e:
            pytest.fail(f"Logging should handle missing caller frame gracefully: {e}")
    
    @patch('common.models.logger.json.dumps')
    def test_log_handles_json_serialization_error(self, mock_json_dumps):
        """Test that logging handles JSON serialization errors."""
        mock_json_dumps.side_effect = [Exception("JSON error"), '{"fallback": "log"}']
        
        logger = Logger("test_logger")
        
        try:
            logger.info("Test message")
            assert True
        except Exception as e:
            pytest.fail(f"Logging should handle JSON errors gracefully: {e}")
    
    def test_logger_level_filtering(self):
        """Test that logger respects log level filtering."""
        logger = Logger("test_logger")
        
        # Set logger to WARNING level
        logger.logger.setLevel(logging.WARNING)
        
        # These should not raise exceptions even if filtered
        try:
            logger.debug("Debug message - should be filtered")
            logger.info("Info message - should be filtered")
            logger.warning("Warning message - should log")
            logger.error("Error message - should log")
            assert True
        except Exception as e:
            pytest.fail(f"Logging with level filtering should not raise exception: {e}")
    
    def test_combined_metadata_and_tempdata(self):
        """Test logging with both metadata and tempdata."""
        logger = Logger("test_logger")
        
        logger.set_metadata({"persistent": "metadata"})
        
        try:
            logger.add_tempdata("temporary", "data")
            # Tempdata should be cleared after the log in add_tempdata
            assert logger._tempdata == {}
            assert logger._metadata["persistent"] == "metadata"
        except Exception as e:
            pytest.fail(f"Combined metadata and tempdata should work: {e}")
    
    def test_empty_message_logging(self):
        """Test logging with empty message."""
        logger = Logger("test_logger")
        
        try:
            logger.info("")
            logger.error("")
            assert True
        except Exception as e:
            pytest.fail(f"Logging empty message should not raise exception: {e}")
    
    def test_very_long_message_logging(self):
        """Test logging with very long message."""
        logger = Logger("test_logger")
        
        long_message = "A" * 10000
        
        try:
            logger.info(long_message)
            assert True
        except Exception as e:
            pytest.fail(f"Logging long message should not raise exception: {e}")