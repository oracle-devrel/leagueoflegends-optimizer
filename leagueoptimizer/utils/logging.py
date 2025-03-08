"""
Logging configuration for the League Optimizer.

This module sets up logging with proper formatters and handlers.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# Base directory for logs
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE_DIR / "logs"

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Log levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def get_logger(
    name: str, 
    level: str = "info", 
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Get a logger with the specified configuration.
    
    Args:
        name: The name of the logger
        level: The log level (debug, info, warning, error, critical)
        log_file: The path to the log file (relative to LOG_DIR)
        console: Whether to log to console
        
    Returns:
        A configured logger
    """
    # Get the log level
    log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    simple_formatter = logging.Formatter("%(levelname)s: %(message)s")
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        file_path = LOG_DIR / log_file
        file_handler = RotatingFileHandler(
            file_path, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)
    
    return logger


# Default application logger
app_logger = get_logger("leagueoptimizer", log_file="app.log")

# API logger
api_logger = get_logger("leagueoptimizer.api", log_file="api.log")

# Data logger
data_logger = get_logger("leagueoptimizer.data", log_file="data.log")

# Model logger
model_logger = get_logger("leagueoptimizer.model", log_file="model.log") 