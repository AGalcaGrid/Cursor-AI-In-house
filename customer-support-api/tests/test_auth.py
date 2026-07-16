import pytest
from tests.conftest import auth_header


class TestAuthRegister:
    """Tests for user registration."""
    
    def test_register_customer_success(self, client, db_session):
        """Test successful customer registration."""
        response = client.post('/api/auth/register', json={
            'name': 'New Customer',
            'email': 'newcustomer@test.com',
            'password': 'SecurePass123'
        })
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert response.json['data']['email'] == 'newcustomer@test.com'
    
    def test_register_invalid_email(self, client, db_session):
        """Test registration with invalid email."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'invalid-email',
            'password': 'SecurePass123'
        })
        assert response.status_code == 400
    
    def test_register_weak_password(self, client, db_session):
        """Test registration with weak password."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': '123'
        })
        assert response.status_code == 400
    
    def test_register_duplicate_email(self, client, customer):
        """Test registration with existing email."""
        response = client.post('/api/auth/register', json={
            'name': 'Another User',
            'email': 'customer@test.com',
            'password': 'SecurePass123'
        })
        assert response.status_code == 409
    
    def test_register_missing_fields(self, client, db_session):
        """Test registration with missing required fields."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User'
        })
        assert response.status_code == 400


class TestAuthLogin:
    """Tests for user login."""
    
    def test_login_success(self, client, customer):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'customer@test.com',
            'password': 'TestPass123'
        })
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert 'access_token' in response.json['data']
        assert 'refresh_token' in response.json['data']
    
    def test_login_invalid_email(self, client, db_session):
        """Test login with non-existent email."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'TestPass123'
        })
        assert response.status_code == 401
    
    def test_login_wrong_password(self, client, customer):
        """Test login with wrong password."""
        response = client.post('/api/auth/login', json={
            'email': 'customer@test.com',
            'password': 'WrongPassword'
        })
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client, db_session):
        """Test login with missing fields."""
        response = client.post('/api/auth/login', json={
            'email': 'customer@test.com'
        })
        assert response.status_code == 400


class TestAuthProfile:
    """Tests for user profile."""
    
    def test_get_profile_success(self, client, customer_token):
        """Test getting user profile."""
        response = client.get('/api/auth/me', headers=auth_header(customer_token))
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert response.json['data']['email'] == 'customer@test.com'
    
    def test_get_profile_unauthorized(self, client):
        """Test getting profile without token."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401


class TestAuthRefresh:
    """Tests for token refresh."""
    
    def test_refresh_token_success(self, client, customer):
        """Test refreshing access token."""
        # First login to get refresh token
        login_response = client.post('/api/auth/login', json={
            'email': 'customer@test.com',
            'password': 'TestPass123'
        })
        refresh_token = login_response.json['data']['refresh_token']
        
        # Use refresh token to get new access token
        response = client.post('/api/auth/refresh', 
            headers={'Authorization': f'Bearer {refresh_token}'})
        assert response.status_code == 200
        assert 'access_token' in response.json['data']
