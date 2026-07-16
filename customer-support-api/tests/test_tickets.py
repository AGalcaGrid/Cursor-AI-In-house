import pytest
from tests.conftest import auth_header
from app.models.ticket import Ticket


class TestTicketCreate:
    """Tests for ticket creation."""
    
    def test_create_ticket_success(self, client, customer_token):
        """Test successful ticket creation."""
        response = client.post('/api/tickets', 
            headers=auth_header(customer_token),
            json={
                'subject': 'Cannot login to my account',
                'description': 'I have been trying to login but keep getting an error message',
                'priority': 'high',
                'category': 'technical'
            })
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert 'TICK-' in response.json['data']['ticket_number']
        assert response.json['data']['status'] == 'open'
        assert response.json['data']['priority'] == 'high'
    
    def test_create_ticket_default_priority(self, client, customer_token):
        """Test ticket creation with default priority."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': 'General inquiry about service',
                'description': 'I would like to know more about your services and pricing'
            })
        assert response.status_code == 201
        assert response.json['data']['priority'] == 'medium'
    
    def test_create_ticket_invalid_priority(self, client, customer_token):
        """Test ticket creation with invalid priority."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': 'Test ticket subject here',
                'description': 'This is a test description with enough characters',
                'priority': 'invalid'
            })
        assert response.status_code == 400
    
    def test_create_ticket_short_subject(self, client, customer_token):
        """Test ticket creation with too short subject."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': 'Hi',
                'description': 'This is a test description with enough characters'
            })
        assert response.status_code == 400
    
    def test_create_ticket_short_description(self, client, customer_token):
        """Test ticket creation with too short description."""
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': 'Valid subject here',
                'description': 'Too short'
            })
        assert response.status_code == 400
    
    def test_create_ticket_unauthorized(self, client):
        """Test ticket creation without authentication."""
        response = client.post('/api/tickets', json={
            'subject': 'Test ticket',
            'description': 'This is a test description'
        })
        assert response.status_code == 401


class TestTicketList:
    """Tests for listing tickets."""
    
    def test_list_tickets_customer(self, client, customer_token, ticket):
        """Test customer can list their own tickets."""
        response = client.get('/api/tickets', headers=auth_header(customer_token))
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert 'tickets' in response.json['data']
        assert len(response.json['data']['tickets']) >= 1
    
    def test_list_tickets_agent(self, client, agent_token, ticket, assigned_ticket):
        """Test agent can list tickets."""
        response = client.get('/api/tickets', headers=auth_header(agent_token))
        assert response.status_code == 200
        assert response.json['status'] == 'success'
    
    def test_list_tickets_with_filters(self, client, customer_token, ticket):
        """Test listing tickets with filters."""
        response = client.get('/api/tickets?status=open&priority=medium',
            headers=auth_header(customer_token))
        assert response.status_code == 200
        for t in response.json['data']['tickets']:
            assert t['status'] == 'open'
            assert t['priority'] == 'medium'
    
    def test_list_tickets_pagination(self, client, customer_token, ticket):
        """Test ticket listing pagination."""
        response = client.get('/api/tickets?page=1&per_page=5',
            headers=auth_header(customer_token))
        assert response.status_code == 200
        assert 'pagination' in response.json['data']
        assert response.json['data']['pagination']['page'] == 1
        assert response.json['data']['pagination']['per_page'] == 5


class TestTicketGet:
    """Tests for getting a single ticket."""
    
    def test_get_ticket_success(self, client, customer_token, ticket):
        """Test getting a ticket by ID."""
        response = client.get(f'/api/tickets/{ticket.id}',
            headers=auth_header(customer_token))
        assert response.status_code == 200
        assert response.json['data']['id'] == ticket.id
    
    def test_get_ticket_not_found(self, client, customer_token):
        """Test getting non-existent ticket."""
        response = client.get('/api/tickets/99999',
            headers=auth_header(customer_token))
        assert response.status_code == 404
    
    def test_get_ticket_forbidden(self, client, agent_token, ticket):
        """Test customer cannot access another customer's ticket."""
        # Create another customer and their token
        from app.models.customer import Customer
        from app import db
        
        other_customer = Customer(
            name='Other Customer',
            email='other@test.com',
            role='customer'
        )
        other_customer.set_password('TestPass123')
        db.session.add(other_customer)
        db.session.commit()
        
        login_response = client.post('/api/auth/login', json={
            'email': 'other@test.com',
            'password': 'TestPass123'
        })
        other_token = login_response.json['data']['access_token']
        
        response = client.get(f'/api/tickets/{ticket.id}',
            headers=auth_header(other_token))
        assert response.status_code == 403


class TestTicketUpdate:
    """Tests for updating tickets."""
    
    def test_update_ticket_success(self, client, customer_token, ticket):
        """Test updating a ticket."""
        response = client.put(f'/api/tickets/{ticket.id}',
            headers=auth_header(customer_token),
            json={'subject': 'Updated Subject Here'})
        assert response.status_code == 200
        assert response.json['data']['subject'] == 'Updated Subject Here'
    
    def test_update_ticket_not_found(self, client, customer_token):
        """Test updating non-existent ticket."""
        response = client.put('/api/tickets/99999',
            headers=auth_header(customer_token),
            json={'subject': 'Updated Subject'})
        assert response.status_code == 404


