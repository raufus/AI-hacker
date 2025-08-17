
"""
Configuration management for AI_HackerOS
"""
import os
from pathlib import Path

class Config:
    # Base paths
    PROJECT_ROOT = Path(__file__).parent.parent
    MODELS_DIR = PROJECT_ROOT / "models"
    REPORTS_DIR = PROJECT_ROOT / "reports"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # AI Model settings
    DEFAULT_MODEL_PATH = MODELS_DIR / "llama-model.gguf"
    MODEL_CONTEXT_SIZE = 4096
    MODEL_TEMPERATURE = 0.7
    
    # Security settings
    MAX_SCAN_THREADS = 10
    SCAN_DELAY = 1.0  # seconds between scans
    REQUEST_TIMEOUT = 30
    
    # Logging settings
    LOG_LEVEL = os.getenv("HACKEROS_LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Browser automation
    BROWSER_HEADLESS = True
    BROWSER_TIMEOUT = 30
    
    # Report settings
    REPORT_TEMPLATE_DIR = PROJECT_ROOT / "templates"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        for directory in [cls.MODELS_DIR, cls.REPORTS_DIR, cls.LOGS_DIR]:
            directory.mkdir(exist_ok=True)

# Global config instance
config = Config()
