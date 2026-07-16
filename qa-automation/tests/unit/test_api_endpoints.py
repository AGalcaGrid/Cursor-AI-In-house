import pytest
import json
from unittest.mock import Mock, patch


class TestAuthEndpoints:
    """Unit tests for authentication endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app import create_app
        app = create_app('testing')
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        token = response.json.get('token')
        return {'Authorization': f'Bearer {token}'}
    
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert 'token' in response.json
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert 'error' in response.json
    
    def test_login_missing_email(self, client):
        """Test login without email"""
        response = client.post('/api/auth/login', json={
            'password': 'password123'
        })
        
        assert response.status_code == 400
    
    def test_login_missing_password(self, client):
        """Test login without password"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
    
    def test_register_success(self, client):
        """Test successful registration"""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'name': 'New User'
        })
        
        assert response.status_code == 201
        assert 'user' in response.json or 'id' in response.json
    
    def test_register_duplicate_email(self, client):
        """Test registration with existing email"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User'
        })
        
        assert response.status_code == 409 or response.status_code == 400


class TestTicketEndpoints:
    """Unit tests for ticket endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app import create_app
        app = create_app('testing')
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        token = response.json.get('token')
        return {'Authorization': f'Bearer {token}'}
    
    def test_get_tickets(self, client, auth_headers):
        """Test getting all tickets"""
        response = client.get('/api/tickets', headers=auth_headers)
        
        assert response.status_code == 200
        assert isinstance(response.json, list) or 'tickets' in response.json
    
    def test_get_tickets_unauthorized(self, client):
        """Test getting tickets without authentication"""
        response = client.get('/api/tickets')
        
        assert response.status_code == 401
    
    def test_create_ticket(self, client, auth_headers):
        """Test creating a ticket"""
        response = client.post('/api/tickets', json={
            'title': 'Test Ticket',
            'description': 'Test description',
            'priority': 'high'
        }, headers=auth_headers)
        
        assert response.status_code == 201
        assert 'id' in response.json or 'ticket' in response.json
    
    def test_create_ticket_missing_title(self, client, auth_headers):
        """Test creating ticket without title"""
        response = client.post('/api/tickets', json={
            'description': 'Test description'
        }, headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_get_single_ticket(self, client, auth_headers):
        """Test getting a single ticket"""
        # First create a ticket
        create_response = client.post('/api/tickets', json={
            'title': 'Test Ticket',
            'description': 'Test description'
        }, headers=auth_headers)
        
        ticket_id = create_response.json.get('id') or create_response.json.get('ticket', {}).get('id')
        
        response = client.get(f'/api/tickets/{ticket_id}', headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_update_ticket(self, client, auth_headers):
        """Test updating a ticket"""
        # First create a ticket
        create_response = client.post('/api/tickets', json={
            'title': 'Test Ticket',
            'description': 'Test description'
        }, headers=auth_headers)
        
        ticket_id = create_response.json.get('id') or create_response.json.get('ticket', {}).get('id')
        
        response = client.put(f'/api/tickets/{ticket_id}', json={
            'title': 'Updated Title'
        }, headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_delete_ticket(self, client, auth_headers):
        """Test deleting a ticket"""
        # First create a ticket
        create_response = client.post('/api/tickets', json={
            'title': 'Test Ticket',
            'description': 'Test description'
        }, headers=auth_headers)
        
        ticket_id = create_response.json.get('id') or create_response.json.get('ticket', {}).get('id')
        
        response = client.delete(f'/api/tickets/{ticket_id}', headers=auth_headers)
        
        assert response.status_code == 200 or response.status_code == 204
    
    def test_get_nonexistent_ticket(self, client, auth_headers):
        """Test getting a ticket that doesn't exist"""
        response = client.get('/api/tickets/99999', headers=auth_headers)
        
        assert response.status_code == 404
