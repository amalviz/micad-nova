"""
Logging configuration and utilities for the test automation framework.
"""
import sys
from pathlib import Path
from loguru import logger
from config.settings import settings

class TestLogger:
    """Enhanced logger for test automation framework."""
    
    def __init__(self):
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure the logger with appropriate settings."""
        # Remove default handler
        logger.remove()
        
        # Console handler
        logger.add(
            sys.stdout,
            format=self._get_console_format(),
            level=settings.logging.level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # File handler
        log_file = settings.get_logs_dir() / settings.logging.file_path.split('/')[-1]
        logger.add(
            log_file,
            format=self._get_file_format(),
            level=settings.logging.level,
            rotation=settings.logging.rotation,
            retention=settings.logging.retention,
            compression="zip",
            backtrace=True,
            diagnose=True
        )
    
    def _get_console_format(self) -> str:
        """Get console log format."""
        if settings.logging.format == "json":
            return "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
        return "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    
    def _get_file_format(self) -> str:
        """Get file log format."""
        return "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        logger.critical(message, **kwargs)
    
    def test_start(self, test_name: str, test_class: str = None):
        """Log test start."""
        test_identifier = f"{test_class}::{test_name}" if test_class else test_name
        logger.info(f"🚀 Starting test: {test_identifier}")
    
    def test_pass(self, test_name: str, duration: float = None):
        """Log test pass."""
        duration_str = f" (Duration: {duration:.2f}s)" if duration else ""
        logger.info(f"✅ Test passed: {test_name}{duration_str}")
    
    def test_fail(self, test_name: str, error_message: str = None, duration: float = None):
        """Log test failure."""
        duration_str = f" (Duration: {duration:.2f}s)" if duration else ""
        logger.error(f"❌ Test failed: {test_name}{duration_str}")
        if error_message:
            logger.error(f"Error: {error_message}")
    
    def test_skip(self, test_name: str, reason: str = None):
        """Log test skip."""
        reason_str = f" - Reason: {reason}" if reason else ""
        logger.warning(f"⏭️  Test skipped: {test_name}{reason_str}")
    
    def step(self, step_description: str):
        """Log test step."""
        logger.info(f"📋 Step: {step_description}")
    
    def screenshot_taken(self, screenshot_path: str):
        """Log screenshot capture."""
        logger.info(f"📸 Screenshot saved: {screenshot_path}")
    
    def video_recorded(self, video_path: str):
        """Log video recording."""
        logger.info(f"🎥 Video recorded: {video_path}")
    
    def ai_analysis(self, analysis_result: dict):
        """Log AI analysis result."""
        logger.info(f"🤖 AI Analysis: {analysis_result}")

# Global logger instance
test_logger = TestLogger()
def get_logger(name: str = __name__) -> TestLogger:
    """Get logger instance for compatibility."""
    return test_logger