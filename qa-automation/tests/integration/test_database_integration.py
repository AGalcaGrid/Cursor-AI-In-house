import pytest
from datetime import datetime


class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    @pytest.fixture
    def db_session(self):
        """Create a database session for testing"""
        from app import create_app, db
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield db.session
            db.session.rollback()
            db.drop_all()
    
    def test_create_user(self, db_session):
        """Test creating a user in the database"""
        from app.models.user import User
        
        user = User(
            email='integration@test.com',
            name='Integration Test User'
        )
        user.set_password('testpassword123')
        
        db_session.add(user)
        db_session.commit()
        
        saved_user = User.query.filter_by(email='integration@test.com').first()
        assert saved_user is not None
        assert saved_user.name == 'Integration Test User'
    
    def test_create_ticket(self, db_session):
        """Test creating a ticket in the database"""
        from app.models.user import User
        from app.models.ticket import Ticket
        
        # Create user first
        user = User(email='ticket@test.com', name='Ticket User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Create ticket
        ticket = Ticket(
            title='Integration Test Ticket',
            description='Test description',
            priority='high',
            user_id=user.id
        )
        db_session.add(ticket)
        db_session.commit()
        
        saved_ticket = Ticket.query.filter_by(title='Integration Test Ticket').first()
        assert saved_ticket is not None
        assert saved_ticket.user_id == user.id
    
    def test_ticket_user_relationship(self, db_session):
        """Test ticket-user relationship"""
        from app.models.user import User
        from app.models.ticket import Ticket
        
        user = User(email='relation@test.com', name='Relation User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        ticket = Ticket(
            title='Relationship Test',
            description='Testing relationships',
            user_id=user.id
        )
        db_session.add(ticket)
        db_session.commit()
        
        # Test relationship
        assert ticket.user.email == 'relation@test.com'
        assert ticket in user.tickets
    
    def test_update_ticket_status(self, db_session):
        """Test updating ticket status"""
        from app.models.user import User
        from app.models.ticket import Ticket
        
        user = User(email='status@test.com', name='Status User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        ticket = Ticket(
            title='Status Test',
            description='Testing status update',
            status='open',
            user_id=user.id
        )
        db_session.add(ticket)
        db_session.commit()
        
        # Update status
        ticket.status = 'closed'
        ticket.closed_at = datetime.utcnow()
        db_session.commit()
        
        updated_ticket = Ticket.query.get(ticket.id)
        assert updated_ticket.status == 'closed'
        assert updated_ticket.closed_at is not None
    
    def test_delete_ticket(self, db_session):
        """Test deleting a ticket"""
        from app.models.user import User
        from app.models.ticket import Ticket
        
        user = User(email='delete@test.com', name='Delete User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        ticket = Ticket(
            title='Delete Test',
            description='Testing deletion',
            user_id=user.id
        )
        db_session.add(ticket)
        db_session.commit()
        
        ticket_id = ticket.id
        db_session.delete(ticket)
        db_session.commit()
        
        deleted_ticket = Ticket.query.get(ticket_id)
        assert deleted_ticket is None
    
    def test_cascade_delete_user_tickets(self, db_session):
        """Test that deleting a user cascades to tickets"""
        from app.models.user import User
        from app.models.ticket import Ticket
        
        user = User(email='cascade@test.com', name='Cascade User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        ticket1 = Ticket(title='Cascade 1', description='Test', user_id=user.id)
        ticket2 = Ticket(title='Cascade 2', description='Test', user_id=user.id)
        db_session.add_all([ticket1, ticket2])
        db_session.commit()
        
        user_id = user.id
        db_session.delete(user)
        db_session.commit()
        
        orphan_tickets = Ticket.query.filter_by(user_id=user_id).all()
        assert len(orphan_tickets) == 0


class TestAPIIntegration:
    """Integration tests for API with database"""
    
    @pytest.fixture
    def client(self):
        """Create test client with database"""
        from app import create_app, db
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            with app.test_client() as client:
                yield client
            db.drop_all()
    
    def test_full_ticket_lifecycle(self, client):
        """Test complete ticket lifecycle through API"""
        # Register user
        register_response = client.post('/api/auth/register', json={
            'email': 'lifecycle@test.com',
            'password': 'password123',
            'name': 'Lifecycle User'
        })
        assert register_response.status_code in [200, 201]
        
        # Login
        login_response = client.post('/api/auth/login', json={
            'email': 'lifecycle@test.com',
            'password': 'password123'
        })
        assert login_response.status_code == 200
        token = login_response.json.get('token')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create ticket
        create_response = client.post('/api/tickets', json={
            'title': 'Lifecycle Ticket',
            'description': 'Testing full lifecycle',
            'priority': 'medium'
        }, headers=headers)
        assert create_response.status_code == 201
        ticket_id = create_response.json.get('id') or create_response.json.get('ticket', {}).get('id')
        
        # Get ticket
        get_response = client.get(f'/api/tickets/{ticket_id}', headers=headers)
        assert get_response.status_code == 200
        
        # Update ticket
        update_response = client.put(f'/api/tickets/{ticket_id}', json={
            'status': 'in_progress'
        }, headers=headers)
        assert update_response.status_code == 200
        
        # Delete ticket
        delete_response = client.delete(f'/api/tickets/{ticket_id}', headers=headers)
        assert delete_response.status_code in [200, 204]
        
        # Verify deletion
        verify_response = client.get(f'/api/tickets/{ticket_id}', headers=headers)
        assert verify_response.status_code == 404
