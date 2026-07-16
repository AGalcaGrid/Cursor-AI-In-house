import pytest
from datetime import datetime


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    from app import create_app, db as _db
    
    _app = create_app('testing')
    _app.config['TESTING'] = True
    _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    _app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    _app.config['WTF_CSRF_ENABLED'] = False
    
    with _app.app_context():
        _db.create_all()
        yield _app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def _db(app):
    """Get database instance."""
    from app import db
    return db


@pytest.fixture
def customer(app, _db):
    """Create a test customer."""
    from app.models.customer import Customer
    
    customer = Customer(
        name='Test Customer',
        email='customer@test.com',
        phone='1234567890',
        company='Test Company',
        role='customer'
    )
    customer.set_password('TestPass123')
    _db.session.add(customer)
    _db.session.commit()
    return customer


@pytest.fixture
def agent(app, _db):
    """Create a test agent."""
    from app.models.agent import Agent
    
    agent = Agent(
        name='Test Agent',
        email='agent@test.com',
        department='Technical Support',
        max_tickets=10,
        role='agent'
    )
    agent.set_password('TestPass123')
    _db.session.add(agent)
    _db.session.commit()
    return agent


@pytest.fixture
def admin(app, _db):
    """Create a test admin."""
    from app.models.agent import Admin
    
    admin = Admin(
        name='Test Admin',
        email='admin@test.com',
        role='admin'
    )
    admin.set_password('TestPass123')
    _db.session.add(admin)
    _db.session.commit()
    return admin


@pytest.fixture
def ticket(app, _db, customer):
    """Create a test ticket."""
    from app.models.ticket import Ticket
    from datetime import datetime
    
    ticket = Ticket(
        ticket_number=Ticket.generate_ticket_number(),
        subject='Test Ticket Subject',
        description='This is a test ticket description with enough characters',
        status='open',
        priority='medium',
        category='technical',
        customer_id=customer.id,
        created_at=datetime.utcnow()
    )
    _db.session.add(ticket)
    _db.session.flush()
    ticket.calculate_sla_deadlines()
    _db.session.commit()
    return ticket


@pytest.fixture
def assigned_ticket(app, _db, customer, agent):
    """Create a test ticket assigned to an agent."""
    from app.models.ticket import Ticket
    from datetime import datetime
    
    ticket = Ticket(
        ticket_number=Ticket.generate_ticket_number(),
        subject='Assigned Ticket Subject',
        description='This is an assigned test ticket description',
        status='assigned',
        priority='high',
        category='billing',
        customer_id=customer.id,
        assigned_to_id=agent.id,
        created_at=datetime.utcnow()
    )
    _db.session.add(ticket)
    _db.session.flush()
    ticket.calculate_sla_deadlines()
    _db.session.commit()
    return ticket


@pytest.fixture
def comment(app, _db, ticket, customer):
    """Create a test comment."""
    from app.models.comment import Comment
    
    comment = Comment(
        ticket_id=ticket.id,
        author_id=customer.id,
        content='This is a test comment',
        is_internal=False,
        is_from_customer=True
    )
    _db.session.add(comment)
    _db.session.commit()
    return comment


@pytest.fixture
def customer_token(client, customer):
    """Get JWT token for customer."""
    response = client.post('/api/auth/login', json={
        'email': 'customer@test.com',
        'password': 'TestPass123'
    })
    return response.json['data']['access_token']


@pytest.fixture
def agent_token(client, agent):
    """Get JWT token for agent."""
    response = client.post('/api/auth/login', json={
        'email': 'agent@test.com',
        'password': 'TestPass123'
    })
    return response.json['data']['access_token']


@pytest.fixture
def admin_token(client, admin):
    """Get JWT token for admin."""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'TestPass123'
    })
    return response.json['data']['access_token']


# Alias for backward compatibility with tests using db_session
@pytest.fixture
def db_session(app, _db):
    """Alias for _db fixture."""
    return _db


@pytest.fixture
def auth_headers(client, app, _db):
    """
    Register and login a test user, return auth headers.
    Matches the pattern from user's example.
    """
    from app.models.customer import Customer
    
    # Create test user
    user = Customer(
        name='testuser',
        email='test@example.com',
        role='customer'
    )
    user.set_password('password123')
    _db.session.add(user)
    _db.session.commit()
    
    # Login to get token
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


def auth_header(token):
    """Helper to create authorization header."""
    return {'Authorization': f'Bearer {token}'}
