import pytest
from tests.conftest import auth_header


class TestTicketCreation:
    """Tests for ticket creation (FR-001, FR-002, FR-004)."""
    
    def test_create_ticket_success(self, client, customer_token):
        """Test successful ticket creation."""
        response = client.post('/api/tickets', headers=auth_header(customer_token), json={
            'subject': 'Cannot login to my account',
            'description': 'I have been trying to login but getting an error message every time.',
            'priority': 'high',
            'category': 'technical',
            'customer_email': 'customer@test.com'
        })
        assert response.status_code == 201
        assert response.json['ticket']['status'] == 'open'
        assert response.json['ticket']['ticket_number'].startswith('TICK-')
    
    def test_create_ticket_auto_generates_number(self, client, customer_token):
        """Test ticket number auto-generation (FR-002)."""
        response = client.post('/api/tickets', headers=auth_header(customer_token), json={
            'subject': 'Test ticket for number generation',
            'description': 'This ticket tests the auto-generation of ticket numbers.',
            'customer_email': 'customer@test.com'
        })
        assert response.status_code == 201
        ticket_number = response.json['ticket']['ticket_number']
        assert ticket_number.startswith('TICK-')
        assert len(ticket_number.split('-')) == 3
    
    def test_create_ticket_default_status_open(self, client, customer_token):
        """Test ticket default status is open (FR-004)."""
        response = client.post('/api/tickets', headers=auth_header(customer_token), json={
            'subject': 'Test default status',
            'description': 'This ticket should have open status by default.',
            'customer_email': 'customer@test.com'
        })
        assert response.status_code == 201
        assert response.json['ticket']['status'] == 'open'
    
    def test_create_ticket_short_subject(self, client, customer_token):
        """Test validation: subject too short."""
        response = client.post('/api/tickets', headers=auth_header(customer_token), json={
            'subject': 'Hi',
            'description': 'This is a valid description with enough characters.',
            'customer_email': 'customer@test.com'
        })
        assert response.status_code == 400
    
    def test_create_ticket_short_description(self, client, customer_token):
        """Test validation: description too short."""
        response = client.post('/api/tickets', headers=auth_header(customer_token), json={
            'subject': 'Valid subject here',
            'description': 'Too short',
            'customer_email': 'customer@test.com'
        })
        assert response.status_code == 400
    
    def test_create_ticket_invalid_priority(self, client, customer_token):
        """Test validation: invalid priority."""
        response = client.post('/api/tickets', headers=auth_header(customer_token), json={
            'subject': 'Valid subject here',
            'description': 'This is a valid description with enough characters.',
            'priority': 'super_urgent',
            'customer_email': 'customer@test.com'
        })
        assert response.status_code == 400
    
    def test_create_ticket_invalid_category(self, client, customer_token):
        """Test validation: invalid category."""
        response = client.post('/api/tickets', headers=auth_header(customer_token), json={
            'subject': 'Valid subject here',
            'description': 'This is a valid description with enough characters.',
            'category': 'invalid_category',
            'customer_email': 'customer@test.com'
        })
        assert response.status_code == 400


