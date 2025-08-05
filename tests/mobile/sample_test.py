"""
Sample mobile test using the framework.
"""
import pytest
import traceback
from selenium.webdriver.common.by import By
from core.base_test import BaseMobileTest
from page_objects.mobile.base_screen import BaseScreen
from core.logger import test_logger

class LoginScreen(BaseScreen):
    """Sample login screen object."""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.email_input = (By.ID, "email")
        self.password_input = (By.ID, "password")
        self.login_button = (By.ID, "login_button")
        self.error_message = (By.ID, "error_message")
        self.dashboard_title = (By.XPATH, "//android.widget.TextView[@text='Dashboard']")
    
    def login(self, email: str, password: str):
        """Perform login action."""
        self.type_text(self.email_input, email)
        self.type_text(self.password_input, password)
        self.tap_element(self.login_button)
        test_logger.step(f"Attempted login with email: {email}")
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        return self.is_element_visible(self.dashboard_title, timeout=10)
    
    def get_error_message(self) -> str:
        """Get login error message."""
        if self.is_element_visible(self.error_message, timeout=5):
            return self.get_text(self.error_message)
        return ""

class HomeScreen(BaseScreen):
    """Sample home screen object."""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.menu_button = (By.ID, "menu_button")
        self.search_button = (By.ID, "search_button")
        self.profile_button = (By.ID, "profile_button")
        self.notification_icon = (By.ID, "notifications")
    
    def open_menu(self):
        """Open navigation menu."""
        self.tap_element(self.menu_button)
        test_logger.step("Opened navigation menu")
    
    def search(self, query: str):
        """Perform search."""
        self.tap_element(self.search_button)
        search_input = (By.ID, "search_input")
        self.wait_for_element(search_input)
        self.type_text(search_input, query)
        
        search_submit = (By.ID, "search_submit")
        self.tap_element(search_submit)
        test_logger.step(f"Searched for: {query}")

class TestMobileLogin(BaseMobileTest):
    """Sample mobile login tests."""
    
    def test_valid_login(self):
        """Test successful login with valid user credentials."""
        try:
            login_screen = LoginScreen(self.driver)
            
            login_screen.login("user@example.com", "password123")
            
            # Take screenshot for documentation
            screenshot_path = self.take_screenshot("login_attempt")
            if hasattr(self, 'test_tracker'):
                self.test_tracker.add_screenshot(screenshot_path)
            
            # Verify login success
            assert login_screen.is_logged_in(), "Login should be successful"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    def test_invalid_credentials(self):
        """Test login attempt with invalid user credentials."""
        try:
            login_screen = LoginScreen(self.driver)
            
            login_screen.login("invalid@example.com", "wrongpassword")
            
            # Verify error message appears
            error_message = login_screen.get_error_message()
            assert "Invalid credentials" in error_message, "Should show invalid credentials error"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    def test_empty_fields(self):
        """Test login attempt with empty email and password fields."""
        try:
            login_screen = LoginScreen(self.driver)
            
            login_screen.login("", "")
            
            # Verify error message appears
            error_message = login_screen.get_error_message()
            assert "Email and password are required" in error_message, "Should show required fields error"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise

class TestMobileNavigation(BaseMobileTest):
    """Sample mobile navigation tests."""
    
    def test_menu_navigation(self):
        """Test that navigation menu opens and contains expected items."""
        try:
            # Login first
            login_screen = LoginScreen(self.driver)
            login_screen.login("user@example.com", "password123")
            
            # Navigate to home screen
            home_screen = HomeScreen(self.driver)
            home_screen.open_menu()
            
            # Test menu items
            menu_items = self.driver.find_elements(By.CLASS_NAME, "menu-item")
            assert len(menu_items) > 0, "Menu should contain navigation items"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    def test_search_functionality(self):
        """Test search functionality returns appropriate results."""
        try:
            # Login first
            login_screen = LoginScreen(self.driver)
            login_screen.login("user@example.com", "password123")
            
            # Perform search
            home_screen = HomeScreen(self.driver)
            home_screen.search("test query")
            
            # Verify search results appear
            search_results = (By.ID, "search_results")
            home_screen.wait_for_element(search_results)
            
            results = home_screen.find_elements(search_results)
            assert len(results) > 0, "Search should return results"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    def test_swipe_navigation(self):
        """Test swipe gestures for navigation between screens."""
        try:
            # Login first
            login_screen = LoginScreen(self.driver)
            login_screen.login("user@example.com", "password123")
            
            # Test swipe left to navigate
            home_screen = HomeScreen(self.driver)
            
            # Get initial screen
            initial_screen = self.driver.current_activity
            
            # Swipe left
            home_screen.swipe_element((By.ID, "main_content"), "left")
            
            # Verify screen changed
            new_screen = self.driver.current_activity
            assert initial_screen != new_screen, "Swipe should change screen"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    def test_device_rotation(self):
        """Test application behavior during device orientation changes."""
        try:
            # Login first
            login_screen = LoginScreen(self.driver)
            login_screen.login("user@example.com", "password123")
            
            home_screen = HomeScreen(self.driver)
            
            # Test portrait mode
            home_screen.rotate_device("portrait")
            assert home_screen.is_element_visible(home_screen.menu_button), "Menu should be visible in portrait"
            
            # Test landscape mode
            home_screen.rotate_device("landscape")
            assert home_screen.is_element_visible(home_screen.menu_button), "Menu should be visible in landscape"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    @pytest.mark.skip(reason="Requires specific device configuration")
    def test_push_notifications(self):
        """Test push notification reception and handling."""
        # This test requires specific setup and would be skipped normally
        if hasattr(self, 'test_tracker'):
            self.test_tracker.end_test(
                test_status='skipped',
                error_message="Requires specific device configuration"
            )

class TestMobileGestures(BaseMobileTest):
    """Test mobile-specific gestures and interactions."""
    
    def test_pinch_zoom(self):
        """Test pinch-to-zoom gesture functionality on images."""
        try:
            # Login and navigate to content that supports zoom
            login_screen = LoginScreen(self.driver)
            login_screen.login("user@example.com", "password123")
            
            home_screen = HomeScreen(self.driver)
            
            # Navigate to image or map view
            image_view = (By.ID, "image_view")
            home_screen.tap_element(image_view)
            
            # Perform pinch zoom
            home_screen.pinch_zoom(image_view, scale=2.0)
            
            # Verify zoom level changed (this would depend on app implementation)
            screenshot_path = self.take_screenshot("after_pinch_zoom")
            if hasattr(self, 'test_tracker'):
                self.test_tracker.add_screenshot(screenshot_path)
                
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    def test_long_press_context_menu(self):
        """Test long press gesture to open context menu."""
        try:
            # Login first
            login_screen = LoginScreen(self.driver)
            login_screen.login("user@example.com", "password123")
            
            home_screen = HomeScreen(self.driver)
            
            # Long press on an item
            list_item = (By.XPATH, "//android.widget.TextView[@text='Sample Item']")
            home_screen.long_press_element(list_item, duration=2000)
            
            # Verify context menu appears
            context_menu = (By.ID, "context_menu")
            assert home_screen.is_element_visible(context_menu, timeout=5), "Context menu should appear after long press"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise