"""
Unit tests for logger module.
"""
import pytest
import json
import logging
from common.logger import Logger

@pytest.fixture
def logger():
    return Logger("test_logger")

def test_logger_initialization(logger):
    assert logger.logger.name == "test_logger"
    assert logger.logger.level == logging.WARNING

def test_log_levels(logger, caplog):
    with caplog.at_level(logging.INFO):
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        for record in caplog.records:
            log_data = json.loads(record.message)
            assert "level" in log_data
            assert "message" in log_data
            assert "timestamp" in log_data
            assert "function" in log_data
            assert "path" in log_data
            assert "line" in log_data

def test_redact_sensitive_info(logger, caplog):
    with caplog.at_level(logging.INFO):
        logger.info("Password: secret123, API Key: abc123")
        
        for record in caplog.records:
            log_data = json.loads(record.message)
            assert "secret123" not in log_data["message"]
            assert "abc123" not in log_data["message"]
            assert "[REDACTED]" in log_data["message"]

def test_metadata_handling(logger):
    logger.set_metadata({"app": "test_app", "env": "test"})
    test_metadata = logger.get_metadata()
    
    assert test_metadata["app"] == "test_app"
    assert test_metadata["env"] == "test"
    
    logger.add_metadata("version", "1.0")
    assert logger.get_metadata()["version"] == "1.0"
    
    logger.delete_metadata("app")
    assert "app" not in logger.get_metadata()

def test_tempdata_handling(logger):
    logger.add_tempdata("request_id", "123")
    assert logger.get_tempdata()["request_id"] == "123"

def test_silence_noisy_libs(logger):
    noisy_libs = logger.noisy_libs()
    assert isinstance(noisy_libs, list)
    assert len(noisy_libs) > 0
    
    logger.silence_noisy_libs()
    for lib in noisy_libs:
        assert logging.getLogger(lib).level == logging.WARNING

def test_set_level(logger):
    logger.set_level("DEBUG")
    assert logger.logger.level == logging.DEBUG
    
    logger.set_level("INFO")
    assert logger.logger.level == logging.INFO
    
    logger.set_level("INVALID")  # Should default to WARNING
    assert logger.logger.level == logging.WARNING