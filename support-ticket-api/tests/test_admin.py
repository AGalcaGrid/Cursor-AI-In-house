import pytest
from tests.conftest import auth_header


class TestAdminDashboard:
    """Tests for admin dashboard (FR-029)."""
    
    def test_admin_can_access_dashboard(self, client, admin_token, ticket):
        """Test admin can access dashboard."""
        response = client.get('/api/admin/dashboard', headers=auth_header(admin_token))
        assert response.status_code == 200
        assert 'dashboard' in response.json
        assert 'tickets' in response.json['dashboard']
    
    def test_dashboard_shows_ticket_stats(self, client, admin_token, ticket):
        """Test dashboard shows ticket statistics."""
        response = client.get('/api/admin/dashboard', headers=auth_header(admin_token))
        assert response.status_code == 200
        assert 'total' in response.json['dashboard']['tickets']
        assert 'open' in response.json['dashboard']['tickets']
    
    def test_dashboard_shows_sla_stats(self, client, admin_token, ticket):
        """Test dashboard shows SLA statistics."""
        response = client.get('/api/admin/dashboard', headers=auth_header(admin_token))
        assert response.status_code == 200
        assert 'sla' in response.json['dashboard']
        assert 'compliance_rate' in response.json['dashboard']['sla']
    
    def test_customer_cannot_access_dashboard(self, client, customer_token):
        """Test customer cannot access dashboard."""
        response = client.get('/api/admin/dashboard', headers=auth_header(customer_token))
        assert response.status_code == 403
    
    def test_agent_cannot_access_dashboard(self, client, agent_token):
        """Test agent cannot access dashboard."""
        response = client.get('/api/admin/dashboard', headers=auth_header(agent_token))
        assert response.status_code == 403


class TestAdminReports:
    """Tests for admin reports (FR-030)."""
    
    def test_get_ticket_report(self, client, admin_token, ticket):
        """Test getting ticket report."""
        response = client.get('/api/admin/reports/tickets', headers=auth_header(admin_token))
        assert response.status_code == 200
        assert 'report' in response.json
    
    def test_get_sla_report(self, client, admin_token, ticket):
        """Test getting SLA report."""
        response = client.get('/api/admin/reports/sla', headers=auth_header(admin_token))
        assert response.status_code == 200
        assert 'by_priority' in response.json['report']
    
    def test_customer_cannot_access_reports(self, client, customer_token):
        """Test customer cannot access reports."""
        response = client.get('/api/admin/reports/tickets', headers=auth_header(customer_token))
        assert response.status_code == 403
