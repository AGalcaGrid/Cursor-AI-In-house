import pytest
from tests.conftest import auth_header


class TestAgentList:
    """Tests for listing agents."""
    
    def test_list_agents_agent(self, client, agent_token, agent):
        """Test agent can list agents."""
        response = client.get('/api/agents', headers=auth_header(agent_token))
        assert response.status_code == 200
        assert response.json['status'] == 'success'
    
    def test_list_agents_admin(self, client, admin_token, agent):
        """Test admin can list agents."""
        response = client.get('/api/agents', headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_list_agents_forbidden_customer(self, client, customer_token):
        """Test customer cannot list agents."""
        response = client.get('/api/agents', headers=auth_header(customer_token))
        assert response.status_code == 403
    
    def test_list_agents_filter_available(self, client, agent_token, agent):
        """Test filtering agents by availability."""
        response = client.get('/api/agents?available=true',
            headers=auth_header(agent_token))
        assert response.status_code == 200
    
    def test_list_agents_filter_department(self, client, agent_token, agent):
        """Test filtering agents by department."""
        response = client.get('/api/agents?department=Technical%20Support',
            headers=auth_header(agent_token))
        assert response.status_code == 200


class TestAgentGet:
    """Tests for getting agent details."""
    
    def test_get_agent_success(self, client, agent_token, agent):
        """Test getting agent details."""
        response = client.get(f'/api/agents/{agent.id}',
            headers=auth_header(agent_token))
        assert response.status_code == 200
        assert response.json['data']['email'] == 'agent@test.com'
    
    def test_get_agent_not_found(self, client, agent_token):
        """Test getting non-existent agent."""
        response = client.get('/api/agents/99999',
            headers=auth_header(agent_token))
        assert response.status_code == 404


class TestAgentCreate:
    """Tests for creating agents."""
    
    def test_create_agent_admin(self, client, admin_token, db_session):
        """Test admin can create agent."""
        response = client.post('/api/agents',
            headers=auth_header(admin_token),
            json={
                'name': 'New Agent',
                'email': 'newagent@test.com',
                'password': 'SecurePass123',
                'department': 'Billing'
            })
        assert response.status_code == 201
        assert response.json['data']['email'] == 'newagent@test.com'
    
    def test_create_agent_forbidden_agent(self, client, agent_token):
        """Test agent cannot create other agents."""
        response = client.post('/api/agents',
            headers=auth_header(agent_token),
            json={
                'name': 'New Agent',
                'email': 'newagent2@test.com',
                'password': 'SecurePass123'
            })
        assert response.status_code == 403
    
    def test_create_agent_duplicate_email(self, client, admin_token, agent):
        """Test creating agent with existing email."""
        response = client.post('/api/agents',
            headers=auth_header(admin_token),
            json={
                'name': 'Duplicate Agent',
                'email': 'agent@test.com',
                'password': 'SecurePass123'
            })
        assert response.status_code == 409


class TestAgentUpdate:
    """Tests for updating agents."""
    
    def test_update_agent_admin(self, client, admin_token, agent):
        """Test admin can update agent."""
        response = client.put(f'/api/agents/{agent.id}',
            headers=auth_header(admin_token),
            json={'department': 'New Department', 'max_tickets': 15})
        assert response.status_code == 200
        assert response.json['data']['department'] == 'New Department'
    
    def test_update_agent_forbidden_agent(self, client, agent_token, agent):
        """Test agent cannot update other agents."""
        response = client.put(f'/api/agents/{agent.id}',
            headers=auth_header(agent_token),
            json={'department': 'Hacked'})
        assert response.status_code == 403


class TestAgentTickets:
    """Tests for agent tickets endpoint."""
    
    def test_get_agent_tickets(self, client, agent_token, agent, assigned_ticket):
        """Test getting agent's assigned tickets."""
        response = client.get(f'/api/agents/{agent.id}/tickets',
            headers=auth_header(agent_token))
        assert response.status_code == 200
    
    def test_get_agent_tickets_with_filter(self, client, agent_token, agent, assigned_ticket):
        """Test filtering agent tickets by status."""
        response = client.get(f'/api/agents/{agent.id}/tickets?status=assigned',
            headers=auth_header(agent_token))
        assert response.status_code == 200


class TestAgentAvailability:
    """Tests for agent availability."""
    
    def test_update_availability_self(self, client, agent_token, agent):
        """Test agent can update their own availability."""
        response = client.put(f'/api/agents/{agent.id}/availability',
            headers=auth_header(agent_token),
            json={'is_available': False})
        assert response.status_code == 200
        assert response.json['data']['is_available'] == False
    
    def test_update_availability_admin(self, client, admin_token, agent):
        """Test admin can update agent availability."""
        response = client.put(f'/api/agents/{agent.id}/availability',
            headers=auth_header(admin_token),
            json={'is_available': True})
        assert response.status_code == 200
    
    def test_update_availability_missing_field(self, client, agent_token, agent):
        """Test updating availability without required field."""
        response = client.put(f'/api/agents/{agent.id}/availability',
            headers=auth_header(agent_token),
            json={})
        assert response.status_code == 400
