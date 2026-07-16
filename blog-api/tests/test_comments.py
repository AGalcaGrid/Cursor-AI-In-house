import pytest
from tests.conftest import auth_header


class TestGetComments:
    """Tests for getting comments."""
    
    def test_get_comments_empty(self, client, post):
        """Test getting comments when none exist."""
        response = client.get(f'/api/posts/{post.id}/comments')
        assert response.status_code == 200
        assert response.json['comments'] == []
    
    def test_get_comments_with_data(self, client, post, comment):
        """Test getting comments with data."""
        response = client.get(f'/api/posts/{post.id}/comments')
        assert response.status_code == 200
        assert len(response.json['comments']) == 1
        assert response.json['comments'][0]['content'] == 'This is a test comment'
    
    def test_get_comments_post_not_found(self, client, app, _db):
        """Test getting comments for non-existent post."""
        response = client.get('/api/posts/99999/comments')
        assert response.status_code == 404


class TestCreateComment:
    """Tests for creating comments."""
    
    def test_create_comment_success(self, client, auth_headers, post):
        """Test successful comment creation."""
        response = client.post(f'/api/posts/{post.id}/comments', 
            headers=auth_headers,
            json={'content': 'Great post! Thanks for sharing.'})
        assert response.status_code == 201
        assert response.json['comment']['content'] == 'Great post! Thanks for sharing.'
    
    def test_create_comment_unauthorized(self, client, post):
        """Test creating comment without auth."""
        response = client.post(f'/api/posts/{post.id}/comments',
            json={'content': 'Unauthorized comment'})
        assert response.status_code == 401
    
    def test_create_comment_post_not_found(self, client, auth_headers):
        """Test creating comment on non-existent post."""
        response = client.post('/api/posts/99999/comments',
            headers=auth_headers,
            json={'content': 'Comment on non-existent post'})
        assert response.status_code == 404
    
    def test_create_comment_empty_content(self, client, auth_headers, post):
        """Test creating comment with empty content."""
        response = client.post(f'/api/posts/{post.id}/comments',
            headers=auth_headers,
            json={'content': ''})
        assert response.status_code == 400
    
    def test_create_comment_missing_content(self, client, auth_headers, post):
        """Test creating comment without content field."""
        response = client.post(f'/api/posts/{post.id}/comments',
            headers=auth_headers,
            json={})
        assert response.status_code == 400


class TestDeleteComment:
    """Tests for deleting comments."""
    
    def test_delete_comment_success(self, client, auth_headers, post, comment):
        """Test successful comment deletion."""
        response = client.delete(f'/api/posts/{post.id}/comments/{comment.id}',
            headers=auth_headers)
        assert response.status_code == 200
    
    def test_delete_comment_unauthorized(self, client, post, comment):
        """Test deleting comment without auth."""
        response = client.delete(f'/api/posts/{post.id}/comments/{comment.id}')
        assert response.status_code == 401
    
    def test_delete_comment_forbidden(self, client, app, _db, post, comment):
        """Test deleting another user's comment."""
        from app.models.user import User
        
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        _db.session.add(other_user)
        _db.session.commit()
        
        login_response = client.post('/api/auth/login', json={
            'email': 'other@example.com',
            'password': 'password123'
        })
        other_token = login_response.json['access_token']
        
        response = client.delete(f'/api/posts/{post.id}/comments/{comment.id}',
            headers={'Authorization': f'Bearer {other_token}'})
        assert response.status_code == 403
    
    def test_delete_comment_not_found(self, client, auth_headers, post):
        """Test deleting non-existent comment."""
        response = client.delete(f'/api/posts/{post.id}/comments/99999',
            headers=auth_headers)
        assert response.status_code == 404
