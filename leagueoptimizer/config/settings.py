"""
Configuration management for the League Optimizer.

This module handles loading configuration from environment variables,
config files, and provides default values.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"

# Default configuration
DEFAULT_CONFIG = {
    "riot_api": {
        "key": None,
        "regions": [
            "br1", "eun1", "euw1", "jp1", "kr", 
            "la1", "la2", "na1", "oc1", "ru", "tr1"
        ],
        "request_limit_per_minute": 1000,
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
        }
    },
    "database": {
        "type": "oracle",  # oracle, sqlite, postgres
        "username": None,
        "password": None,
        "dsn": None,
        "sqlite_path": str(BASE_DIR / "data" / "league.db"),
    },
    "message_queue": {
        "host": "localhost",
        "port": 5672,
        "username": "league",
        "password": "league",
        "queue_name": "live_client",
        "heartbeat": 600,
        "blocked_connection_timeout": 300,
    },
    "live_client": {
        "base_url": "https://127.0.0.1:2999/liveclientdata",
        "request_interval": 30,  # seconds
    },
    "model": {
        "save_path": str(BASE_DIR / "models" / "trained"),
    }
}


def load_config_file(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", str(BASE_DIR / "config.yaml"))
    
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            file_config = yaml.safe_load(f)
            if file_config:
                # Recursively update the config
                _update_config(config, file_config)
    
    return config


def _update_config(config: Dict[str, Any], updates: Dict[str, Any]) -> None:
    """Recursively update a nested dictionary."""
    for key, value in updates.items():
        if isinstance(value, dict) and key in config and isinstance(config[key], dict):
            _update_config(config[key], value)
        else:
            config[key] = value


def get_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    config = DEFAULT_CONFIG.copy()
    
    # Riot API settings
    if riot_api_key := os.getenv("RIOT_API_KEY"):
        config["riot_api"]["key"] = riot_api_key
    
    # Database settings
    if db_username := os.getenv("DB_USERNAME"):
        config["database"]["username"] = db_username
    if db_password := os.getenv("DB_PASSWORD"):
        config["database"]["password"] = db_password
    if db_dsn := os.getenv("DB_DSN"):
        config["database"]["dsn"] = db_dsn
    if db_type := os.getenv("DB_TYPE"):
        config["database"]["type"] = db_type
    
    # Message queue settings
    if mq_host := os.getenv("MQ_HOST"):
        config["message_queue"]["host"] = mq_host
    if mq_port := os.getenv("MQ_PORT"):
        config["message_queue"]["port"] = int(mq_port)
    if mq_username := os.getenv("MQ_USERNAME"):
        config["message_queue"]["username"] = mq_username
    if mq_password := os.getenv("MQ_PASSWORD"):
        config["message_queue"]["password"] = mq_password
    
    # Model settings
    if model_path := os.getenv("MODEL_SAVE_PATH"):
        config["model"]["save_path"] = model_path
    
    return config


def get_config() -> Dict[str, Any]:
    """
    Get the application configuration.
    
    Loads configuration from:
    1. Default values
    2. Config file (config.yaml)
    3. Environment variables (highest priority)
    """
    # Start with file config (which includes defaults)
    config = load_config_file()
    
    # Update with environment variables
    env_config = get_env_config()
    _update_config(config, env_config)
    
    # Add API headers with token
    if config["riot_api"]["key"]:
        config["riot_api"]["headers"]["X-Riot-Token"] = config["riot_api"]["key"]
    
    return config


# Singleton config instance
CONFIG = get_config() 