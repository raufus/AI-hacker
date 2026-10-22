import pytest
from unittest.mock import patch, mock_open
from config.config_manager import ConfigManager

@pytest.fixture
def mock_config_manager():
    # Use patch to mock the loading so it doesn't write to disk during testing
    with patch("config.config_manager.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="{}")), \
         patch("config.config_manager.ConfigManager._save_config"):

        manager = ConfigManager("dummy_config.yaml")
        yield manager

def test_validate_config_valid(mock_config_manager):
    assert mock_config_manager.validate_config() is True

def test_validate_config_missing_section(mock_config_manager):
    # Remove a required section
    del mock_config_manager.config["system"]
    assert mock_config_manager.validate_config() is False

def test_validate_config_system_not_dict(mock_config_manager):
    mock_config_manager.config["system"] = "not a dict"
    assert mock_config_manager.validate_config() is False

def test_validate_config_network_not_dict(mock_config_manager):
    mock_config_manager.config["network"] = 123
    assert mock_config_manager.validate_config() is False

def test_validate_config_missing_max_concurrent_scans(mock_config_manager):
    del mock_config_manager.config["system"]["max_concurrent_scans"]
    assert mock_config_manager.validate_config() is False

def test_validate_config_invalid_max_concurrent_scans_type(mock_config_manager):
    # Set to a non-integer
    mock_config_manager.config["system"]["max_concurrent_scans"] = "5"
    assert mock_config_manager.validate_config() is False

def test_validate_config_missing_network_timeout(mock_config_manager):
    del mock_config_manager.config["network"]["timeout"]
    assert mock_config_manager.validate_config() is False

def test_validate_config_invalid_network_timeout_type(mock_config_manager):
    # Set to a non-integer
    mock_config_manager.config["network"]["timeout"] = "30"
    assert mock_config_manager.validate_config() is False
