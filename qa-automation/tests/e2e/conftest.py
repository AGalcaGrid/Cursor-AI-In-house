import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application"""
    return os.environ.get("BASE_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def api_url():
    """API URL for the backend"""
    return os.environ.get("API_URL", "http://localhost:5000")


@pytest.fixture(scope="function")
def driver():
    """Create a WebDriver instance for each test"""
    chrome_options = Options()
    
    # Headless mode for CI/CD
    if os.environ.get("HEADLESS", "true").lower() == "true":
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="function")
def authenticated_driver(driver, base_url):
    """Create an authenticated WebDriver session"""
    from pages.login_page import LoginPage
    
    driver.get(f"{base_url}/login")
    login_page = LoginPage(driver, base_url)
    
    # Use test credentials
    test_email = os.environ.get("TEST_USER_EMAIL", "test@example.com")
    test_password = os.environ.get("TEST_USER_PASSWORD", "password123")
    
    login_page.login(test_email, test_password)
    login_page.wait_for_login_complete()
    
    yield driver


@pytest.fixture(scope="session")
def test_data():
    """Test data for various tests"""
    return {
        "valid_user": {
            "email": "test@example.com",
            "password": "password123"
        },
        "invalid_user": {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        },
        "test_ticket": {
            "title": "Test Ticket",
            "description": "This is a test ticket description",
            "priority": "High",
            "category": "Technical"
        }
    }
