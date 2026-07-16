import pytest


class TestSearch:
    """Tests for search functionality."""
    
    def test_search_posts_success(self, client, post):
        """Test successful search."""
        response = client.get('/api/search?q=Test')
        assert response.status_code == 200
        assert len(response.json['posts']) == 1
        assert response.json['query'] == 'Test'
    
    def test_search_posts_no_results(self, client, post):
        """Test search with no matching results."""
        response = client.get('/api/search?q=nonexistent')
        assert response.status_code == 200
        assert response.json['posts'] == []
    
    def test_search_posts_missing_query(self, client, app, _db):
        """Test search without query parameter."""
        response = client.get('/api/search')
        assert response.status_code == 400
    
    def test_search_posts_empty_query(self, client, app, _db):
        """Test search with empty query."""
        response = client.get('/api/search?q=')
        assert response.status_code == 400
    
    def test_search_posts_content_match(self, client, post):
        """Test search matches content."""
        response = client.get('/api/search?q=content')
        assert response.status_code == 200
        assert len(response.json['posts']) == 1
    
    def test_search_posts_pagination(self, client, app, _db, user, category):
        """Test search pagination."""
        from app.models.post import Post
        
        # Create multiple posts with searchable content
        for i in range(25):
            post = Post(
                title=f'Searchable Post {i}',
                slug=f'searchable-post-{i}',
                content='This is searchable content for testing',
                author_id=user.id,
                category_id=category.id
            )
            _db.session.add(post)
        _db.session.commit()
        
        response = client.get('/api/search?q=searchable&page=1&per_page=10')
        assert response.status_code == 200
        assert len(response.json['posts']) == 10
        assert response.json['pagination']['total'] == 25
