"""
Logging utility for the social media sentiment analysis application.
Provides structured logging with rotation and multiple handlers.
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from ..config import LoggingConfig, OUTPUTS_DIR

class Logger:
    """Custom logger with file and console handlers"""
    
    def __init__(self, name: str, log_file: Optional[Path] = None):
        self.name = name
        self.log_file = log_file or LoggingConfig.LOG_FILE
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, LoggingConfig.LOG_LEVEL))
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        formatter = logging.Formatter(LoggingConfig.LOG_FORMAT)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        try:
            # Ensure output directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=LoggingConfig.LOG_MAX_BYTES,
                backupCount=LoggingConfig.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not setup file handler: {e}")
        
        return logger
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        self.logger.exception(message, **kwargs)

def get_logger(name: str) -> Logger:
    """Get a configured logger instance"""
    return Logger(name)

# Global logger instance
app_logger = get_logger("app")