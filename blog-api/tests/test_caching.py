import pytest


class TestCacheInvalidation:
    """Tests for cache invalidation on CRUD operations."""
    
    def test_cache_invalidated_on_create(self, client, auth_headers, category):
        """Test that cache is invalidated when creating a post."""
        # Get initial posts
        response1 = client.get('/api/posts')
        initial_count = len(response1.json['posts'])
        
        # Create new post
        client.post('/api/posts', headers=auth_headers, json={
            'title': 'New Cached Post',
            'content': 'This post should invalidate the cache',
            'category_id': category.id
        })
        
        # Get posts again - should include new post
        response2 = client.get('/api/posts')
        new_count = len(response2.json['posts'])
        
        assert new_count == initial_count + 1
    
    def test_cache_invalidated_on_update(self, client, auth_headers, post):
        """Test that cache is invalidated when updating a post."""
        # Get initial post
        response1 = client.get(f'/api/posts/{post.id}')
        original_title = response1.json['post']['title']
        
        # Update post
        client.put(f'/api/posts/{post.id}', headers=auth_headers, json={
            'title': 'Updated Cached Title'
        })
        
        # Get post again - should have new title
        response2 = client.get(f'/api/posts/{post.id}')
        
        assert response2.json['post']['title'] == 'Updated Cached Title'
        assert response2.json['post']['title'] != original_title
    
    def test_cache_invalidated_on_delete(self, client, auth_headers, post):
        """Test that cache is invalidated when deleting a post."""
        post_id = post.id
        
        # Get initial posts count
        response1 = client.get('/api/posts')
        initial_count = len(response1.json['posts'])
        
        # Delete post
        client.delete(f'/api/posts/{post_id}', headers=auth_headers)
        
        # Get posts again - should have one less
        response2 = client.get('/api/posts')
        new_count = len(response2.json['posts'])
        
        assert new_count == initial_count - 1


class TestCacheKeyGeneration:
    """Tests for cache key generation."""
    
    def test_different_pages_different_cache(self, client, app, _db, user, category):
        """Test that different pages have different cache keys."""
        from app.models.post import Post
        
        # Create enough posts for pagination
        for i in range(25):
            post = Post(
                title=f'Cache Key Post {i}',
                slug=f'cache-key-post-{i}',
                content='Content for cache key testing',
                author_id=user.id,
                category_id=category.id
            )
            _db.session.add(post)
        _db.session.commit()
        
        # Get different pages
        response1 = client.get('/api/posts?page=1&per_page=10')
        response2 = client.get('/api/posts?page=2&per_page=10')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        # Different pages should have different posts
        assert response1.json['posts'][0]['id'] != response2.json['posts'][0]['id']
    
    def test_category_filter_different_cache(self, client, app, _db, user):
        """Test that category filter creates different cache."""
        from app.models.post import Post
        from app.models.category import Category
        
        # Create two categories
        cat1 = Category(name='Tech', slug='tech', description='Tech posts')
        cat2 = Category(name='Life', slug='life', description='Life posts')
        _db.session.add_all([cat1, cat2])
        _db.session.commit()
        
        # Create posts in different categories
        post1 = Post(
            title='Tech Post',
            slug='tech-post',
            content='Content for tech category',
            author_id=user.id,
            category_id=cat1.id
        )
        post2 = Post(
            title='Life Post',
            slug='life-post',
            content='Content for life category',
            author_id=user.id,
            category_id=cat2.id
        )
        _db.session.add_all([post1, post2])
        _db.session.commit()
        
        # Get posts by category
        response1 = client.get('/api/posts?category=tech')
        response2 = client.get('/api/posts?category=life')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(response1.json['posts']) == 1
        assert len(response2.json['posts']) == 1
        assert response1.json['posts'][0]['title'] == 'Tech Post'
        assert response2.json['posts'][0]['title'] == 'Life Post'
