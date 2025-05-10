import logging
import os
import sys
from typing import Optional

def setup_logging(log_file_path: Optional[str] = None, debug: bool = False) -> None:
    """Set up logging configuration for the application
    
    Args:
        log_file_path: Optional path to log file. If None, logs only go to console
        debug: Whether to enable debug level logging
    """
    # Create logs directory if it doesn't exist
    if log_file_path:
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Remove any existing handlers to prevent duplication if called multiple times
    # (though it should ideally be called once)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add console handler (explicitly to sys.stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Add file handler if log_file_path is provided
    if log_file_path:
        try:
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
            root_logger.addHandler(file_handler)
            root_logger.info(f"Logging to file: {log_file_path}")
        except Exception as e:
            root_logger.error(f"Failed to set up file logging: {e}")
    
    # Log initial configuration
    root_logger.info("Logging initialized")
    if debug:
        root_logger.debug("Debug logging enabled") 