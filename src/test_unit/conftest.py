"""
Configuration file for pytest.
"""

import os
import sys
import pytest

# Add src directory to Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, src_path)

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to mock AWS environment variables."""
    monkeypatch.setenv('AWS_REGION', 'us-east-1')
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    monkeypatch.setenv('AWS_SESSION_TOKEN', 'testing')