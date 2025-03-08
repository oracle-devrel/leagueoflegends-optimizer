"""
Tests for the configuration module.
"""
import os
from unittest import mock

import pytest

from leagueoptimizer.config.settings import (
    _update_config,
    get_config,
    get_env_config,
    load_config_file,
)


def test_update_config():
    """Test the _update_config function."""
    # Test with simple dictionaries
    config = {"a": 1, "b": 2}
    updates = {"b": 3, "c": 4}
    _update_config(config, updates)
    assert config == {"a": 1, "b": 3, "c": 4}

    # Test with nested dictionaries
    config = {"a": 1, "b": {"c": 2, "d": 3}}
    updates = {"b": {"d": 4, "e": 5}}
    _update_config(config, updates)
    assert config == {"a": 1, "b": {"c": 2, "d": 4, "e": 5}}


def test_load_config_file():
    """Test the load_config_file function."""
    # Test with non-existent file
    with mock.patch("os.path.exists", return_value=False):
        config = load_config_file("non_existent_file.yaml")
        assert "riot_api" in config
        assert "database" in config
        assert "message_queue" in config

    # Test with existing file
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch("builtins.open", mock.mock_open(read_data="""
riot_api:
  key: test_key
database:
  type: sqlite
""")):
            config = load_config_file("test_file.yaml")
            assert config["riot_api"]["key"] == "test_key"
            assert config["database"]["type"] == "sqlite"


def test_get_env_config():
    """Test the get_env_config function."""
    # Test with environment variables
    with mock.patch.dict(os.environ, {
        "RIOT_API_KEY": "env_key",
        "DB_TYPE": "sqlite",
        "MQ_HOST": "localhost",
    }):
        config = get_env_config()
        assert config["riot_api"]["key"] == "env_key"
        assert config["database"]["type"] == "sqlite"
        assert config["message_queue"]["host"] == "localhost"


def test_get_config():
    """Test the get_config function."""
    # Test with environment variables
    with mock.patch("leagueoptimizer.config.settings.load_config_file", return_value={
        "riot_api": {"key": "file_key"},
        "database": {"type": "oracle"},
    }):
        with mock.patch("leagueoptimizer.config.settings.get_env_config", return_value={
            "riot_api": {"key": "env_key"},
            "database": {"type": "sqlite"},
        }):
            config = get_config()
            assert config["riot_api"]["key"] == "env_key"  # Environment variable takes precedence
            assert config["database"]["type"] == "sqlite"  # Environment variable takes precedence
            assert "message_queue" in config  # Default values are included 