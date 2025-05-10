import logging
import os
from typing import Optional

class Logger:
    """Simple logger utility for the application"""
    
    def __init__(self, name: str, log_file_path: Optional[str] = None, debug: bool = False):
        """
        Initialize a logger with console and optional file output
        
        Args:
            name: Name of the logger
            log_file_path: Optional path to log file
            debug: Whether to enable debug level logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Add file handler if log_file_path is provided
        if log_file_path:
            try:
                # Ensure directory exists
                log_dir = os.path.dirname(log_file_path)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                    
                file_handler = logging.FileHandler(log_file_path)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                self.logger.info(f"Logging to file: {log_file_path}")
            except Exception as e:
                self.logger.error(f"Failed to set up file logging: {e}")
        
        self.logger.info("Logger initialized")
    
    def debug(self, message: str) -> None:
        """Log a debug message"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log an info message"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log a warning message"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log an error message"""
        self.logger.error(message)
    

if __name__ == "__main__":
    logger = Logger("test", "test.log", True)
    logger.info("Hello, world!")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

