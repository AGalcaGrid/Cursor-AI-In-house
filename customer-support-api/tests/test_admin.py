import pytest
from tests.conftest import auth_header


class TestAdminDashboard:
    """Tests for admin dashboard."""
    
    def test_get_dashboard_admin(self, client, admin_token, ticket):
        """Test admin can access dashboard."""
        response = client.get('/api/admin/dashboard',
            headers=auth_header(admin_token))
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert 'tickets' in response.json['data']
        assert 'agents' in response.json['data']
        assert 'customers' in response.json['data']
    
    def test_get_dashboard_forbidden_agent(self, client, agent_token):
        """Test agent cannot access dashboard."""
        response = client.get('/api/admin/dashboard',
            headers=auth_header(agent_token))
        assert response.status_code == 403
    
    def test_get_dashboard_forbidden_customer(self, client, customer_token):
        """Test customer cannot access dashboard."""
        response = client.get('/api/admin/dashboard',
            headers=auth_header(customer_token))
        assert response.status_code == 403


class TestTicketReports:
    """Tests for ticket reports."""
    
    def test_get_ticket_report_admin(self, client, admin_token, ticket):
        """Test admin can get ticket report."""
        response = client.get('/api/admin/reports/tickets',
            headers=auth_header(admin_token))
        assert response.status_code == 200
        assert 'status_breakdown' in response.json['data']
        assert 'priority_breakdown' in response.json['data']
        assert 'metrics' in response.json['data']
    
    def test_get_ticket_report_with_dates(self, client, admin_token, ticket):
        """Test ticket report with date filters."""
        response = client.get('/api/admin/reports/tickets?start_date=2024-01-01&end_date=2030-12-31',
            headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_get_ticket_report_forbidden(self, client, agent_token):
        """Test non-admin cannot access ticket report."""
        response = client.get('/api/admin/reports/tickets',
            headers=auth_header(agent_token))
        assert response.status_code == 403


class TestAgentReports:
    """Tests for agent reports."""
    
    def test_get_agent_report_admin(self, client, admin_token, agent, assigned_ticket):
        """Test admin can get agent report."""
        response = client.get('/api/admin/reports/agents',
            headers=auth_header(admin_token))
        assert response.status_code == 200
        assert isinstance(response.json['data'], list)
    
    def test_get_agent_report_forbidden(self, client, customer_token):
        """Test customer cannot access agent report."""
        response = client.get('/api/admin/reports/agents',
            headers=auth_header(customer_token))
        assert response.status_code == 403


class TestSLAReports:
    """Tests for SLA reports."""
    
    def test_get_sla_report_admin(self, client, admin_token, ticket):
        """Test admin can get SLA report."""
        response = client.get('/api/admin/reports/sla',
            headers=auth_header(admin_token))
        assert response.status_code == 200
        assert 'summary' in response.json['data']
        assert 'by_priority' in response.json['data']
    
    def test_get_sla_report_with_dates(self, client, admin_token, ticket):
        """Test SLA report with date filters."""
        response = client.get('/api/admin/reports/sla?start_date=2024-01-01',
            headers=auth_header(admin_token))
        assert response.status_code == 200


class TestUnassignedTickets:
    """Tests for unassigned tickets endpoint."""
    
    def test_get_unassigned_tickets_admin(self, client, admin_token, ticket):
        """Test admin can get unassigned tickets."""
        response = client.get('/api/admin/tickets/unassigned',
            headers=auth_header(admin_token))
        assert response.status_code == 200
        # All returned tickets should be unassigned and open
        for t in response.json['data']:
            assert t['assigned_to_id'] is None
            assert t['status'] == 'open'
    
    def test_get_unassigned_tickets_agent(self, client, agent_token, ticket):
        """Test agent can get unassigned tickets."""
        response = client.get('/api/admin/tickets/unassigned',
            headers=auth_header(agent_token))
        assert response.status_code == 200
    
    def test_get_unassigned_tickets_forbidden_customer(self, client, customer_token):
        """Test customer cannot get unassigned tickets."""
        response = client.get('/api/admin/tickets/unassigned',
            headers=auth_header(customer_token))
        assert response.status_code == 403


class TestSLABreachedTickets:
    """Tests for SLA breached tickets endpoint."""
    
    def test_get_sla_breached_tickets_admin(self, client, admin_token):
        """Test admin can get SLA breached tickets."""
        response = client.get('/api/admin/tickets/sla-breached',
            headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_get_sla_breached_tickets_by_type(self, client, admin_token):
        """Test filtering SLA breached tickets by type."""
        response = client.get('/api/admin/tickets/sla-breached?type=response',
            headers=auth_header(admin_token))
        assert response.status_code == 200
        
        response = client.get('/api/admin/tickets/sla-breached?type=resolution',
            headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_get_sla_breached_tickets_forbidden(self, client, agent_token):
        """Test non-admin cannot access SLA breached tickets."""
        response = client.get('/api/admin/tickets/sla-breached',
            headers=auth_header(agent_token))
        assert response.status_code == 403


class TestReportExport:
    """Tests for report export."""
    
    def test_export_tickets_report_json(self, client, admin_token, ticket):
        """Test exporting tickets report as JSON."""
        response = client.post('/api/admin/reports/export',
            headers=auth_header(admin_token),
            json={'report_type': 'tickets', 'format': 'json'})
        assert response.status_code == 200
    
    def test_export_tickets_report_csv(self, client, admin_token, ticket):
        """Test exporting tickets report as CSV."""
        response = client.post('/api/admin/reports/export',
            headers=auth_header(admin_token),
            json={'report_type': 'tickets', 'format': 'csv'})
        assert response.status_code == 200
        assert response.content_type == 'text/csv; charset=utf-8'
    
    def test_export_agents_report(self, client, admin_token, agent):
        """Test exporting agents report."""
        response = client.post('/api/admin/reports/export',
            headers=auth_header(admin_token),
            json={'report_type': 'agents', 'format': 'json'})
        assert response.status_code == 200
    
    def test_export_invalid_report_type(self, client, admin_token):
        """Test exporting with invalid report type."""
        response = client.post('/api/admin/reports/export',
            headers=auth_header(admin_token),
            json={'report_type': 'invalid', 'format': 'json'})
        assert response.status_code == 400
    
    def test_export_forbidden_customer(self, client, customer_token):
        """Test customer cannot export reports."""
        response = client.post('/api/admin/reports/export',
            headers=auth_header(customer_token),
            json={'report_type': 'tickets', 'format': 'json'})
        assert response.status_code == 403
