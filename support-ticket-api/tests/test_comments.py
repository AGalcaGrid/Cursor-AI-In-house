import pytest
from tests.conftest import auth_header


class TestCommentCreation:
    """Tests for comment creation (FR-015, FR-016)."""
    
    def test_customer_can_add_comment(self, client, customer_token, ticket):
        """Test customer can add comment to their ticket."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token),
            json={'content': 'Thank you for looking into this issue.'})
        assert response.status_code == 201
        assert response.json['comment']['is_internal'] == False
    
    def test_agent_can_add_comment(self, client, agent_token, assigned_ticket):
        """Test agent can add comment to assigned ticket."""
        response = client.post(f'/api/tickets/{assigned_ticket.id}/comments',
            headers=auth_header(agent_token),
            json={'content': 'I am looking into this issue now.'})
        assert response.status_code == 201
    
    def test_agent_can_add_internal_comment(self, client, agent_token, assigned_ticket):
        """Test agent can add internal comment (FR-016)."""
        response = client.post(f'/api/tickets/{assigned_ticket.id}/comments',
            headers=auth_header(agent_token),
            json={'content': 'Internal note: Check database logs.', 'is_internal': True})
        assert response.status_code == 201
        assert response.json['comment']['is_internal'] == True
    
    def test_customer_cannot_add_internal_comment(self, client, customer_token, ticket):
        """Test customer cannot add internal comment (FR-016)."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token),
            json={'content': 'Trying to be internal', 'is_internal': True})
        assert response.status_code == 403
    
    def test_comment_empty_content(self, client, customer_token, ticket):
        """Test comment with empty content."""
        response = client.post(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token),
            json={'content': ''})
        assert response.status_code == 400


class TestCommentRetrieval:
    """Tests for comment retrieval (FR-016)."""
    
    def test_get_comments(self, client, customer_token, ticket, comment):
        """Test getting comments for a ticket."""
        response = client.get(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token))
        assert response.status_code == 200
        assert len(response.json['comments']) >= 1
    
    def test_customer_cannot_see_internal_comments(self, client, app, _db, customer_token, ticket, agent):
        """Test customer cannot see internal comments (FR-016)."""
        from app.models.comment import Comment
        
        # Add internal comment
        internal_comment = Comment(
            ticket_id=ticket.id,
            user_id=agent.id,
            content='Internal note not visible to customer',
            is_internal=True
        )
        _db.session.add(internal_comment)
        _db.session.commit()
        
        response = client.get(f'/api/tickets/{ticket.id}/comments',
            headers=auth_header(customer_token))
        
        # Customer should not see internal comments
        for comment in response.json['comments']:
            assert comment['is_internal'] == False
    
    def test_agent_can_see_internal_comments(self, client, app, _db, agent_token, assigned_ticket, agent):
        """Test agent can see internal comments (FR-016)."""
        from app.models.comment import Comment
        
        internal_comment = Comment(
            ticket_id=assigned_ticket.id,
            user_id=agent.id,
            content='Internal note visible to agent',
            is_internal=True
        )
        _db.session.add(internal_comment)
        _db.session.commit()
        
        response = client.get(f'/api/tickets/{assigned_ticket.id}/comments',
            headers=auth_header(agent_token))
        
        internal_found = any(c['is_internal'] for c in response.json['comments'])
        assert internal_found == True


class TestCommentDeletion:
    """Tests for comment deletion."""
    
    def test_admin_can_delete_comment(self, client, admin_token, ticket, comment):
        """Test admin can delete comment."""
        response = client.delete(f'/api/tickets/{ticket.id}/comments/{comment.id}',
            headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_customer_cannot_delete_comment(self, client, customer_token, ticket, comment):
        """Test customer cannot delete comment."""
        response = client.delete(f'/api/tickets/{ticket.id}/comments/{comment.id}',
            headers=auth_header(customer_token))
        assert response.status_code == 403
