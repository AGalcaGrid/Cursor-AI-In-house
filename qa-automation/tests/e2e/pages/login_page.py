from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from .base_page import BasePage


class LoginPage(BasePage):
    """Page Object for Login Page"""
    
    # Locators
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    REMEMBER_ME_CHECKBOX = (By.ID, "remember-me")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot Password?")
    REGISTER_LINK = (By.LINK_TEXT, "Register")
    LOADING_SPINNER = (By.CLASS_NAME, "loading-spinner")
    
    def __init__(self, driver: WebDriver, base_url: str = "http://localhost:3000"):
        super().__init__(driver)
        self.base_url = base_url
        self.url = f"{base_url}/login"
    
    def open(self):
        """Navigate to login page"""
        self.navigate_to(self.url)
        return self
    
    def login(self, email: str, password: str):
        """Perform login with given credentials"""
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
    
    def login_with_remember_me(self, email: str, password: str):
        """Login with remember me option checked"""
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.REMEMBER_ME_CHECKBOX)
        self.click(self.LOGIN_BUTTON)
    
    def get_error_message(self) -> str:
        """Get error message text"""
        return self.get_text(self.ERROR_MESSAGE)
    
    def is_error_displayed(self) -> bool:
        """Check if error message is displayed"""
        return self.is_element_visible(self.ERROR_MESSAGE)
    
    def click_forgot_password(self):
        """Click forgot password link"""
        self.click(self.FORGOT_PASSWORD_LINK)
    
    def click_register(self):
        """Click register link"""
        self.click(self.REGISTER_LINK)
    
    def wait_for_login_complete(self):
        """Wait for login process to complete"""
        self.wait_for_element_invisible(self.LOADING_SPINNER)
    
    def is_login_page(self) -> bool:
        """Check if current page is login page"""
        return "/login" in self.get_current_url()
