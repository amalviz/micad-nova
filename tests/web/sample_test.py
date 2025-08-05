"""
Sample web test using the framework.
"""
import pytest
import traceback
from core.base_test import BaseWebTest
from page_objects.web.base_page import BasePage

class LoginPage(BasePage):
    """Sample login page object."""
    
    def __init__(self, page):
        super().__init__(page)
        self.email_input = "#email"
        self.password_input = "#password" 
        self.login_button = "button[type='submit']"
        self.error_message = ".error-message"
        self.dashboard_header = "h1.dashboard"
    
    async def login(self, email: str, password: str):
        """Perform login action."""
        await self.type_text(self.email_input, email)
        await self.type_text(self.password_input, password)
        await self.click_element(self.login_button)
        self.log_step(f"Attempted login with email: {email}")
    
    async def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        return await self.is_element_visible(self.dashboard_header)
    
    async def get_error_message(self) -> str:
        """Get login error message."""
        if await self.is_element_visible(self.error_message):
            return await self.get_text(self.error_message)
        return ""

class TestWebLogin(BaseWebTest):
    """Sample web login tests."""
    
    async def test_valid_login(self):
        """Test successful login with valid user credentials."""
        try:
            login_page = LoginPage(self.page)
            
            await login_page.navigate_to("https://example.com/login")
            await login_page.login("user@example.com", "password123")
            
            # Take screenshot for documentation
            screenshot_path = await self.take_screenshot("login_attempt")
            if hasattr(self, 'test_tracker'):
                self.test_tracker.add_screenshot(screenshot_path)
            
            # Verify login success
            assert await login_page.is_logged_in(), "Login should be successful"
            
        except Exception as e:
            # Update test status to failed
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    async def test_invalid_email(self):
        """Test login attempt with invalid email format."""
        try:
            login_page = LoginPage(self.page)
            
            await login_page.navigate_to("https://example.com/login")
            await login_page.login("invalid-email", "password123")
            
            # Verify error message appears
            error_message = await login_page.get_error_message()
            assert "Invalid email" in error_message, "Should show invalid email error"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    async def test_empty_password(self):
        """Test login attempt with empty password field."""
        try:
            login_page = LoginPage(self.page)
            
            await login_page.navigate_to("https://example.com/login")
            await login_page.login("user@example.com", "")
            
            # Verify error message appears
            error_message = await login_page.get_error_message()
            assert "Password is required" in error_message, "Should show password required error"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
        login_page = LoginPage(self.page)
        
        await login_page.navigate_to("https://example.com/login")
        await login_page.login("user@example.com", "password123")
        
        # Take screenshot for documentation
        await self.take_screenshot("login_attempt")
        
        # Verify login success
        assert await login_page.is_logged_in(), "Login should be successful"
    
    async def test_invalid_email(self):
        """Test login with invalid email."""
        login_page = LoginPage(self.page)
        
        await login_page.navigate_to("https://example.com/login")
        await login_page.login("invalid-email", "password123")
        
        # Verify error message appears
        error_message = await login_page.get_error_message()
        assert "Invalid email" in error_message, "Should show invalid email error"
    
    async def test_empty_password(self):
        """Test login with empty password."""
        login_page = LoginPage(self.page)
        
        await login_page.navigate_to("https://example.com/login")
        await login_page.login("user@example.com", "")
        
        # Verify error message appears
        error_message = await login_page.get_error_message()
        assert "Password is required" in error_message, "Should show password required error"
    
    @pytest.mark.skip(reason="Feature not implemented yet")
    async def test_forgot_password(self):
        """Test forgot password link functionality."""
        # This test is skipped for demonstration
        if hasattr(self, 'test_tracker'):
            self.test_tracker.end_test(
                test_status='skipped',
                error_message="Feature not implemented yet"
            )

class TestWebNavigation(BaseWebTest):
    """Sample web navigation tests."""
    
    async def test_page_title(self):
        """Verify that the main page displays correct title."""
        try:
            await self.page.goto("https://example.com")
            
            title = await self.page.title()
            assert "Example" in title, "Page title should contain 'Example'"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    async def test_navigation_links(self):
        """Test that navigation links redirect to correct pages."""
        try:
            await self.page.goto("https://example.com")
            
            # Test navigation to different sections
            await self.page.click("a[href='/about']")
            await self.page.wait_for_url("**/about")
            
            title = await self.page.title()
            assert "About" in title, "About page should load correctly"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise
    
    async def test_responsive_design(self):
        """Verify responsive design elements on mobile viewport."""
        try:
            # Set mobile viewport
            await self.page.set_viewport_size({"width": 375, "height": 667})
            await self.page.goto("https://example.com")
            
            # Check mobile menu is visible
            mobile_menu = await self.page.is_visible(".mobile-menu-button")
            assert mobile_menu, "Mobile menu should be visible on small screens"
            
        except Exception as e:
            if hasattr(self, 'test_tracker'):
                self.test_tracker.end_test(
                    test_status='failed',
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise