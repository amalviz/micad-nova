"""
Base test classes for web and mobile testing.
"""
import pytest
from typing import Optional, Any
import uuid
import os
from core.driver_manager import DriverManager, WebDriverManager, MobileDriverManager
from core.logger import get_logger
from config.settings import get_settings
from core.test_tracker import tracker_manager

# Try to import optional dependencies
try:
    from utils.ai_analyzer import AIAnalyzer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    class AIAnalyzer:
        def __init__(self): pass
        def analyze_failure(self, *args, **kwargs): return {"analysis": "AI analysis not available"}

settings = get_settings()
logger = get_logger(__name__)

class BaseTest:
    """Base test class with common functionality."""
    
    def setup_method(self):
        """Setup method called before each test."""
        # Get or create test run ID
        self.run_id = os.getenv('TEST_RUN_ID', str(uuid.uuid4()))
        
        # Determine app type and application from test class
        self.app_type = self._get_app_type()
        self.application = self._get_application_name()
        
        # Create or get test tracker
        self.test_tracker = tracker_manager.get_tracker(self.run_id)
        if not self.test_tracker:
            self.test_tracker = tracker_manager.create_tracker(
                self.run_id, self.app_type, self.application
            )
        
        self.driver_manager = DriverManager()
        if settings.ai_analysis_enabled and AI_AVAILABLE:
            self.ai_analyzer = AIAnalyzer()
        else:
            self.ai_analyzer = None
        logger.info(f"Starting test: {self.__class__.__name__}")
    
    def teardown_method(self):
        """Teardown method called after each test."""
        if hasattr(self, 'driver_manager'):
            self.driver_manager.quit()
        # Note: Don't remove tracker here as other tests in the run might still need it
        logger.info(f"Finished test: {self.__class__.__name__}")
    
    def _get_app_type(self) -> str:
        """Determine app type from test class location."""
        module_path = self.__class__.__module__
        if 'web' in module_path:
            return 'Web'
        elif 'mobile' in module_path:
            return 'Mobile'
        return 'Web'  # Default
    
    def _get_application_name(self) -> Optional[str]:
        """Extract application name from test class or environment."""
        # Try to get from environment first
        app_name = os.getenv('TEST_APPLICATION')
        if app_name:
            return app_name
        
        # Try to extract from module path
        module_path = self.__class__.__module__
        parts = module_path.split('.')
        
        # Look for application name in path like tests.web.myapp.test_login
        if len(parts) >= 4:
            return parts[2]  # myapp
        
        return None
    
    def _get_test_description(self, method_name: str) -> Optional[str]:
        """Get test description from docstring."""
        test_method = getattr(self, method_name, None)
        if test_method and test_method.__doc__:
            return test_method.__doc__.strip()
        return None
    
    def handle_test_failure(self, excinfo):
        """Handle test failure with optional AI analysis."""
        logger.error(f"Test failed: {str(excinfo.value)}")
        
        if self.ai_analyzer and AI_AVAILABLE:
            try:
                analysis = self.ai_analyzer.analyze_failure(
                    error_message=str(excinfo.value),
                    screenshot_path=self.driver_manager.get_screenshot_path(),
                    page_source=self.driver_manager.get_page_source()
                )
                logger.info(f"AI Analysis: {analysis}")
            except Exception as e:
                logger.warning(f"AI analysis failed: {str(e)}")

