import pytest
from tests.conftest import auth_header


class TestTicketValidation:
    """Tests for ticket validation errors."""
    
    def test_create_ticket_empty_subject(self, client, customer_token):
        """Test creating ticket with empty subject."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': '',
                'description': 'This is a valid description with enough characters'
            })
        assert response.status_code == 400
        assert 'errors' in response.json or 'error' in response.json
    
    def test_create_ticket_short_subject(self, client, customer_token):
        """Test creating ticket with too short subject."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': 'Hi',
                'description': 'This is a valid description with enough characters'
            })
        assert response.status_code == 400
    
    def test_create_ticket_short_description(self, client, customer_token):
        """Test creating ticket with too short description."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': 'Valid subject here',
                'description': 'Short'
            })
        assert response.status_code == 400
    
    def test_create_ticket_invalid_priority(self, client, customer_token):
        """Test creating ticket with invalid priority."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': 'Valid subject here',
                'description': 'This is a valid description with enough characters',
                'priority': 'super_urgent'
            })
        assert response.status_code == 400
    
    def test_create_ticket_invalid_category(self, client, customer_token):
        """Test creating ticket with invalid category."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': 'Valid subject here',
                'description': 'This is a valid description with enough characters',
                'category': 'invalid_category'
            })
        assert response.status_code == 400
    
    def test_create_ticket_missing_required_fields(self, client, customer_token):
        """Test creating ticket without required fields."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={})
        assert response.status_code == 400


class TestAuthValidation:
    """Tests for authentication validation errors."""
    
    def test_register_invalid_email(self, client, app, _db):
        """Test registration with invalid email format."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'not-an-email',
            'password': 'SecurePass123'
        })
        assert response.status_code == 400
    
    def test_register_short_password(self, client, app, _db):
        """Test registration with too short password."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'valid@email.com',
            'password': '123'
        })
        assert response.status_code == 400
    
    def test_register_missing_name(self, client, app, _db):
        """Test registration without name."""
        response = client.post('/api/auth/register', json={
            'email': 'valid@email.com',
            'password': 'SecurePass123'
        })
        assert response.status_code == 400
    
    def test_register_missing_email(self, client, app, _db):
        """Test registration without email."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'password': 'SecurePass123'
        })
        assert response.status_code == 400
    
    def test_register_missing_password(self, client, app, _db):
        """Test registration without password."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'valid@email.com'
        })
        assert response.status_code == 400
    
    def test_login_missing_email(self, client, app, _db):
        """Test login without email."""
        response = client.post('/api/auth/login', json={
            'password': 'SecurePass123'
        })
        assert response.status_code == 400
    
    def test_login_missing_password(self, client, app, _db):
        """Test login without password."""
        response = client.post('/api/auth/login', json={
            'email': 'valid@email.com'
        })
        assert response.status_code == 400


class TestCommentValidation:
    """Tests for comment validation errors."""
    
    def test_create_comment_empty_content(self, client, customer_token, ticket):
        """Test creating comment with empty content."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token),
            json={'content': ''})
        assert response.status_code == 400
    
    def test_create_comment_missing_content(self, client, customer_token, ticket):
        """Test creating comment without content field."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token),
            json={})
        assert response.status_code == 400


class TestAgentValidation:
    """Tests for agent validation errors."""
    
    def test_create_agent_invalid_email(self, client, admin_token, app, _db):
        """Test creating agent with invalid email."""
        response = client.post('/api/agents',
            headers=auth_header(admin_token),
            json={
                'name': 'New Agent',
                'email': 'invalid-email',
                'password': 'SecurePass123'
            })
        assert response.status_code == 400
    
    def test_create_agent_missing_name(self, client, admin_token, app, _db):
        """Test creating agent without name."""
        response = client.post('/api/agents',
            headers=auth_header(admin_token),
            json={
                'email': 'agent@test.com',
                'password': 'SecurePass123'
            })
        assert response.status_code == 400


class TestPriorityUpdateValidation:
    """Tests for priority update validation."""
    
    def test_update_priority_missing_reason(self, client, agent_token, ticket):
        """Test updating priority without required reason."""
        response = client.put(f'/api/tickets/{ticket.id}/priority',
            headers=auth_header(agent_token),
            json={'priority': 'urgent'})
        assert response.status_code == 400
    
    def test_update_priority_invalid_value(self, client, agent_token, ticket):
        """Test updating priority with invalid value."""
        response = client.put(f'/api/tickets/{ticket.id}/priority',
            headers=auth_header(agent_token),
            json={
                'priority': 'super_high',
                'reason': 'Valid reason'
            })
        assert response.status_code == 400
    
    def test_update_priority_empty_reason(self, client, agent_token, ticket):
        """Test updating priority with empty reason."""
        response = client.put(f'/api/tickets/{ticket.id}/priority',
            headers=auth_header(agent_token),
            json={
                'priority': 'urgent',
                'reason': ''
            })
        assert response.status_code == 400


class TestStatusUpdateValidation:
    """Tests for status update validation."""
    
    def test_update_status_invalid_value(self, client, agent_token, ticket):
        """Test updating status with invalid value."""
        response = client.put(f'/api/tickets/{ticket.id}/status',
            headers=auth_header(agent_token),
            json={'status': 'invalid_status'})
        assert response.status_code == 400
    
    def test_update_status_invalid_transition(self, client, agent_token, ticket):
        """Test invalid status transition (open -> resolved)."""
        response = client.put(f'/api/tickets/{ticket.id}/status',
            headers=auth_header(agent_token),
            json={'status': 'resolved'})
        assert response.status_code == 400


class TestAssignmentValidation:
    """Tests for ticket assignment validation."""
    
    def test_assign_ticket_missing_agent_id(self, client, admin_token, ticket):
        """Test assigning ticket without agent_id."""
        response = client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(admin_token),
            json={})
        assert response.status_code == 400
    
    def test_assign_ticket_invalid_agent_id(self, client, admin_token, ticket):
        """Test assigning ticket to non-existent agent."""
        response = client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(admin_token),
            json={'agent_id': 99999})
        assert response.status_code == 404
