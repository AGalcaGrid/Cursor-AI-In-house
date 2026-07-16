from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from .base_page import BasePage


class TicketPage(BasePage):
    """Page Object for Ticket Details/Create Page"""
    
    # Locators - Create Ticket Form
    TITLE_INPUT = (By.ID, "ticket-title")
    DESCRIPTION_INPUT = (By.ID, "ticket-description")
    PRIORITY_DROPDOWN = (By.ID, "ticket-priority")
    CATEGORY_DROPDOWN = (By.ID, "ticket-category")
    SUBMIT_BUTTON = (By.ID, "submit-ticket")
    CANCEL_BUTTON = (By.ID, "cancel-btn")
    
    # Locators - Ticket Details
    TICKET_TITLE = (By.CLASS_NAME, "ticket-title")
    TICKET_STATUS = (By.CLASS_NAME, "ticket-status")
    TICKET_PRIORITY = (By.CLASS_NAME, "ticket-priority")
    TICKET_DESCRIPTION = (By.CLASS_NAME, "ticket-description")
    TICKET_CREATED_DATE = (By.CLASS_NAME, "ticket-created")
    TICKET_UPDATED_DATE = (By.CLASS_NAME, "ticket-updated")
    
    # Locators - Comments
    COMMENT_INPUT = (By.ID, "comment-input")
    ADD_COMMENT_BUTTON = (By.ID, "add-comment-btn")
    COMMENT_LIST = (By.CLASS_NAME, "comment-list")
    COMMENT_ITEMS = (By.CLASS_NAME, "comment-item")
    
    # Locators - Actions
    EDIT_BUTTON = (By.ID, "edit-ticket-btn")
    DELETE_BUTTON = (By.ID, "delete-ticket-btn")
    CLOSE_TICKET_BUTTON = (By.ID, "close-ticket-btn")
    REOPEN_TICKET_BUTTON = (By.ID, "reopen-ticket-btn")
    
    # Locators - Messages
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success-message")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    
    def __init__(self, driver: WebDriver, base_url: str = "http://localhost:3000"):
        super().__init__(driver)
        self.base_url = base_url
    
    def create_ticket(self, title: str, description: str, priority: str = "Medium", category: str = "General"):
        """Create a new ticket"""
        self.type(self.TITLE_INPUT, title)
        self.type(self.DESCRIPTION_INPUT, description)
        self.select_priority(priority)
        self.select_category(category)
        self.click(self.SUBMIT_BUTTON)
    
    def select_priority(self, priority: str):
        """Select ticket priority"""
        from selenium.webdriver.support.ui import Select
        dropdown = Select(self.find_element(self.PRIORITY_DROPDOWN))
        dropdown.select_by_visible_text(priority)
    
    def select_category(self, category: str):
        """Select ticket category"""
        from selenium.webdriver.support.ui import Select
        dropdown = Select(self.find_element(self.CATEGORY_DROPDOWN))
        dropdown.select_by_visible_text(category)
    
    def get_ticket_title(self) -> str:
        """Get ticket title"""
        return self.get_text(self.TICKET_TITLE)
    
    def get_ticket_status(self) -> str:
        """Get ticket status"""
        return self.get_text(self.TICKET_STATUS)
    
    def get_ticket_priority(self) -> str:
        """Get ticket priority"""
        return self.get_text(self.TICKET_PRIORITY)
    
    def get_ticket_description(self) -> str:
        """Get ticket description"""
        return self.get_text(self.TICKET_DESCRIPTION)
    
    def add_comment(self, comment: str):
        """Add a comment to the ticket"""
        self.type(self.COMMENT_INPUT, comment)
        self.click(self.ADD_COMMENT_BUTTON)
    
    def get_comment_count(self) -> int:
        """Get number of comments"""
        comments = self.find_elements(self.COMMENT_ITEMS)
        return len(comments)
    
    def close_ticket(self):
        """Close the ticket"""
        self.click(self.CLOSE_TICKET_BUTTON)
    
    def reopen_ticket(self):
        """Reopen the ticket"""
        self.click(self.REOPEN_TICKET_BUTTON)
    
    def delete_ticket(self):
        """Delete the ticket"""
        self.click(self.DELETE_BUTTON)
    
    def edit_ticket(self):
        """Click edit button"""
        self.click(self.EDIT_BUTTON)
    
    def get_success_message(self) -> str:
        """Get success message"""
        return self.get_text(self.SUCCESS_MESSAGE)
    
    def get_error_message(self) -> str:
        """Get error message"""
        return self.get_text(self.ERROR_MESSAGE)
    
    def is_success_displayed(self) -> bool:
        """Check if success message is displayed"""
        return self.is_element_visible(self.SUCCESS_MESSAGE)
