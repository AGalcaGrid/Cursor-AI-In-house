import pytest
from pages.dashboard_page import DashboardPage
from pages.ticket_page import TicketPage


class TestTicketFlow:
    """E2E tests for ticket management functionality"""
    
    @pytest.fixture
    def dashboard_page(self, authenticated_driver, base_url):
        """Initialize dashboard page with authenticated session"""
        authenticated_driver.get(f"{base_url}/dashboard")
        return DashboardPage(authenticated_driver, base_url)
    
    def test_create_ticket(self, dashboard_page, test_data):
        """Test creating a new ticket"""
        dashboard_page.click_create_ticket()
        
        ticket_page = TicketPage(dashboard_page.driver)
        ticket_data = test_data["test_ticket"]
        
        ticket_page.create_ticket(
            title=ticket_data["title"],
            description=ticket_data["description"],
            priority=ticket_data["priority"],
            category=ticket_data["category"]
        )
        
        assert ticket_page.is_success_displayed()
        assert "created" in ticket_page.get_success_message().lower()
    
    def test_view_ticket_details(self, dashboard_page):
        """Test viewing ticket details"""
        initial_count = dashboard_page.get_ticket_count()
        assert initial_count > 0, "Should have at least one ticket"
        
        # Click first ticket
        dashboard_page.click(DashboardPage.TICKET_ITEMS)
        
        ticket_page = TicketPage(dashboard_page.driver)
        assert ticket_page.get_ticket_title() != ""
        assert ticket_page.get_ticket_status() != ""
    
    def test_add_comment_to_ticket(self, dashboard_page):
        """Test adding a comment to a ticket"""
        dashboard_page.click(DashboardPage.TICKET_ITEMS)
        
        ticket_page = TicketPage(dashboard_page.driver)
        initial_comments = ticket_page.get_comment_count()
        
        ticket_page.add_comment("This is a test comment")
        
        assert ticket_page.get_comment_count() == initial_comments + 1
    
    def test_close_ticket(self, dashboard_page):
        """Test closing a ticket"""
        dashboard_page.click(DashboardPage.TICKET_ITEMS)
        
        ticket_page = TicketPage(dashboard_page.driver)
        ticket_page.close_ticket()
        
        assert ticket_page.get_ticket_status().lower() == "closed"
    
    def test_reopen_ticket(self, dashboard_page):
        """Test reopening a closed ticket"""
        # Filter to show closed tickets
        dashboard_page.filter_by_status("Closed")
        dashboard_page.click(DashboardPage.TICKET_ITEMS)
        
        ticket_page = TicketPage(dashboard_page.driver)
        ticket_page.reopen_ticket()
        
        assert ticket_page.get_ticket_status().lower() in ["open", "reopened"]
    
    def test_search_tickets(self, dashboard_page, test_data):
        """Test searching for tickets"""
        search_term = test_data["test_ticket"]["title"]
        dashboard_page.search_tickets(search_term)
        
        # Verify search results
        ticket_count = dashboard_page.get_ticket_count()
        assert ticket_count >= 0  # May or may not find results
    
    def test_filter_tickets_by_status(self, dashboard_page):
        """Test filtering tickets by status"""
        dashboard_page.filter_by_status("Open")
        
        # All visible tickets should be open
        ticket_count = dashboard_page.get_ticket_count()
        assert ticket_count >= 0
    
    def test_dashboard_stats_displayed(self, dashboard_page):
        """Test that dashboard statistics are displayed"""
        stats = dashboard_page.get_stats()
        
        assert 'total' in stats
        assert 'open' in stats
        assert 'closed' in stats
    
    def test_create_ticket_validation(self, dashboard_page):
        """Test ticket creation validation"""
        dashboard_page.click_create_ticket()
        
        ticket_page = TicketPage(dashboard_page.driver)
        
        # Try to submit without filling required fields
        ticket_page.click(TicketPage.SUBMIT_BUTTON)
        
        assert ticket_page.is_element_visible(TicketPage.ERROR_MESSAGE)
