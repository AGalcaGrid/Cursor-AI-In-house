import pytest
from tests.conftest import auth_header


class TestUserRegistration:
    """Tests for user registration."""
    
    def test_register_success(self, client, app, _db):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123'
        })
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert 'user' in response.json
        assert response.json['user']['username'] == 'newuser'
    
    def test_register_duplicate_username(self, client, user):
        """Test registration with existing username."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'securepass123'
        })
        assert response.status_code == 400
    
    def test_register_duplicate_email(self, client, user):
        """Test registration with existing email."""
        response = client.post('/api/auth/register', json={
            'username': 'anotheruser',
            'email': 'test@example.com',
            'password': 'securepass123'
        })
        assert response.status_code == 400
    
    def test_register_invalid_email(self, client, app, _db):
        """Test registration with invalid email."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'securepass123'
        })
        assert response.status_code == 400
    
    def test_register_short_password(self, client, app, _db):
        """Test registration with short password."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '123'
        })
        assert response.status_code == 400
    
    def test_register_missing_fields(self, client, app, _db):
        """Test registration with missing fields."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser'
        })
        assert response.status_code == 400


class TestUserLogin:
    """Tests for user login."""
    
    def test_login_success(self, client, user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json
    
    def test_login_wrong_password(self, client, user):
        """Test login with wrong password."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client, app, _db):
        """Test login with non-existent email."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client, app, _db):
        """Test login with missing fields."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com'
        })
        assert response.status_code == 400


class TestCurrentUser:
    """Tests for getting current user."""
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user profile."""
        response = client.get('/api/auth/me', headers=auth_headers)
        assert response.status_code == 200
        assert response.json['user']['username'] == 'testuser'
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401
