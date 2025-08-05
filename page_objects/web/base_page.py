"""
Base page object for web testing.
"""
from typing import Optional, List
from playwright.async_api import Page, Locator
from core.logger import test_logger

class BasePage:
    """Base page object with common functionality for web pages."""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = ""
    
    async def navigate_to(self, url: str = None):
        """Navigate to the page."""
        target_url = url or self.base_url
        await self.page.goto(target_url)
        test_logger.step(f"Navigated to: {target_url}")
    
    async def wait_for_page_load(self):
        """Wait for page to fully load."""
        await self.page.wait_for_load_state("networkidle")
        test_logger.step("Page fully loaded")
    
    async def get_title(self) -> str:
        """Get page title."""
        title = await self.page.title()
        test_logger.step(f"Page title: {title}")
        return title
    
    async def get_url(self) -> str:
        """Get current URL."""
        url = self.page.url
        test_logger.step(f"Current URL: {url}")
        return url
    
    async def click_element(self, locator: str, timeout: int = 30000):
        """Click an element."""
        await self.page.click(locator, timeout=timeout)
        test_logger.step(f"Clicked element: {locator}")
    
    async def type_text(self, locator: str, text: str, timeout: int = 30000):
        """Type text into an element."""
        await self.page.fill(locator, text, timeout=timeout)
        test_logger.step(f"Typed text into {locator}: {text}")
    
    async def clear_and_type(self, locator: str, text: str, timeout: int = 30000):
        """Clear and type text into an element."""
        await self.page.click(locator, timeout=timeout)
        await self.page.keyboard.press("Control+A")
        await self.page.keyboard.press("Delete")
        await self.page.fill(locator, text)
        test_logger.step(f"Cleared and typed text into {locator}: {text}")
    
    async def get_text(self, locator: str, timeout: int = 30000) -> str:
        """Get text from an element."""
        text = await self.page.text_content(locator, timeout=timeout)
        test_logger.step(f"Got text from {locator}: {text}")
        return text or ""
    
    async def get_attribute(self, locator: str, attribute: str, timeout: int = 30000) -> Optional[str]:
        """Get attribute value from an element."""
        value = await self.page.get_attribute(locator, attribute, timeout=timeout)
        test_logger.step(f"Got attribute {attribute} from {locator}: {value}")
        return value
    
    async def is_element_visible(self, locator: str, timeout: int = 5000) -> bool:
        """Check if element is visible."""
        try:
            await self.page.wait_for_selector(locator, state="visible", timeout=timeout)
            test_logger.step(f"Element is visible: {locator}")
            return True
        except:
            test_logger.step(f"Element is not visible: {locator}")
            return False
    
    async def is_element_enabled(self, locator: str) -> bool:
        """Check if element is enabled."""
        is_enabled = await self.page.is_enabled(locator)
        test_logger.step(f"Element {locator} enabled: {is_enabled}")
        return is_enabled
    
    async def wait_for_element(self, locator: str, state: str = "visible", timeout: int = 30000):
        """Wait for element to reach specified state."""
        await self.page.wait_for_selector(locator, state=state, timeout=timeout)
        test_logger.step(f"Element {locator} reached state: {state}")
    
    async def hover_element(self, locator: str, timeout: int = 30000):
        """Hover over an element."""
        await self.page.hover(locator, timeout=timeout)
        test_logger.step(f"Hovered over element: {locator}")
    
    async def select_option(self, locator: str, value: str = None, label: str = None, timeout: int = 30000):
        """Select option from dropdown."""
        if value:
            await self.page.select_option(locator, value=value, timeout=timeout)
            test_logger.step(f"Selected option by value {value} in {locator}")
        elif label:
            await self.page.select_option(locator, label=label, timeout=timeout)
            test_logger.step(f"Selected option by label {label} in {locator}")
    
    async def upload_file(self, locator: str, file_path: str, timeout: int = 30000):
        """Upload file to input element."""
        await self.page.set_input_files(locator, file_path, timeout=timeout)
        test_logger.step(f"Uploaded file {file_path} to {locator}")
    
    async def execute_javascript(self, script: str, *args):
        """Execute JavaScript code."""
        result = await self.page.evaluate(script, *args)
        test_logger.step(f"Executed JavaScript: {script}")
        return result
    
    async def scroll_to_element(self, locator: str):
        """Scroll to element."""
        await self.page.locator(locator).scroll_into_view_if_needed()
        test_logger.step(f"Scrolled to element: {locator}")
    
    async def get_elements(self, locator: str) -> List[Locator]:
        """Get multiple elements."""
        elements = self.page.locator(locator)
        count = await elements.count()
        test_logger.step(f"Found {count} elements matching: {locator}")
        return elements
    
    async def switch_to_frame(self, frame_locator: str):
        """Switch to iframe."""
        frame = self.page.frame_locator(frame_locator)
        test_logger.step(f"Switched to frame: {frame_locator}")
        return frame
    
    async def handle_alert(self, action: str = "accept", text: str = None):
        """Handle JavaScript alerts."""
        def alert_handler(dialog):
            if text:
                dialog.accept(text)
            elif action == "accept":
                dialog.accept()
            else:
                dialog.dismiss()
        
        self.page.on("dialog", alert_handler)
        test_logger.step(f"Set up alert handler: {action}")