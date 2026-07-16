import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


class TestLoginFlow:
    """E2E tests for login functionality"""
    
    @pytest.fixture
    def login_page(self, driver, base_url):
        """Initialize login page"""
        driver.get(f"{base_url}/login")
        return LoginPage(driver, base_url)
    
    def test_successful_login(self, login_page, test_data):
        """Test successful login flow"""
        user = test_data["valid_user"]
        login_page.login(user["email"], user["password"])
        
        dashboard = DashboardPage(login_page.driver)
        assert dashboard.is_displayed(), "Dashboard should be displayed after login"
        assert "Welcome" in dashboard.get_welcome_message()
    
    def test_login_with_invalid_credentials(self, login_page, test_data):
        """Test login with wrong password"""
        user = test_data["invalid_user"]
        login_page.login(user["email"], user["password"])
        
        assert login_page.is_error_displayed(), "Error message should be displayed"
        error_msg = login_page.get_error_message()
        assert "Invalid credentials" in error_msg or "incorrect" in error_msg.lower()
    
    def test_login_with_empty_email(self, login_page):
        """Test login with empty email"""
        login_page.login("", "password123")
        
        assert login_page.is_error_displayed()
        error_msg = login_page.get_error_message()
        assert "email" in error_msg.lower() or "required" in error_msg.lower()
    
    def test_login_with_empty_password(self, login_page):
        """Test login with empty password"""
        login_page.login("test@example.com", "")
        
        assert login_page.is_error_displayed()
        error_msg = login_page.get_error_message()
        assert "password" in error_msg.lower() or "required" in error_msg.lower()
    
    def test_login_with_empty_fields(self, login_page):
        """Test login with empty email and password"""
        login_page.login("", "")
        
        assert login_page.is_error_displayed()
        error_msg = login_page.get_error_message()
        assert "required" in error_msg.lower() or "email" in error_msg.lower() or "password" in error_msg.lower()
    
    def test_login_with_invalid_email_format(self, login_page):
        """Test login with invalid email format"""
        login_page.login("invalidemail", "password123")
        
        assert login_page.is_error_displayed()
        error_msg = login_page.get_error_message()
        assert "email" in error_msg.lower() or "invalid" in error_msg.lower()
    
    def test_login_page_elements_visible(self, login_page):
        """Test that all login page elements are visible"""
        assert login_page.is_element_visible(LoginPage.EMAIL_INPUT)
        assert login_page.is_element_visible(LoginPage.PASSWORD_INPUT)
        assert login_page.is_element_visible(LoginPage.LOGIN_BUTTON)
    
    def test_forgot_password_link(self, login_page):
        """Test forgot password link navigation"""
        login_page.click_forgot_password()
        assert "forgot" in login_page.get_current_url().lower() or "reset" in login_page.get_current_url().lower()
    
    def test_register_link(self, login_page):
        """Test register link navigation"""
        login_page.click_register()
        assert "register" in login_page.get_current_url().lower() or "signup" in login_page.get_current_url().lower()
