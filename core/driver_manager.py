"""
Driver management for web and mobile automation.
"""

import asyncio
from typing import Optional, Dict, Any, Union
from config.settings import get_settings
from core.logger import get_logger

# Try to import web automation libraries
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Create mock classes for type hints
    class Browser: pass
    class BrowserContext: pass
    class Page: pass

# Try to import mobile automation libraries
try:
    from appium import webdriver as appium_webdriver
    from appium.options.android import UiAutomator2Options
    from appium.options.ios import XCUITestOptions
    APPIUM_AVAILABLE = True
except ImportError:
    APPIUM_AVAILABLE = False

settings = get_settings()
logger = get_logger(__name__)

class WebDriverManager:
    """Manager for web browser instances using Playwright."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def start_browser(self, **kwargs) -> Page:
        """Start browser and return page instance."""
        try:
            self.playwright = await async_playwright().start()
            
            # Select browser type
            browser_type = getattr(self.playwright, settings.web.browser)
            
            # Launch browser
            self.browser = await browser_type.launch(
                headless=settings.web.headless,
                **kwargs
            )
            
            # Create context
            self.context = await self.browser.new_context(
                viewport={
                    'width': settings.web.viewport_width,
                    'height': settings.web.viewport_height
                }
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(settings.web.timeout)
            
            test_logger.info(f"Browser started: {settings.web.browser}")
            return self.page
            
        except Exception as e:
            test_logger.error(f"Failed to start browser: {str(e)}")
            raise
    
    async def get_web_driver(self, browser_type: str = "chromium") -> Page:
        """Get a web driver instance using Playwright."""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not available in this environment")
            
        if not self.playwright:
            self.playwright = await async_playwright().start()
            
        # Validate browser type
        if browser_type not in ["chromium", "firefox", "webkit"]:
            logger.warning(f"Unsupported browser type: {browser_type}, defaulting to chromium")
            browser_type = "chromium"
            
        browser = await getattr(self.playwright, browser_type).launch(
            headless=settings.web_headless
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        self.web_drivers.append((browser, context, page))
        
        logger.info(f"Created {browser_type} web driver")
        return page
    
    async def take_screenshot(self, path: str = None) -> str:
        """Take screenshot of current page."""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        if not path:
            timestamp = str(int(asyncio.get_event_loop().time() * 1000))
            path = f"screenshots/screenshot_{timestamp}.png"
        
        screenshot_path = settings.get_reports_dir() / path
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        await self.page.screenshot(path=str(screenshot_path))
        test_logger.screenshot_taken(str(screenshot_path))
        return str(screenshot_path)
    
    async def start_video_recording(self):
        """Start video recording."""
        if not self.context:
            raise RuntimeError("Browser context not available")
        
        video_dir = settings.get_reports_dir() / "videos"
        video_dir.mkdir(parents=True, exist_ok=True)
        
        # Enable video recording
        await self.context.close()
        self.context = await self.browser.new_context(
            viewport={
                'width': settings.web.viewport_width,
                'height': settings.web.viewport_height
            },
            record_video_dir=str(video_dir)
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(settings.web.timeout)
    
    async def stop_video_recording(self) -> Optional[str]:
        """Stop video recording and return path."""
        if not self.page:
            return None
        
        video_path = await self.page.video.path() if self.page.video else None
        if video_path:
            test_logger.video_recorded(video_path)
        return video_path
    
    async def close(self):
        """Close browser and cleanup."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            test_logger.info("Browser closed successfully")
            
        except Exception as e:
            test_logger.error(f"Error closing browser: {str(e)}")

class MobileDriverManager:
    """Manager for mobile app instances using Appium."""
    
    def __init__(self):
        self.driver: Optional[WebDriver] = None
    
    def start_driver(self, **kwargs) -> WebDriver:
        """Start mobile driver and return instance."""
        try:
            platform = settings.mobile.platform_name.lower()
            
            if platform == "android":
                return self._start_android_driver(**kwargs)
            elif platform == "ios":
                return self._start_ios_driver(**kwargs)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
                
        except Exception as e:
            test_logger.error(f"Failed to start mobile driver: {str(e)}")
            raise
    
    def get_mobile_driver(self, platform: str = "android") -> Any:
        """Get a mobile driver instance using Appium."""
        if not APPIUM_AVAILABLE:
            raise ImportError("Appium is not available in this environment")
            
        platform = platform.lower()
        
        if platform == "android":
            options = UiAutomator2Options()
            options.platform_name = settings.mobile_platform_name
            options.device_name = settings.mobile_device_name
        elif platform == "ios":
            options = XCUITestOptions()
            options.platform_name = settings.mobile_platform_name
            options.device_name = settings.mobile_device_name
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        driver = appium_webdriver.Remote(settings.mobile_server_url, options=options)
        self.mobile_drivers.append(driver)
        
        logger.info(f"Created {platform} mobile driver")
        return driver
    
    def _start_android_driver(self, **kwargs) -> WebDriver:
        """Start Android driver."""
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = settings.mobile.device_name
        
        if settings.mobile.android_app_path:
            options.app = settings.mobile.android_app_path
        
        if settings.mobile.app_package:
            options.app_package = settings.mobile.app_package
        
        if settings.mobile.app_activity:
            options.app_activity = settings.mobile.app_activity
        
        # Add custom capabilities
        for key, value in kwargs.items():
            setattr(options, key, value)
        
        self.driver = appium_webdriver(
            settings.mobile.appium_server_url,
            options=options
        )
        
        test_logger.info(f"Android driver started: {settings.mobile.device_name}")
        return self.driver
    
    def _start_ios_driver(self, **kwargs) -> WebDriver:
        """Start iOS driver."""
        options = XCUITestOptions()
        options.platform_name = "iOS"
        options.device_name = settings.mobile.device_name
        
        if settings.mobile.ios_app_path:
            options.app = settings.mobile.ios_app_path
        
        # Add custom capabilities
        for key, value in kwargs.items():
            setattr(options, key, value)
        
        self.driver = appium_webdriver(
            settings.mobile.appium_server_url,
            options=options
        )
        
        test_logger.info(f"iOS driver started: {settings.mobile.device_name}")
        return self.driver
    
    def take_screenshot(self, path: str = None) -> str:
        """Take screenshot of current screen."""
        if not self.driver:
            raise RuntimeError("Mobile driver not started")
        
        if not path:
            timestamp = str(int(asyncio.get_event_loop().time() * 1000))
            path = f"screenshots/mobile_screenshot_{timestamp}.png"
        
        screenshot_path = settings.get_reports_dir() / path
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.driver.save_screenshot(str(screenshot_path))
        test_logger.screenshot_taken(str(screenshot_path))
        return str(screenshot_path)
    
    def close(self):
        """Close mobile driver."""
        try:
            if self.driver:
                self.driver.quit()
                test_logger.info("Mobile driver closed successfully")
        except Exception as e:
            test_logger.error(f"Error closing mobile driver: {str(e)}")