class TestTicketAssign:
    """Tests for ticket assignment."""
    
    def test_assign_ticket_success(self, client, admin_token, ticket, agent):
        """Test assigning a ticket to an agent."""
        response = client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(admin_token),
            json={'agent_id': agent.id})
        assert response.status_code == 200
        assert response.json['data']['assigned_to_id'] == agent.id
        assert response.json['data']['status'] == 'assigned'
    
    def test_assign_ticket_agent_not_found(self, client, admin_token, ticket):
        """Test assigning to non-existent agent."""
        response = client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(admin_token),
            json={'agent_id': 99999})
        assert response.status_code == 404
    
    def test_assign_ticket_forbidden_customer(self, client, customer_token, ticket, agent):
        """Test customer cannot assign tickets."""
        response = client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(customer_token),
            json={'agent_id': agent.id})
        assert response.status_code == 403


class TestTicketStatus:
    """Tests for ticket status updates."""
    
    def test_update_status_success(self, client, agent_token, assigned_ticket):
        """Test updating ticket status."""
        response = client.put(f'/api/tickets/{assigned_ticket.id}/status',
            headers=auth_header(agent_token),
            json={'status': 'in_progress'})
        assert response.status_code == 200
        assert response.json['data']['status'] == 'in_progress'
    
    def test_update_status_invalid_transition(self, client, agent_token, ticket):
        """Test invalid status transition."""
        response = client.put(f'/api/tickets/{ticket.id}/status',
            headers=auth_header(agent_token),
            json={'status': 'resolved'})
        assert response.status_code == 400
    
    def test_update_status_customer_can_only_close(self, client, customer_token, ticket):
        """Test customer can only close tickets, not other status changes."""
        # Customer trying to set to in_progress should be forbidden
        response = client.put(f'/api/tickets/{ticket.id}/status',
            headers=auth_header(customer_token),
            json={'status': 'assigned'})
        assert response.status_code == 403


class TestTicketPriority:
    """Tests for ticket priority updates."""
    
    def test_update_priority_success(self, client, agent_token, ticket):
        """Test updating ticket priority with reason."""
        response = client.put(f'/api/tickets/{ticket.id}/priority',
            headers=auth_header(agent_token),
            json={
                'priority': 'urgent',
                'reason': 'Customer is a VIP and needs immediate attention'
            })
        assert response.status_code == 200
        assert response.json['data']['priority'] == 'urgent'
    
    def test_update_priority_missing_reason(self, client, agent_token, ticket):
        """Test priority update without reason fails."""
        response = client.put(f'/api/tickets/{ticket.id}/priority',
            headers=auth_header(agent_token),
            json={'priority': 'urgent'})
        assert response.status_code == 400
    
    def test_update_priority_forbidden_customer(self, client, customer_token, ticket):
        """Test customer cannot update priority."""
        response = client.put(f'/api/tickets/{ticket.id}/priority',
            headers=auth_header(customer_token),
            json={
                'priority': 'urgent',
                'reason': 'I want it urgent'
            })
        assert response.status_code == 403


class TestTicketHistory:
    """Tests for ticket history."""
    
    def test_get_history_success(self, client, customer_token, ticket):
        """Test getting ticket history."""
        response = client.get(f'/api/tickets/{ticket.id}/history',
            headers=auth_header(customer_token))
        assert response.status_code == 200
        assert 'status_changes' in response.json['data']
        assert 'assignments' in response.json['data']
        assert 'priority_changes' in response.json['data']


class TestTicketDelete:
    """Tests for ticket deletion."""
    
    def test_delete_ticket_admin(self, client, admin_token, ticket):
        """Test admin can delete ticket."""
        response = client.delete(f'/api/tickets/{ticket.id}',
            headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_delete_ticket_forbidden_agent(self, client, agent_token, ticket):
        """Test agent cannot delete ticket."""
        response = client.delete(f'/api/tickets/{ticket.id}',
            headers=auth_header(agent_token))
        assert response.status_code == 403
    
    def test_delete_ticket_forbidden_customer(self, client, customer_token, ticket):
        """Test customer cannot delete ticket."""
        response = client.delete(f'/api/tickets/{ticket.id}',
            headers=auth_header(customer_token))
        assert response.status_code == 403


class TestTicketExport:
    """Tests for ticket export."""
    
    def test_export_tickets_csv(self, client, agent_token, ticket):
        """Test exporting tickets to CSV."""
        response = client.get('/api/tickets/export',
            headers=auth_header(agent_token))
        assert response.status_code == 200
        assert response.content_type == 'text/csv; charset=utf-8'
    
    def test_export_tickets_forbidden_customer(self, client, customer_token):
        """Test customer cannot export tickets."""
        response = client.get('/api/tickets/export',
            headers=auth_header(customer_token))
        assert response.status_code == 403
