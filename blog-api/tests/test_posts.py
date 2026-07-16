import pytest
from tests.conftest import auth_header


class TestGetPosts:
    """Tests for getting posts."""
    
    def test_get_posts_empty(self, client, app, _db):
        """Test getting posts when none exist."""
        response = client.get('/api/posts')
        assert response.status_code == 200
        assert response.json['posts'] == []
    
    def test_get_posts_with_data(self, client, post):
        """Test getting posts with data."""
        response = client.get('/api/posts')
        assert response.status_code == 200
        assert len(response.json['posts']) == 1
        assert response.json['posts'][0]['title'] == 'Test Post Title'
    
    def test_get_posts_pagination(self, client, app, _db, user, category):
        """Test posts pagination."""
        from app.models.post import Post
        
        # Create multiple posts
        for i in range(25):
            post = Post(
                title=f'Post {i}',
                slug=f'post-{i}',
                content='Content for testing pagination',
                author_id=user.id,
                category_id=category.id
            )
            _db.session.add(post)
        _db.session.commit()
        
        response = client.get('/api/posts?page=1&per_page=20')
        assert response.status_code == 200
        assert len(response.json['posts']) == 20
        assert response.json['pagination']['total'] == 25
        assert response.json['pagination']['pages'] == 2
    
    def test_get_posts_filter_by_category(self, client, post, category):
        """Test filtering posts by category."""
        response = client.get(f'/api/posts?category={category.slug}')
        assert response.status_code == 200
        assert len(response.json['posts']) == 1


class TestCreatePost:
    """Tests for creating posts."""
    
    def test_create_post_success(self, client, auth_headers, category):
        """Test successful post creation."""
        response = client.post('/api/posts', headers=auth_headers, json={
            'title': 'My New Blog Post',
            'content': 'This is the content of my new blog post with enough text.',
            'category_id': category.id
        })
        assert response.status_code == 201
        assert response.json['post']['title'] == 'My New Blog Post'
        assert response.json['post']['slug'] == 'my-new-blog-post'
    
    def test_create_post_without_category(self, client, auth_headers):
        """Test creating post without category."""
        response = client.post('/api/posts', headers=auth_headers, json={
            'title': 'Post Without Category',
            'content': 'This is a post without a category assigned.'
        })
        assert response.status_code == 201
        assert response.json['post']['category_id'] is None
    
    def test_create_post_unauthorized(self, client):
        """Test creating post without auth."""
        response = client.post('/api/posts', json={
            'title': 'Unauthorized Post',
            'content': 'This should fail because no auth.'
        })
        assert response.status_code == 401
    
    def test_create_post_missing_title(self, client, auth_headers):
        """Test creating post without title."""
        response = client.post('/api/posts', headers=auth_headers, json={
            'content': 'Content without title'
        })
        assert response.status_code == 400
    
    def test_create_post_short_title(self, client, auth_headers):
        """Test creating post with short title."""
        response = client.post('/api/posts', headers=auth_headers, json={
            'title': 'Hi',
            'content': 'Content with short title'
        })
        assert response.status_code == 400
    
    def test_create_post_invalid_category(self, client, auth_headers):
        """Test creating post with invalid category."""
        response = client.post('/api/posts', headers=auth_headers, json={
            'title': 'Post with Invalid Category',
            'content': 'This post has an invalid category ID.',
            'category_id': 99999
        })
        assert response.status_code == 404


class TestGetSinglePost:
    """Tests for getting a single post."""
    
    def test_get_post_success(self, client, post):
        """Test getting a single post."""
        response = client.get(f'/api/posts/{post.id}')
        assert response.status_code == 200
        assert response.json['post']['title'] == 'Test Post Title'
    
    def test_get_post_not_found(self, client, app, _db):
        """Test getting non-existent post."""
        response = client.get('/api/posts/99999')
        assert response.status_code == 404


class TestUpdatePost:
    """Tests for updating posts."""
    
    def test_update_post_success(self, client, auth_headers, post):
        """Test successful post update."""
        response = client.put(f'/api/posts/{post.id}', headers=auth_headers, json={
            'title': 'Updated Post Title',
            'content': 'This is the updated content of the post.'
        })
        assert response.status_code == 200
        assert response.json['post']['title'] == 'Updated Post Title'
    
    def test_update_post_unauthorized(self, client, post):
        """Test updating post without auth."""
        response = client.put(f'/api/posts/{post.id}', json={
            'title': 'Unauthorized Update'
        })
        assert response.status_code == 401
    
    def test_update_post_forbidden(self, client, app, _db, post):
        """Test updating another user's post."""
        from app.models.user import User
        
        # Create another user
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        _db.session.add(other_user)
        _db.session.commit()
        
        # Login as other user
        login_response = client.post('/api/auth/login', json={
            'email': 'other@example.com',
            'password': 'password123'
        })
        other_token = login_response.json['access_token']
        
        response = client.put(f'/api/posts/{post.id}', 
            headers={'Authorization': f'Bearer {other_token}'},
            json={'title': 'Hacked Title'})
        assert response.status_code == 403
    
    def test_update_post_not_found(self, client, auth_headers):
        """Test updating non-existent post."""
        response = client.put('/api/posts/99999', headers=auth_headers, json={
            'title': 'Update Non-existent'
        })
        assert response.status_code == 404


class TestDeletePost:
    """Tests for deleting posts."""
    
    def test_delete_post_success(self, client, auth_headers, post):
        """Test successful post deletion."""
        response = client.delete(f'/api/posts/{post.id}', headers=auth_headers)
        assert response.status_code == 200
        
        # Verify post is deleted
        get_response = client.get(f'/api/posts/{post.id}')
        assert get_response.status_code == 404
    
    def test_delete_post_unauthorized(self, client, post):
        """Test deleting post without auth."""
        response = client.delete(f'/api/posts/{post.id}')
        assert response.status_code == 401
    
    def test_delete_post_forbidden(self, client, app, _db, post):
        """Test deleting another user's post."""
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
        
        response = client.delete(f'/api/posts/{post.id}',
            headers={'Authorization': f'Bearer {other_token}'})
        assert response.status_code == 403
    
    def test_delete_post_not_found(self, client, auth_headers):
        """Test deleting non-existent post."""
        response = client.delete('/api/posts/99999', headers=auth_headers)
        assert response.status_code == 404
