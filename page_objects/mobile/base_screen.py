"""
Base screen object for mobile testing.
"""
from typing import Optional, List, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from core.logger import test_logger

class BaseScreen:
    """Base screen object with common functionality for mobile screens."""
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
    
    def find_element(self, locator: Tuple[str, str], timeout: int = 30) -> WebElement:
        """Find element with wait."""
        wait = WebDriverWait(self.driver, timeout)
        element = wait.until(EC.presence_of_element_located(locator))
        test_logger.step(f"Found element: {locator}")
        return element
    
    def find_elements(self, locator: Tuple[str, str], timeout: int = 30) -> List[WebElement]:
        """Find multiple elements."""
        wait = WebDriverWait(self.driver, timeout)
        elements = wait.until(EC.presence_of_all_elements_located(locator))
        test_logger.step(f"Found {len(elements)} elements matching: {locator}")
        return elements
    
    def click_element(self, locator: Tuple[str, str], timeout: int = 30):
        """Click an element."""
        element = self.find_element(locator, timeout)
        element.click()
        test_logger.step(f"Clicked element: {locator}")
    
    def type_text(self, locator: Tuple[str, str], text: str, timeout: int = 30):
        """Type text into an element."""
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)
        test_logger.step(f"Typed text into {locator}: {text}")
    
    def get_text(self, locator: Tuple[str, str], timeout: int = 30) -> str:
        """Get text from an element."""
        element = self.find_element(locator, timeout)
        text = element.text
        test_logger.step(f"Got text from {locator}: {text}")
        return text
    
    def get_attribute(self, locator: Tuple[str, str], attribute: str, timeout: int = 30) -> Optional[str]:
        """Get attribute value from an element."""
        element = self.find_element(locator, timeout)
        value = element.get_attribute(attribute)
        test_logger.step(f"Got attribute {attribute} from {locator}: {value}")
        return value
    
    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """Check if element is visible."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            test_logger.step(f"Element is visible: {locator}")
            return True
        except:
            test_logger.step(f"Element is not visible: {locator}")
            return False
    
    def is_element_enabled(self, locator: Tuple[str, str], timeout: int = 30) -> bool:
        """Check if element is enabled."""
        element = self.find_element(locator, timeout)
        is_enabled = element.is_enabled()
        test_logger.step(f"Element {locator} enabled: {is_enabled}")
        return is_enabled
    
    def wait_for_element(self, locator: Tuple[str, str], condition: str = "visible", timeout: int = 30):
        """Wait for element with specific condition."""
        wait = WebDriverWait(self.driver, timeout)
        
        if condition == "visible":
            wait.until(EC.visibility_of_element_located(locator))
        elif condition == "clickable":
            wait.until(EC.element_to_be_clickable(locator))
        elif condition == "present":
            wait.until(EC.presence_of_element_located(locator))
        
        test_logger.step(f"Element {locator} reached condition: {condition}")
    
    def tap_element(self, locator: Tuple[str, str], timeout: int = 30):
        """Tap an element using TouchAction."""
        element = self.find_element(locator, timeout)
        TouchAction(self.driver).tap(element).perform()
        test_logger.step(f"Tapped element: {locator}")
    
    def long_press_element(self, locator: Tuple[str, str], duration: int = 1000, timeout: int = 30):
        """Long press an element."""
        element = self.find_element(locator, timeout)
        TouchAction(self.driver).long_press(element, duration=duration).release().perform()
        test_logger.step(f"Long pressed element {locator} for {duration}ms")
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000):
        """Swipe from one point to another."""
        TouchAction(self.driver).press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
        test_logger.step(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    
    def swipe_element(self, locator: Tuple[str, str], direction: str, distance: int = 200, timeout: int = 30):
        """Swipe an element in specified direction."""
        element = self.find_element(locator, timeout)
        location = element.location
        size = element.size
        
        center_x = location['x'] + size['width'] // 2
        center_y = location['y'] + size['height'] // 2
        
        if direction.lower() == "up":
            end_y = center_y - distance
            self.swipe(center_x, center_y, center_x, end_y)
        elif direction.lower() == "down":
            end_y = center_y + distance
            self.swipe(center_x, center_y, center_x, end_y)
        elif direction.lower() == "left":
            end_x = center_x - distance
            self.swipe(center_x, center_y, end_x, center_y)
        elif direction.lower() == "right":
            end_x = center_x + distance
            self.swipe(center_x, center_y, end_x, center_y)
        
        test_logger.step(f"Swiped element {locator} {direction}")
    
    def scroll_to_element(self, locator: Tuple[str, str], max_scrolls: int = 10):
        """Scroll until element is visible."""
        for i in range(max_scrolls):
            if self.is_element_visible(locator, timeout=2):
                test_logger.step(f"Found element after {i} scrolls: {locator}")
                return True
            
            # Scroll down
            self.scroll_down()
        
        test_logger.step(f"Element not found after {max_scrolls} scrolls: {locator}")
        return False
    
    def scroll_up(self, distance: int = 500):
        """Scroll up on the screen."""
        size = self.driver.get_window_size()
        start_y = size['height'] // 2
        end_y = start_y - distance
        center_x = size['width'] // 2
        
        self.swipe(center_x, start_y, center_x, end_y)
        test_logger.step("Scrolled up")
    
    def scroll_down(self, distance: int = 500):
        """Scroll down on the screen."""
        size = self.driver.get_window_size()
        start_y = size['height'] // 2
        end_y = start_y + distance
        center_x = size['width'] // 2
        
        self.swipe(center_x, start_y, center_x, end_y)
        test_logger.step("Scrolled down")
    
    def pinch_zoom(self, locator: Tuple[str, str] = None, scale: float = 0.5, timeout: int = 30):
        """Perform pinch zoom gesture."""
        if locator:
            element = self.find_element(locator, timeout)
            location = element.location
            size = element.size
            center_x = location['x'] + size['width'] // 2
            center_y = location['y'] + size['height'] // 2
        else:
            size = self.driver.get_window_size()
            center_x = size['width'] // 2
            center_y = size['height'] // 2
        
        # Create two touch actions for pinch
        action1 = TouchAction(self.driver)
        action2 = TouchAction(self.driver)
        
        offset = int(100 * scale)
        
        action1.press(x=center_x - offset, y=center_y - offset).move_to(x=center_x - 50, y=center_y - 50).release()
        action2.press(x=center_x + offset, y=center_y + offset).move_to(x=center_x + 50, y=center_y + 50).release()
        
        multi_action = MultiAction(self.driver)
        multi_action.add(action1, action2)
        multi_action.perform()
        
        test_logger.step(f"Performed pinch zoom with scale: {scale}")
    
    def hide_keyboard(self):
        """Hide the keyboard if visible."""
        try:
            self.driver.hide_keyboard()
            test_logger.step("Keyboard hidden")
        except:
            test_logger.step("Keyboard not visible or failed to hide")
    
    def rotate_device(self, orientation: str):
        """Rotate device to specified orientation."""
        if orientation.lower() == "landscape":
            self.driver.orientation = "LANDSCAPE"
        elif orientation.lower() == "portrait":
            self.driver.orientation = "PORTRAIT"
        
        test_logger.step(f"Device rotated to: {orientation}")
    
    def get_device_orientation(self) -> str:
        """Get current device orientation."""
        orientation = self.driver.orientation
        test_logger.step(f"Current orientation: {orientation}")
        return orientation