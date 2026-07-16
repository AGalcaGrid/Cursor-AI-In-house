import pytest


class TestGetCategories:
    """Tests for getting categories."""
    
    def test_get_categories_empty(self, client, app, _db):
        """Test getting categories when none exist."""
        response = client.get('/api/categories')
        assert response.status_code == 200
        assert response.json['categories'] == []
    
    def test_get_categories_with_data(self, client, category):
        """Test getting categories with data."""
        response = client.get('/api/categories')
        assert response.status_code == 200
        assert len(response.json['categories']) == 1
        assert response.json['categories'][0]['name'] == 'Technology'
    
    def test_get_single_category(self, client, category):
        """Test getting a single category."""
        response = client.get(f'/api/categories/{category.id}')
        assert response.status_code == 200
        assert response.json['category']['name'] == 'Technology'
    
    def test_get_category_not_found(self, client, app, _db):
        """Test getting non-existent category."""
        response = client.get('/api/categories/99999')
        assert response.status_code == 404
