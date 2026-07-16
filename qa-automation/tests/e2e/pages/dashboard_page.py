from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from .base_page import BasePage


class DashboardPage(BasePage):
    """Page Object for Dashboard Page"""
    
    # Locators
    WELCOME_MESSAGE = (By.CLASS_NAME, "welcome-message")
    USER_MENU = (By.ID, "user-menu")
    LOGOUT_BUTTON = (By.ID, "logout-btn")
    TICKET_LIST = (By.CLASS_NAME, "ticket-list")
    TICKET_ITEMS = (By.CLASS_NAME, "ticket-item")
    CREATE_TICKET_BUTTON = (By.ID, "create-ticket-btn")
    SEARCH_INPUT = (By.ID, "search-tickets")
    FILTER_DROPDOWN = (By.ID, "filter-status")
    STATS_WIDGET = (By.CLASS_NAME, "stats-widget")
    NOTIFICATION_BADGE = (By.CLASS_NAME, "notification-badge")
    SIDEBAR = (By.CLASS_NAME, "sidebar")
    MAIN_CONTENT = (By.CLASS_NAME, "main-content")
    
    def __init__(self, driver: WebDriver, base_url: str = "http://localhost:3000"):
        super().__init__(driver)
        self.base_url = base_url
        self.url = f"{base_url}/dashboard"
    
    def is_displayed(self) -> bool:
        """Check if dashboard is displayed"""
        return self.is_element_visible(self.WELCOME_MESSAGE)
    
    def get_welcome_message(self) -> str:
        """Get welcome message text"""
        return self.get_text(self.WELCOME_MESSAGE)
    
    def logout(self):
        """Perform logout"""
        self.click(self.USER_MENU)
        self.click(self.LOGOUT_BUTTON)
    
    def get_ticket_count(self) -> int:
        """Get number of tickets displayed"""
        tickets = self.find_elements(self.TICKET_ITEMS)
        return len(tickets)
    
    def click_create_ticket(self):
        """Click create ticket button"""
        self.click(self.CREATE_TICKET_BUTTON)
    
    def search_tickets(self, query: str):
        """Search for tickets"""
        self.type(self.SEARCH_INPUT, query)
    
    def filter_by_status(self, status: str):
        """Filter tickets by status"""
        from selenium.webdriver.support.ui import Select
        dropdown = Select(self.find_element(self.FILTER_DROPDOWN))
        dropdown.select_by_visible_text(status)
    
    def get_notification_count(self) -> int:
        """Get notification count"""
        try:
            badge_text = self.get_text(self.NOTIFICATION_BADGE)
            return int(badge_text) if badge_text else 0
        except:
            return 0
    
    def is_sidebar_visible(self) -> bool:
        """Check if sidebar is visible"""
        return self.is_element_visible(self.SIDEBAR)
    
    def get_stats(self) -> dict:
        """Get dashboard statistics"""
        stats_element = self.find_element(self.STATS_WIDGET)
        return {
            'total': stats_element.find_element(By.CLASS_NAME, 'stat-total').text,
            'open': stats_element.find_element(By.CLASS_NAME, 'stat-open').text,
            'closed': stats_element.find_element(By.CLASS_NAME, 'stat-closed').text
        }