class TestTicketRetrieval:
    """Tests for ticket retrieval."""
    
    def test_get_tickets_customer(self, client, customer_token, ticket):
        """Test customer can only see own tickets."""
        response = client.get('/api/tickets', headers=auth_header(customer_token))
        assert response.status_code == 200
        assert len(response.json['tickets']) >= 1
    
    def test_get_tickets_agent(self, client, agent_token, assigned_ticket):
        """Test agent can see assigned tickets."""
        response = client.get('/api/tickets', headers=auth_header(agent_token))
        assert response.status_code == 200
    
    def test_get_tickets_admin(self, client, admin_token, ticket):
        """Test admin can see all tickets."""
        response = client.get('/api/tickets', headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_get_single_ticket(self, client, customer_token, ticket):
        """Test getting single ticket."""
        response = client.get(f'/api/tickets/{ticket.id}', headers=auth_header(customer_token))
        assert response.status_code == 200
        assert response.json['ticket']['id'] == ticket.id
    
    def test_get_ticket_not_found(self, client, customer_token):
        """Test getting non-existent ticket."""
        response = client.get('/api/tickets/99999', headers=auth_header(customer_token))
        assert response.status_code == 404


class TestTicketStatusTransitions:
    """Tests for status transitions (FR-011, FR-012)."""
    
    def test_status_open_to_assigned(self, client, admin_token, ticket, agent):
        """Test transition from open to assigned."""
        # Assign ticket first
        client.post(f'/api/tickets/{ticket.id}/assign', 
            headers=auth_header(admin_token),
            json={'agent_id': agent.id})
        
        response = client.get(f'/api/tickets/{ticket.id}', headers=auth_header(admin_token))
        assert response.json['ticket']['status'] == 'assigned'
    
    def test_status_assigned_to_in_progress(self, client, agent_token, assigned_ticket):
        """Test transition from assigned to in_progress."""
        response = client.put(f'/api/tickets/{assigned_ticket.id}/status',
            headers=auth_header(agent_token),
            json={'status': 'in_progress'})
        assert response.status_code == 200
        assert response.json['ticket']['status'] == 'in_progress'
    
    def test_status_invalid_transition(self, client, agent_token, assigned_ticket):
        """Test invalid status transition."""
        response = client.put(f'/api/tickets/{assigned_ticket.id}/status',
            headers=auth_header(agent_token),
            json={'status': 'resolved'})
        assert response.status_code == 400
    
    def test_customer_can_close_ticket(self, client, customer_token, app, _db, customer):
        """Test customer can close their ticket."""
        from app.models.ticket import Ticket
        
        # Create ticket in resolved state
        ticket = Ticket(
            ticket_number=Ticket.generate_ticket_number(),
            subject='Ticket to close',
            description='This ticket will be closed by customer.',
            status='resolved',
            customer_email=customer.email
        )
        _db.session.add(ticket)
        _db.session.commit()
        
        response = client.put(f'/api/tickets/{ticket.id}/status',
            headers=auth_header(customer_token),
            json={'status': 'closed'})
        assert response.status_code == 200


class TestTicketAssignment:
    """Tests for ticket assignment (FR-005, FR-008, FR-010)."""
    
    def test_admin_can_assign_ticket(self, client, admin_token, ticket, agent):
        """Test admin can assign ticket (FR-005)."""
        response = client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(admin_token),
            json={'agent_id': agent.id})
        assert response.status_code == 200
        assert response.json['ticket']['assigned_to_id'] == agent.id
    
    def test_assignment_changes_status(self, client, admin_token, ticket, agent):
        """Test assignment changes status to assigned (FR-008)."""
        response = client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(admin_token),
            json={'agent_id': agent.id})
        assert response.status_code == 200
        assert response.json['ticket']['status'] == 'assigned'
    
    def test_assignment_history_tracked(self, client, admin_token, ticket, agent):
        """Test assignment history is tracked (FR-010)."""
        client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(admin_token),
            json={'agent_id': agent.id})
        
        response = client.get(f'/api/tickets/{ticket.id}/history',
            headers=auth_header(admin_token))
        assert response.status_code == 200
        assert len(response.json['history']) >= 1
    
    def test_customer_cannot_assign(self, client, customer_token, ticket, agent):
        """Test customer cannot assign tickets."""
        response = client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(customer_token),
            json={'agent_id': agent.id})
        assert response.status_code == 403
    
    def test_assign_to_nonexistent_agent(self, client, admin_token, ticket):
        """Test assigning to non-existent agent."""
        response = client.post(f'/api/tickets/{ticket.id}/assign',
            headers=auth_header(admin_token),
            json={'agent_id': 99999})
        assert response.status_code == 404


class TestTicketPriority:
    """Tests for priority management (FR-023, FR-024)."""
    
    def test_agent_can_change_priority(self, client, agent_token, assigned_ticket):
        """Test agent can change priority (FR-023)."""
        response = client.put(f'/api/tickets/{assigned_ticket.id}/priority',
            headers=auth_header(agent_token),
            json={'priority': 'urgent', 'reason': 'Customer is VIP'})
        assert response.status_code == 200
        assert response.json['ticket']['priority'] == 'urgent'
    
    def test_priority_change_requires_reason(self, client, agent_token, assigned_ticket):
        """Test priority change requires reason (FR-024)."""
        response = client.put(f'/api/tickets/{assigned_ticket.id}/priority',
            headers=auth_header(agent_token),
            json={'priority': 'urgent'})
        assert response.status_code == 400
    
    def test_customer_cannot_change_priority(self, client, customer_token, ticket):
        """Test customer cannot change priority."""
        response = client.put(f'/api/tickets/{ticket.id}/priority',
            headers=auth_header(customer_token),
            json={'priority': 'urgent', 'reason': 'I want it urgent'})
        assert response.status_code == 403


class TestTicketDeletion:
    """Tests for ticket deletion."""
    
    def test_admin_can_delete_ticket(self, client, admin_token, ticket):
        """Test admin can delete ticket."""
        response = client.delete(f'/api/tickets/{ticket.id}',
            headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_customer_cannot_delete_ticket(self, client, customer_token, ticket):
        """Test customer cannot delete ticket."""
        response = client.delete(f'/api/tickets/{ticket.id}',
            headers=auth_header(customer_token))
        assert response.status_code == 403
    
    def test_agent_cannot_delete_ticket(self, client, agent_token, assigned_ticket):
        """Test agent cannot delete ticket."""
        response = client.delete(f'/api/tickets/{assigned_ticket.id}',
            headers=auth_header(agent_token))
        assert response.status_code == 403