class BaseWebTest(BaseTest):
    """Base class for web tests using Playwright."""
    
    def __init__(self):
        super().__init__()
        self.driver_manager = WebDriverManager()
        self.page = None
        self.current_test_name = None
    
    async def setup_method(self, method):
        """Setup web test environment."""
        super().setup_method(method)
        
        # Start test tracking
        self.current_test_name = method.__name__
        test_description = self._get_test_description(method.__name__)
        
        self.test_tracker.start_test(
            testcase_name=f"{self.__class__.__name__}.{self.current_test_name}",
            testcase_description=test_description,
            test_metadata={
                'test_class': self.__class__.__name__,
                'test_method': self.current_test_name,
                'browser': settings.web.browser if hasattr(settings, 'web') else 'unknown'
            }
        )
        
        # Start browser
        self.page = await self.driver_manager.start_browser()
        
        # Start video recording if enabled
        if settings.reporting.enable_video_recording:
            await self.driver_manager.start_video_recording()
        
        # Navigate to base URL if configured
        if settings.web.base_url:
            await self.page.goto(settings.web.base_url)
    
    async def teardown_method(self, method):
        """Cleanup web test environment."""
        test_status = 'passed'  # Default to passed
        error_message = None
        stack_trace = None
        screenshot_path = None
        video_path = None
        
        try:
            # Take screenshot on failure
            if settings.reporting.enable_screenshots:
                screenshot_path = await self.take_screenshot(f"final_{self.current_test_name}")
                self.screenshot_paths.append(screenshot_path)
            
            # Stop video recording
            if settings.reporting.enable_video_recording:
                video_path = await self.driver_manager.stop_video_recording()
            
            # Close browser
            await self.driver_manager.close()
            
        except Exception as e:
            test_logger.error(f"Error in web test teardown: {str(e)}")
            test_status = 'error'
            error_message = str(e)
        finally:
            # End test tracking
            if hasattr(self, 'test_tracker') and self.current_test_name:
                self.test_tracker.end_test(
                    test_status=test_status,
                    error_message=error_message,
                    stack_trace=stack_trace,
                    screenshot_path=screenshot_path,
                    video_path=video_path
                )
            
            super().teardown_method(method)
    
    async def take_screenshot(self, name: str = None) -> str:
        """Take screenshot of current page."""
        if not name:
            name = f"{self.test_name}_{len(self.screenshot_paths)}"
        
        screenshot_path = await self.driver_manager.take_screenshot(f"{name}.png")
        self.screenshot_paths.append(screenshot_path)
        return screenshot_path
    
    async def navigate_to(self, url: str):
        """Navigate to specific URL."""
        await self.page.goto(url)
        self.log_step(f"Navigated to: {url}")

class BaseMobileTest(BaseTest):
    """Base class for mobile tests using Appium."""
    
    def __init__(self):
        super().__init__()
        self.driver_manager = MobileDriverManager()
        self.driver = None
        self.current_test_name = None
    
    def setup_method(self, method):
        """Setup mobile test environment."""
        super().setup_method(method)
        
        # Start test tracking
        self.current_test_name = method.__name__
        test_description = self._get_test_description(method.__name__)
        
        self.test_tracker.start_test(
            testcase_name=f"{self.__class__.__name__}.{self.current_test_name}",
            testcase_description=test_description,
            test_metadata={
                'test_class': self.__class__.__name__,
                'test_method': self.current_test_name,
                'platform': settings.mobile.platform_name if hasattr(settings, 'mobile') else 'unknown',
                'device': settings.mobile.device_name if hasattr(settings, 'mobile') else 'unknown'
            }
        )
        
        # Start mobile driver
        self.driver = self.driver_manager.start_driver()
    
    def teardown_method(self, method):
        """Cleanup mobile test environment."""
        test_status = 'passed'  # Default to passed
        error_message = None
        stack_trace = None
        screenshot_path = None
        
        try:
            # Take screenshot on failure
            if settings.reporting.enable_screenshots:
                screenshot_path = self.take_screenshot(f"final_{self.current_test_name}")
                self.screenshot_paths.append(screenshot_path)
            
            # Close driver
            self.driver_manager.close()
            
        except Exception as e:
            test_logger.error(f"Error in mobile test teardown: {str(e)}")
            test_status = 'error'
            error_message = str(e)
        finally:
            # End test tracking
            if hasattr(self, 'test_tracker') and self.current_test_name:
                self.test_tracker.end_test(
                    test_status=test_status,
                    error_message=error_message,
                    stack_trace=stack_trace,
                    screenshot_path=screenshot_path
                )
            
            super().teardown_method(method)
    
    def take_screenshot(self, name: str = None) -> str:
        """Take screenshot of current screen."""
        if not name:
            name = f"{self.test_name}_{len(self.screenshot_paths)}"
        
        screenshot_path = self.driver_manager.take_screenshot(f"{name}.png")
        self.screenshot_paths.append(screenshot_path)
        return screenshot_path
    
    def install_app(self, app_path: str):
        """Install app on device."""
        self.driver.install_app(app_path)
        self.log_step(f"Installed app: {app_path}")
    
    def launch_app(self, app_id: str):
        """Launch app by bundle ID."""
        self.driver.activate_app(app_id)
        self.log_step(f"Launched app: {app_id}")