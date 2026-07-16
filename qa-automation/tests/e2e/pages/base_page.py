from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from typing import Tuple


class BasePage:
    """Base page object with common methods for all page objects"""
    
    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.timeout = timeout
    
    def find_element(self, locator: Tuple[By, str]):
        """Wait for and return an element"""
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator: Tuple[By, str]):
        """Wait for and return multiple elements"""
        return self.wait.until(EC.presence_of_all_elements_located(locator))
    
    def click(self, locator: Tuple[By, str]):
        """Wait for element to be clickable and click it"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
    
    def type(self, locator: Tuple[By, str], text: str):
        """Clear field and type text"""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator: Tuple[By, str]) -> str:
        """Get text content of an element"""
        element = self.find_element(locator)
        return element.text
    
    def is_element_visible(self, locator: Tuple[By, str]) -> bool:
        """Check if element is visible"""
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except:
            return False
    
    def wait_for_element_invisible(self, locator: Tuple[By, str]):
        """Wait for element to become invisible"""
        self.wait.until(EC.invisibility_of_element_located(locator))
    
    def get_attribute(self, locator: Tuple[By, str], attribute: str) -> str:
        """Get attribute value of an element"""
        element = self.find_element(locator)
        return element.get_attribute(attribute)
    
    def scroll_to_element(self, locator: Tuple[By, str]):
        """Scroll to element"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.driver.current_url
    
    def get_title(self) -> str:
        """Get page title"""
        return self.driver.title
    
    def refresh(self):
        """Refresh the page"""
        self.driver.refresh()
    
    def navigate_to(self, url: str):
        """Navigate to a URL"""
        self.driver.get(url)
