import pytest
from tests.conftest import auth_header


class TestCommentList:
    """Tests for listing comments."""
    
    def test_list_comments_customer(self, client, customer_token, ticket, comment):
        """Test customer can list comments on their ticket."""
        response = client.get(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token))
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert len(response.json['data']) >= 1
    
    def test_list_comments_agent(self, client, agent_token, ticket, comment):
        """Test agent can list comments."""
        response = client.get(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(agent_token))
        assert response.status_code == 200
    
    def test_list_comments_ticket_not_found(self, client, customer_token):
        """Test listing comments for non-existent ticket."""
        response = client.get('/api/tickets/99999/comments',
            headers=auth_header(customer_token))
        assert response.status_code == 404


class TestCommentCreate:
    """Tests for creating comments."""
    
    def test_create_comment_customer(self, client, customer_token, ticket):
        """Test customer can add comment to their ticket."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token),
            json={'content': 'This is a customer comment on the ticket'})
        assert response.status_code == 201
        assert response.json['data']['is_from_customer'] == True
        assert response.json['data']['is_internal'] == False
    
    def test_create_comment_agent(self, client, agent_token, ticket):
        """Test agent can add comment."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(agent_token),
            json={'content': 'This is an agent response to the ticket'})
        assert response.status_code == 201
        assert response.json['data']['is_from_customer'] == False
    
    def test_create_internal_comment_agent(self, client, agent_token, ticket):
        """Test agent can add internal comment."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(agent_token),
            json={
                'content': 'This is an internal note for agents only',
                'is_internal': True
            })
        assert response.status_code == 201
        assert response.json['data']['is_internal'] == True
    
    def test_create_internal_comment_forbidden_customer(self, client, customer_token, ticket):
        """Test customer cannot create internal comments."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token),
            json={
                'content': 'Trying to create internal note',
                'is_internal': True
            })
        assert response.status_code == 403
    
    def test_create_comment_empty_content(self, client, customer_token, ticket):
        """Test creating comment with empty content."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token),
            json={'content': ''})
        assert response.status_code == 400


class TestCommentUpdate:
    """Tests for updating comments."""
    
    def test_update_comment_author(self, client, customer_token, ticket, comment):
        """Test author can update their comment."""
        response = client.put(f'/api/tickets/{ticket.id}/comments/{comment.id}',
            headers=auth_header(customer_token),
            json={'content': 'Updated comment content here'})
        assert response.status_code == 200
        assert response.json['data']['content'] == 'Updated comment content here'
    
    def test_update_comment_admin(self, client, admin_token, ticket, comment):
        """Test admin can update any comment."""
        response = client.put(f'/api/tickets/{ticket.id}/comments/{comment.id}',
            headers=auth_header(admin_token),
            json={'content': 'Admin updated this comment'})
        assert response.status_code == 200
    
    def test_update_comment_not_found(self, client, customer_token, ticket):
        """Test updating non-existent comment."""
        response = client.put(f'/api/tickets/{ticket.id}/comments/99999',
            headers=auth_header(customer_token),
            json={'content': 'Updated content'})
        assert response.status_code == 404


class TestCommentDelete:
    """Tests for deleting comments."""
    
    def test_delete_comment_author(self, client, customer_token, ticket, comment):
        """Test author can delete their comment."""
        response = client.delete(f'/api/tickets/{ticket.id}/comments/{comment.id}',
            headers=auth_header(customer_token))
        assert response.status_code == 200
    
    def test_delete_comment_admin(self, client, admin_token, ticket, comment):
        """Test admin can delete any comment."""
        response = client.delete(f'/api/tickets/{ticket.id}/comments/{comment.id}',
            headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_delete_comment_forbidden(self, client, agent_token, ticket, comment):
        """Test non-author agent cannot delete comment."""
        response = client.delete(f'/api/tickets/{ticket.id}/comments/{comment.id}',
            headers=auth_header(agent_token))
        assert response.status_code == 403
    
    def test_delete_comment_not_found(self, client, customer_token, ticket):
        """Test deleting non-existent comment."""
        response = client.delete(f'/api/tickets/{ticket.id}/comments/99999',
            headers=auth_header(customer_token))
        assert response.status_code == 404
