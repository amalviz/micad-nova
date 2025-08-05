"""
Configuration settings for the test automation framework.
"""
import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseSettings, Field

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback if python-dotenv is not available
    pass

class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    url: str = Field(default="postgresql://user:password@localhost:5432/test_automation", env="DATABASE_URL")
    pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    echo: bool = Field(default=False, env="DATABASE_ECHO")

class WebConfig(BaseSettings):
    """Web testing configuration settings."""
    browser: str = Field(default="chromium", env="WEB_BROWSER")
    headless: bool = Field(default=False, env="WEB_HEADLESS")
    timeout: int = Field(default=30000, env="WEB_TIMEOUT")
    base_url: str = Field(default="https://example.com", env="WEB_BASE_URL")
    viewport_width: int = Field(default=1280, env="WEB_VIEWPORT_WIDTH")
    viewport_height: int = Field(default=720, env="WEB_VIEWPORT_HEIGHT")

class MobileConfig(BaseSettings):
    """Mobile testing configuration settings."""
    appium_server_url: str = Field(default="http://localhost:4723", env="APPIUM_SERVER_URL")
    android_app_path: Optional[str] = Field(default=None, env="ANDROID_APP_PATH")
    ios_app_path: Optional[str] = Field(default=None, env="IOS_APP_PATH")
    platform_name: str = Field(default="Android", env="MOBILE_PLATFORM_NAME")
    device_name: str = Field(default="emulator-5554", env="MOBILE_DEVICE_NAME")
    app_package: Optional[str] = Field(default=None, env="MOBILE_APP_PACKAGE")
    app_activity: Optional[str] = Field(default=None, env="MOBILE_APP_ACTIVITY")

class LoggingConfig(BaseSettings):
    """Logging configuration settings."""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    file_path: str = Field(default="logs/test.log", env="LOG_FILE")
    rotation: str = Field(default="10 MB", env="LOG_ROTATION")
    retention: str = Field(default="30 days", env="LOG_RETENTION")

class AIConfig(BaseSettings):
    """AI analysis configuration settings."""
    enabled: bool = Field(default=False, env="ENABLE_AI_ANALYSIS")
    model_name: str = Field(default="bert-base-uncased", env="AI_MODEL_NAME")
    confidence_threshold: float = Field(default=0.7, env="AI_CONFIDENCE_THRESHOLD")
    max_tokens: int = Field(default=512, env="AI_MAX_TOKENS")

class ReportConfig(BaseSettings):
    """Reporting configuration settings."""
    formats: List[str] = Field(default=["html"], env="REPORT_FORMAT")
    output_dir: str = Field(default="reports", env="REPORT_OUTPUT_DIR")
    enable_screenshots: bool = Field(default=True, env="ENABLE_SCREENSHOTS")
    enable_video_recording: bool = Field(default=False, env="ENABLE_VIDEO_RECORDING")

class GeneralConfig(BaseSettings):
    """General configuration settings."""
    parallel_workers: int = Field(default=4, env="PARALLEL_WORKERS")
    retry_failed_tests: int = Field(default=1, env="RETRY_FAILED_TESTS")
    test_timeout: int = Field(default=300, env="TEST_TIMEOUT")
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)

class Settings:
    """Main settings class combining all configuration sections."""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.web = WebConfig()
        self.mobile = MobileConfig()
        self.logging = LoggingConfig()
        self.ai = AIConfig()
        self.reporting = ReportConfig()
        self.general = GeneralConfig()
    
    def get_project_root(self) -> Path:
        """Get the project root directory."""
        return self.general.project_root
    
    def get_reports_dir(self) -> Path:
        """Get the reports directory."""
        reports_dir = self.general.project_root / self.reporting.output_dir
        reports_dir.mkdir(exist_ok=True)
        return reports_dir
    
    def get_logs_dir(self) -> Path:
        """Get the logs directory."""
        logs_dir = self.general.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings