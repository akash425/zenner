"""
Configuration management.

Reads settings from config.ini and environment variables.
"""
import configparser
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CONFIG_PATH = Path('./config.ini')


class Config:
    """
    Manages application configuration.
    
    Reads from config.ini and caches the result.
    """
    
    _instance: Optional['Config'] = None
    _config: Optional[configparser.RawConfigParser] = None
    _config_path: Optional[Path] = None
    
    def __new__(cls, config_path: Optional[Path] = None):
        """Create only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the configuration."""
        if self._config is None:
            self._config_path = config_path or DEFAULT_CONFIG_PATH
            self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self._config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self._config_path}. "
                f"Please create the configuration file."
            )
        
        self._config = configparser.RawConfigParser()
        self._config.read(self._config_path)
    
    def get_mongo_uri(self) -> str:
        """Get MongoDB connection URI from config or environment variable."""
        # Try config file first
        if self._config.has_option('mongodb', 'uri'):
            uri = self._config.get('mongodb', 'uri', fallback='').strip()
            if uri:
                return uri
        
        # Fallback to environment variable
        uri = os.getenv('MONGO_URI', '').strip()
        if uri:
            return uri
        
        raise ValueError(
            "MongoDB URI not found. Set it in config.ini [mongodb] uri "
            "or MONGO_URI environment variable"
        )
    
    def get(self, section: str, option: str, fallback: Optional[str] = None) -> str:
        """Get a configuration value."""
        return self._config.get(section, option, fallback=fallback or '').strip()
    
    def getint(self, section: str, option: str, fallback: int = 0) -> int:
        """Get a configuration value as integer."""
        try:
            return self._config.getint(section, option, fallback=fallback)
        except (ValueError, configparser.NoOptionError):
            return fallback
    
    # Convenience methods for commonly used configs (optional - you can use get() directly instead)
    def get_database_name(self) -> str:
        """Get database name."""
        return self.get('database', 'name', 'lorawan')
    
    def get_collection_name(self) -> str:
        """Get collection name."""
        return self.get('database', 'collection', 'uplinks')
    
    def get_analytics_collection_name(self) -> str:
        """Get analytics collection name."""
        return self.get('database', 'analytics_collection', 'analytics')
    
    def get_csv_file_path(self) -> str:
        """Get CSV file path."""
        csv_path = self.get('ingestion', 'csv_file_path', '')
        if not csv_path:
            raise ValueError("CSV file path not configured in config.ini [ingestion] csv_file_path")
        return csv_path
    
    def get_log_file_path(self) -> str:
        """Get log file path."""
        return self.get('ingestion', 'log_file_path', './logs/ingestion.log')
    
    def get_analytics_log_path(self) -> str:
        """Get analytics log file path."""
        return './logs/analytics.log'
    
    def get_batch_size(self) -> int:
        """Get batch size for database operations."""
        return self.getint('ingestion', 'batch_size', 1000)
    
    def get_cron_time(self) -> str:
        """Get cron schedule time."""
        return self.get('scheduler', 'cron_time', '0 0 * * *')
    
    def get_checkpoint_file_path(self) -> str:
        """Get checkpoint file path."""
        return self.get('ingestion', 'checkpoint_file_path', './data/checkpoint.json')
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

