"""
Logging setup.

Creates and configures loggers for the application.
"""
import logging
from pathlib import Path
from typing import Optional, Dict

# Cache loggers to avoid creating duplicates
_logger_cache: Dict[str, logging.Logger] = {}


def get_logger(
    name: str,
    log_file_path: Optional[str] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Create or get a logger with consistent settings."""
    # Return cached logger if it exists
    if name in _logger_cache:
        logger = _logger_cache[name]
        if logger.handlers:
            return logger
    
    # Create new logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Add file handler if path provided
    if log_file_path:
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Always log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Cache the logger
    _logger_cache[name] = logger
    
    return logger


def setup_ingestion_logger(log_file_path: Optional[str] = None) -> logging.Logger:
    """Get logger for ingestion module."""
    if log_file_path is None:
        from src.utils.config import Config
        config = Config()
        log_file_path = config.get_log_file_path()
    
    return get_logger('ingestion.main', log_file_path)


def setup_analytics_logger(log_file_path: Optional[str] = None) -> logging.Logger:
    """Get logger for analytics module."""
    if log_file_path is None:
        from src.utils.config import Config
        config = Config()
        log_file_path = config.get_analytics_log_path()
    
    return get_logger('analytics.main', log_file_path)

