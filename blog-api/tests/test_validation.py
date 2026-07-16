import pytest


class TestPostValidation:
    """Tests for post validation errors."""
    
    def test_create_post_empty_title(self, client, auth_headers):
        """Test creating post with empty title."""
        response = client.post('/api/posts', headers=auth_headers, json={
            'title': '',
            'content': 'Valid content here with enough text'
        })
        assert response.status_code == 400
    
    def test_create_post_short_content(self, client, auth_headers):
        """Test creating post with too short content."""
        response = client.post('/api/posts', headers=auth_headers, json={
            'title': 'Valid Title Here',
            'content': 'Short'
        })
        assert response.status_code == 400
    
    def test_create_post_missing_content(self, client, auth_headers):
        """Test creating post without content."""
        response = client.post('/api/posts', headers=auth_headers, json={
            'title': 'Valid Title Here'
        })
        assert response.status_code == 400
    
    def test_update_post_short_title(self, client, auth_headers, post):
        """Test updating post with too short title."""
        response = client.put(f'/api/posts/{post.id}', headers=auth_headers, json={
            'title': 'Hi'
        })
        assert response.status_code == 400
    
    def test_update_post_short_content(self, client, auth_headers, post):
        """Test updating post with too short content."""
        response = client.put(f'/api/posts/{post.id}', headers=auth_headers, json={
            'content': 'Short'
        })
        assert response.status_code == 400


class TestCommentValidation:
    """Tests for comment validation errors."""
    
    def test_create_comment_too_long(self, client, auth_headers, post):
        """Test creating comment with too long content."""
        response = client.post(f'/api/posts/{post.id}/comments',
            headers=auth_headers,
            json={'content': 'x' * 2001})
        assert response.status_code == 400


class TestAuthValidation:
    """Tests for authentication validation errors."""
    
    def test_register_short_username(self, client, app, _db):
        """Test registration with too short username."""
        response = client.post('/api/auth/register', json={
            'username': 'ab',
            'email': 'valid@email.com',
            'password': 'securepass123'
        })
        assert response.status_code == 400
    
    def test_register_long_username(self, client, app, _db):
        """Test registration with too long username."""
        response = client.post('/api/auth/register', json={
            'username': 'a' * 81,
            'email': 'valid@email.com',
            'password': 'securepass123'
        })
        assert response.status_code == 400
    
    def test_login_invalid_json(self, client, app, _db):
        """Test login with invalid JSON."""
        response = client.post('/api/auth/login',
            data='invalid json',
            content_type='application/json')
        assert response.status_code in [400, 500]
