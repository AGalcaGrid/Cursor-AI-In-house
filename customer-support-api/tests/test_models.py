import pytest
from datetime import datetime, timedelta
from app.models.ticket import Ticket, TicketStatusHistory, TicketAssignment, PriorityChangeHistory
from app.models.customer import Customer
from app.models.agent import Agent
from app.models.comment import Comment


class TestTicketModel:
    """Tests for Ticket model."""
    
    def test_generate_ticket_number(self):
        """Test ticket number generation format."""
        ticket_number = Ticket.generate_ticket_number()
        assert ticket_number.startswith('TICK-')
        assert len(ticket_number) == 18  # TICK-YYYYMMDD-XXXX
    
    def test_status_transitions_valid(self, db_session, customer):
        """Test valid status transitions."""
        ticket = Ticket(
            ticket_number=Ticket.generate_ticket_number(),
            subject='Test Ticket',
            description='Test description with enough characters',
            customer_id=customer.id
        )
        db_session.session.add(ticket)
        db_session.session.commit()
        
        # open -> assigned is valid
        assert ticket.can_transition_to('assigned') == True
        # open -> resolved is invalid
        assert ticket.can_transition_to('resolved') == False
    
    def test_status_transitions_same_status(self, db_session, customer):
        """Test transitioning to same status."""
        ticket = Ticket(
            ticket_number=Ticket.generate_ticket_number(),
            subject='Test Ticket',
            description='Test description with enough characters',
            customer_id=customer.id,
            status='open'
        )
        db_session.session.add(ticket)
        db_session.session.commit()
        
        assert ticket.can_transition_to('open') == True
    
    def test_reopen_within_7_days(self, db_session, customer):
        """Test reopening ticket within 7 days."""
        ticket = Ticket(
            ticket_number=Ticket.generate_ticket_number(),
            subject='Test Ticket',
            description='Test description with enough characters',
            customer_id=customer.id,
            status='closed',
            closed_at=datetime.utcnow() - timedelta(days=3)
        )
        db_session.session.add(ticket)
        db_session.session.commit()
        
        assert ticket.can_transition_to('reopened') == True
    
    def test_reopen_after_7_days(self, db_session, customer):
        """Test reopening ticket after 7 days fails."""
        ticket = Ticket(
            ticket_number=Ticket.generate_ticket_number(),
            subject='Test Ticket',
            description='Test description with enough characters',
            customer_id=customer.id,
            status='closed',
            closed_at=datetime.utcnow() - timedelta(days=10)
        )
        db_session.session.add(ticket)
        db_session.session.commit()
        
        assert ticket.can_transition_to('reopened') == False
    
    def test_calculate_sla_deadlines(self, db_session, customer):
        """Test SLA deadline calculation."""
        ticket = Ticket(
            ticket_number=Ticket.generate_ticket_number(),
            subject='Test Ticket',
            description='Test description with enough characters',
            customer_id=customer.id,
            priority='urgent',
            created_at=datetime.utcnow()
        )
        db_session.session.add(ticket)
        db_session.session.commit()
        
        ticket.calculate_sla_deadlines()
        
        # Urgent: 2 hours response, 24 hours resolution
        assert ticket.sla_response_due_at is not None
        assert ticket.sla_resolution_due_at is not None
        
        response_diff = (ticket.sla_response_due_at - ticket.created_at).total_seconds() / 3600
        assert abs(response_diff - 2) < 0.1  # Within 0.1 hours
    
    def test_check_sla_breach_response(self, db_session, customer):
        """Test SLA breach detection for response."""
        ticket = Ticket(
            ticket_number=Ticket.generate_ticket_number(),
            subject='Test Ticket',
            description='Test description with enough characters',
            customer_id=customer.id,
            priority='urgent',
            created_at=datetime.utcnow() - timedelta(hours=3),
            sla_response_due_at=datetime.utcnow() - timedelta(hours=1)
        )
        db_session.session.add(ticket)
        db_session.session.commit()
        
        ticket.check_sla_breach()
        assert ticket.sla_response_breached == True
    
    def test_update_status_with_history(self, db_session, customer):
        """Test status update creates history entry."""
        ticket = Ticket(
            ticket_number=Ticket.generate_ticket_number(),
            subject='Test Ticket',
            description='Test description with enough characters',
            customer_id=customer.id,
            status='open'
        )
        db_session.session.add(ticket)
        db_session.session.commit()
        
        result = ticket.update_status('assigned', customer.id)
        db_session.session.commit()
        
        assert result == True
        assert ticket.status == 'assigned'
        
        history = TicketStatusHistory.query.filter_by(ticket_id=ticket.id).first()
        assert history is not None
        assert history.old_status == 'open'
        assert history.new_status == 'assigned'


