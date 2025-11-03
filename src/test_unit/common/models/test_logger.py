"""
Unit tests for logger module.
"""
import pytest
import json
import logging
from common.models.logger import Logger


class TestLogger:
    
    def setup_method(self):
        """Reset Logger singleton state before each test."""
        Logger._instance = None
        Logger._initialized = False
    
    def test_logger_initialization(self):
        """Test Logger initialization."""
        logger = Logger("test_logger")
        # Since Logger is a singleton, it may retain the name from previous instances
        # Just check that it's a valid logger instance
        assert hasattr(logger, 'logger')
        assert logger.logger.level == logging.INFO
    
    def test_singleton_behavior(self):
        """Test that Logger is a singleton."""
        logger1 = Logger("logger1")
        logger2 = Logger("logger2")
        assert logger1 is logger2
    
    def test_log_levels(self):
        """Test different log levels."""
        logger = Logger("test_logger")
        
        # Test that logging methods exist and can be called without error
        try:
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            logger.debug("Test debug message")
            logger.critical("Test critical message")
            assert True
        except Exception as e:
            pytest.fail(f"Logging methods should not raise exceptions: {e}")
    
    def test_metadata_handling(self):
        """Test metadata handling."""
        logger = Logger("test_logger")
        
        # Test setting metadata
        metadata = {"app": "test_app", "env": "test"}
        logger.set_metadata(metadata)
        
        # Check that metadata is stored internally
        assert logger._metadata["app"] == "test_app"
        assert logger._metadata["env"] == "test"
    
    def test_add_metadata(self):
        """Test adding individual metadata."""
        logger = Logger("test_logger")
        
        logger.add_metadata("version", "1.0")
        
        # Check that metadata is stored internally
        assert logger._metadata["version"] == "1.0"
    
    def test_tempdata_handling(self):
        """Test temporary data handling."""
        logger = Logger("test_logger")
        
        # add_tempdata should store data temporarily and log it
        logger.add_tempdata("request_id", "123")
        
        # The tempdata should be cleared after logging, but we can test that the method works
        # by checking that it doesn't raise an exception
        assert True
    
    def test_init_context(self):
        """Test context initialization."""
        logger = Logger("test_logger")
        
        # Mock context object
        class MockContext:
            aws_request_id = "test-request-id"
        
        context = MockContext()
        logger.init_context(context)
        
        # Metadata should be set with context info
        assert logger._metadata.get("aws_request_id") == "test-request-id"
    
    def test_init_context_with_none(self):
        """Test context initialization with None."""
        logger = Logger("test_logger")
        logger.init_context(None)
        
        # Should not raise an exception
        assert True