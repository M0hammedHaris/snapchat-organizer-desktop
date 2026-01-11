"""Logging configuration for Snapchat Organizer Desktop.

This module sets up application-wide logging with file rotation and
configurable log levels.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from .config import (
    LOG_PATH,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    MAX_LOG_SIZE,
    LOG_BACKUP_COUNT,
)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[str] = None,
) -> logging.Logger:
    """Set up a logger with file and console handlers.
    
    Args:
        name: Logger name (usually __name__ of the calling module)
        log_file: Optional log file name (default: <name>.log)
        level: Optional log level (default: from config.LOG_LEVEL)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Application started")
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level
    log_level = getattr(logging, level or LOG_LEVEL)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        # Use module name as log file name
        log_file = f"{name.replace('.', '_')}.log"
    
    log_path = LOG_PATH / log_file
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=MAX_LOG_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8',
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.debug(f"Logger initialized: {name} (level={LOG_LEVEL}, file={log_path})")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get an existing logger or create a new one.
    
    This is a convenience wrapper around setup_logger for modules
    that just need a basic logger.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing file")
    """
    return setup_logger(name)


# Application-wide logger
app_logger = setup_logger("snapchat_organizer", log_file="app.log")