class TestCustomerModel:
    """Tests for Customer model."""
    
    def test_customer_creation(self, db_session):
        """Test customer creation."""
        customer = Customer(
            name='Test Customer',
            email='test@example.com',
            phone='1234567890',
            company='Test Co',
            role='customer'
        )
        customer.set_password('TestPass123')
        db_session.session.add(customer)
        db_session.session.commit()
        
        assert customer.id is not None
        assert customer.role == 'customer'
    
    def test_customer_password_hashing(self, db_session):
        """Test password is hashed."""
        customer = Customer(
            name='Test Customer',
            email='test2@example.com',
            role='customer'
        )
        customer.set_password('TestPass123')
        db_session.session.add(customer)
        db_session.session.commit()
        
        assert customer.password_hash != 'TestPass123'
        assert customer.check_password('TestPass123') == True
        assert customer.check_password('WrongPass') == False


class TestAgentModel:
    """Tests for Agent model."""
    
    def test_agent_creation(self, db_session):
        """Test agent creation."""
        agent = Agent(
            name='Test Agent',
            email='testagent@example.com',
            department='Support',
            max_tickets=10,
            role='agent'
        )
        agent.set_password('TestPass123')
        db_session.session.add(agent)
        db_session.session.commit()
        
        assert agent.id is not None
        assert agent.role == 'agent'
        assert agent.is_available == True
    
    def test_agent_can_accept_tickets(self, db_session, customer):
        """Test agent ticket capacity check."""
        agent = Agent(
            name='Test Agent',
            email='testagent2@example.com',
            department='Support',
            max_tickets=2,
            role='agent'
        )
        agent.set_password('TestPass123')
        db_session.session.add(agent)
        db_session.session.commit()
        
        # Initially can accept tickets
        assert agent.can_accept_tickets == True
        
        # Create tickets up to max
        for i in range(2):
            ticket = Ticket(
                ticket_number=Ticket.generate_ticket_number(),
                subject=f'Test Ticket {i}',
                description='Test description with enough characters',
                customer_id=customer.id,
                assigned_to_id=agent.id,
                status='assigned'
            )
            db_session.session.add(ticket)
        db_session.session.commit()
        
        # Now at capacity
        assert agent.can_accept_tickets == False


class TestCommentModel:
    """Tests for Comment model."""
    
    def test_comment_creation(self, db_session, ticket, customer):
        """Test comment creation."""
        comment = Comment(
            ticket_id=ticket.id,
            author_id=customer.id,
            content='This is a test comment',
            is_internal=False,
            is_from_customer=True
        )
        db_session.session.add(comment)
        db_session.session.commit()
        
        assert comment.id is not None
        assert comment.is_from_customer == True
    
    def test_internal_comment(self, db_session, ticket, agent):
        """Test internal comment creation."""
        comment = Comment(
            ticket_id=ticket.id,
            author_id=agent.id,
            content='Internal note for agents',
            is_internal=True,
            is_from_customer=False
        )
        db_session.session.add(comment)
        db_session.session.commit()
        
        assert comment.is_internal == True
