import pytest
from tests.conftest import auth_header


class TestUserRegistration:
    """Tests for user registration."""
    
    def test_register_customer_success(self, client, app, _db):
        """Test successful customer registration."""
        response = client.post('/api/auth/register', json={
            'name': 'New Customer',
            'email': 'newcustomer@test.com',
            'password': 'SecurePass123'
        })
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert response.json['user']['email'] == 'newcustomer@test.com'
        assert response.json['user']['role'] == 'customer'
    
    def test_register_agent_success(self, client, app, _db):
        """Test successful agent registration."""
        response = client.post('/api/auth/register', json={
            'name': 'New Agent',
            'email': 'newagent@test.com',
            'password': 'SecurePass123',
            'role': 'agent'
        })
        assert response.status_code == 201
        assert response.json['user']['role'] == 'agent'
    
    def test_register_duplicate_email(self, client, customer):
        """Test registration with existing email."""
        response = client.post('/api/auth/register', json={
            'name': 'Another User',
            'email': 'customer@test.com',
            'password': 'SecurePass123'
        })
        assert response.status_code == 400
    
    def test_register_invalid_email(self, client, app, _db):
        """Test registration with invalid email."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'invalid-email',
            'password': 'SecurePass123'
        })
        assert response.status_code == 400
    
    def test_register_weak_password(self, client, app, _db):
        """Test registration with weak password."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@test.com',
            'password': 'weak'
        })
        assert response.status_code == 400
    
    def test_register_missing_fields(self, client, app, _db):
        """Test registration with missing fields."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User'
        })
        assert response.status_code == 400


class TestUserLogin:
    """Tests for user login."""
    
    def test_login_success(self, client, customer):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'customer@test.com',
            'password': 'TestPass123'
        })
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json
    
    def test_login_wrong_password(self, client, customer):
        """Test login with wrong password."""
        response = client.post('/api/auth/login', json={
            'email': 'customer@test.com',
            'password': 'WrongPassword'
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client, app, _db):
        """Test login with non-existent email."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'TestPass123'
        })
        assert response.status_code == 401


class TestCurrentUser:
    """Tests for getting current user."""
    
    def test_get_current_user(self, client, customer_token):
        """Test getting current user profile."""
        response = client.get('/api/auth/me', headers=auth_header(customer_token))
        assert response.status_code == 200
        assert response.json['user']['email'] == 'customer@test.com'
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401
