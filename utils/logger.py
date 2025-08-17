
"""
Logging & error handling
"""
import logging
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """Set up logger with file and console handlers"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Default log file with timestamp
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/ai_hackeros_{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class SecurityLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.security_log_file = f"logs/security_events_{datetime.now().strftime('%Y%m%d')}.log"
        self._setup_security_handler()

    def _setup_security_handler(self):
        """Set up a dedicated handler for security events."""
        security_handler = logging.FileHandler(self.security_log_file)
        security_handler.setFormatter(
            logging.Formatter('%(asctime)s - SECURITY - %(message)s')
        )
        # Add this handler to the root logger to capture all security events
        logging.getLogger().addHandler(security_handler)

    def log_security_event(self, event_type: str, target: str, details: dict):
        """Log security-related events."""
        message = f"Event: {event_type} | Target: {target} | Details: {details}"
        self.logger.warning(message) # Log to the main logger
    
    def log_vulnerability_found(self, vuln_type: str, target: str, severity: str):
        """Log vulnerability discovery"""
        self.log_security_event(
            "VULNERABILITY_FOUND",
            target,
            {"type": vuln_type, "severity": severity}
        )
    
    def log_exploitation_attempt(self, target: str, method: str, success: bool):
        """Log exploitation attempts"""
        self.log_security_event(
            "EXPLOITATION_ATTEMPT",
            target,
            {"method": method, "success": success}
        )
    
    def log_access_gained(self, target: str, access_type: str):
        """Log successful access"""
        self.log_security_event(
            "ACCESS_GAINED",
            target,
            {"access_type": access_type}
        )

# Error handling decorators
def handle_errors(func):
    """Decorator for error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__module__)
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

def log_function_calls(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} returned: {result}")
        return result
    return wrapper
