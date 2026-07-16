import pytest
import time


class TestResponseTime:
    """Tests for API response time performance."""
    
    def test_get_posts_response_time(self, client, post):
        """Test that getting posts responds within acceptable time."""
        start_time = time.time()
        response = client.get('/api/posts')
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time < 500
    
    def test_get_single_post_response_time(self, client, post):
        """Test that getting a single post responds quickly."""
        start_time = time.time()
        response = client.get(f'/api/posts/{post.id}')
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time < 200
    
    def test_search_response_time(self, client, post):
        """Test that search responds within acceptable time."""
        start_time = time.time()
        response = client.get('/api/search?q=Test')
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time < 500


class TestCachingEffectiveness:
    """Tests to verify caching improves performance."""
    
    def test_repeated_requests_consistent(self, client, post):
        """Test that repeated requests return consistent results."""
        response1 = client.get('/api/posts')
        response2 = client.get('/api/posts')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json['posts'] == response2.json['posts']
    
    def test_cached_single_post_consistent(self, client, post):
        """Test that cached single post returns consistent results."""
        response1 = client.get(f'/api/posts/{post.id}')
        response2 = client.get(f'/api/posts/{post.id}')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json['post']['id'] == response2.json['post']['id']


class TestPaginationPerformance:
    """Tests for pagination performance."""
    
    def test_pagination_first_page(self, client, app, _db, user, category):
        """Test first page pagination performance."""
        from app.models.post import Post
        
        for i in range(25):
            post = Post(
                title=f'Pagination Post {i}',
                slug=f'pagination-post-{i}',
                content='Content for pagination testing',
                author_id=user.id,
                category_id=category.id
            )
            _db.session.add(post)
        _db.session.commit()
        
        start_time = time.time()
        response = client.get('/api/posts?page=1&per_page=10')
        response_time = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        assert len(response.json['posts']) == 10
        assert response_time < 500
    
    def test_pagination_second_page(self, client, app, _db, user, category):
        """Test second page pagination performance."""
        from app.models.post import Post
        
        for i in range(25):
            post = Post(
                title=f'Page2 Post {i}',
                slug=f'page2-post-{i}',
                content='Content for pagination testing',
                author_id=user.id,
                category_id=category.id
            )
            _db.session.add(post)
        _db.session.commit()
        
        response = client.get('/api/posts?page=2&per_page=10')
        
        assert response.status_code == 200
        assert response.json['pagination']['page'] == 2


class TestBulkOperations:
    """Tests for bulk operation performance."""
    
    def test_multiple_sequential_requests(self, client, post):
        """Test handling multiple sequential requests."""
        for _ in range(5):
            response = client.get('/api/posts')
            assert response.status_code == 200
    
    def test_category_filter_performance(self, client, post, category):
        """Test category filtering performance."""
        start_time = time.time()
        response = client.get(f'/api/posts?category={category.slug}')
        response_time = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time < 500
