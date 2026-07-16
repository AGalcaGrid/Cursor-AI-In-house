"""Tests for task endpoints with caching and performance optimizations."""
import pytest
from datetime import datetime, timedelta
from app.models.task import Task


class TestGetTasks:
    """Test GET /api/tasks endpoint."""
    
    def test_get_tasks_success(self, client, auth_headers, test_task):
        """Test getting tasks successfully."""
        response = client.get('/api/tasks', headers=auth_headers)
        
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Test Task'
        assert response.json[0]['status'] == 'pending'
    
    def test_get_tasks_empty(self, client, auth_headers, db_session):
        """Test getting tasks when none exist."""
        response = client.get('/api/tasks', headers=auth_headers)
        
        assert response.status_code == 200
        assert len(response.json) == 0
    
    def test_get_tasks_filter_by_status(self, client, auth_headers, multiple_tasks):
        """Test filtering tasks by status."""
        response = client.get('/api/tasks?status=pending', headers=auth_headers)
        
        assert response.status_code == 200
        assert all(task['status'] == 'pending' for task in response.json)
    
    def test_get_tasks_filter_by_priority(self, client, auth_headers, multiple_tasks):
        """Test filtering tasks by priority."""
        response = client.get('/api/tasks?priority=high', headers=auth_headers)
        
        assert response.status_code == 200
        assert all(task['priority'] == 'high' for task in response.json)
    
    def test_get_tasks_filter_assigned_to_me(self, client, auth_headers, assigned_task, test_user):
        """Test filtering tasks assigned to current user."""
        # Login as the assigned user
        response = client.post('/api/auth/login', json={
            'email': 'another@example.com',
            'password': 'AnotherPassword123!'
        })
        token = response.json['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/tasks?assigned_to_me=true', headers=headers)
        
        assert response.status_code == 200
        assert len(response.json) >= 1
        assert any(task['title'] == 'Assigned Task' for task in response.json)
    
    def test_get_tasks_unauthorized(self, client):
        """Test getting tasks without authentication."""
        response = client.get('/api/tasks')
        
        assert response.status_code == 401
    
    def test_get_tasks_caching(self, client, auth_headers, test_task):
        """Test that tasks endpoint uses caching."""
        # First request
        response1 = client.get('/api/tasks', headers=auth_headers)
        assert response1.status_code == 200
        
        # Second request should be cached
        response2 = client.get('/api/tasks', headers=auth_headers)
        assert response2.status_code == 200
        assert response1.json == response2.json


class TestGetTask:
    """Test GET /api/tasks/<id> endpoint."""
    
    def test_get_task_success(self, client, auth_headers, test_task):
        """Test getting a specific task."""
        response = client.get(f'/api/tasks/{test_task.id}', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['id'] == test_task.id
        assert response.json['title'] == 'Test Task'
    
    def test_get_task_not_found(self, client, auth_headers):
        """Test getting a non-existent task."""
        response = client.get('/api/tasks/99999', headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_task_unauthorized(self, client, test_task):
        """Test getting a task without authentication."""
        response = client.get(f'/api/tasks/{test_task.id}')
        
        assert response.status_code == 401


class TestCreateTask:
    """Test POST /api/tasks endpoint."""
    
    def test_create_task_success(self, client, auth_headers, db_session):
        """Test creating a task successfully."""
        task_data = {
            'title': 'New Task',
            'description': 'New task description',
            'status': 'pending',
            'priority': 'high',
            'due_date': (datetime.utcnow() + timedelta(days=5)).isoformat()
        }
        
        response = client.post('/api/tasks', json=task_data, headers=auth_headers)
        
        assert response.status_code == 201
        assert response.json['title'] == 'New Task'
        assert response.json['priority'] == 'high'
        
        # Verify task was created in database
        task = Task.query.filter_by(title='New Task').first()
        assert task is not None
    
    def test_create_task_minimal_data(self, client, auth_headers):
        """Test creating a task with minimal required data."""
        task_data = {
            'title': 'Minimal Task'
        }
        
        response = client.post('/api/tasks', json=task_data, headers=auth_headers)
        
        assert response.status_code == 201
        assert response.json['title'] == 'Minimal Task'
        assert response.json['status'] == 'pending'  # Default value
        assert response.json['priority'] == 'medium'  # Default value
    
    def test_create_task_validation_error(self, client, auth_headers):
        """Test creating a task with invalid data."""
        task_data = {
            'description': 'Missing title'
        }
        
        response = client.post('/api/tasks', json=task_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert 'errors' in response.json
    
    def test_create_task_with_assignment(self, client, auth_headers, another_user, mocker):
        """Test creating a task with assignment triggers notification."""
        # Mock the Celery task
        mock_task = mocker.patch('app.routes.tasks.send_task_assignment_email')
        
        task_data = {
            'title': 'Assigned Task',
            'assigned_to_id': another_user.id
        }
        
        response = client.post('/api/tasks', json=task_data, headers=auth_headers)
        
        assert response.status_code == 201
        assert response.json['assigned_to_id'] == another_user.id
        
        # Verify background task was called
        mock_task.delay.assert_called_once()
    
    def test_create_task_cache_invalidation(self, client, auth_headers):
        """Test that creating a task invalidates cache."""
        # Get tasks (should cache)
        response1 = client.get('/api/tasks', headers=auth_headers)
        initial_count = len(response1.json)
        
        # Create new task
        task_data = {'title': 'Cache Test Task'}
        client.post('/api/tasks', json=task_data, headers=auth_headers)
        
        # Get tasks again (cache should be invalidated)
        response2 = client.get('/api/tasks', headers=auth_headers)
        assert len(response2.json) == initial_count + 1


class TestUpdateTask:
    """Test PUT /api/tasks/<id> endpoint."""
    
    def test_update_task_success(self, client, auth_headers, test_task):
        """Test updating a task successfully."""
        update_data = {
            'title': 'Updated Task',
            'status': 'in_progress',
            'priority': 'high'
        }
        
        response = client.put(f'/api/tasks/{test_task.id}', json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['title'] == 'Updated Task'
        assert response.json['status'] == 'in_progress'
        assert response.json['priority'] == 'high'
    
    def test_update_task_partial(self, client, auth_headers, test_task):
        """Test partial update of a task."""
        update_data = {
            'status': 'completed'
        }
        
        response = client.put(f'/api/tasks/{test_task.id}', json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['status'] == 'completed'
        assert response.json['title'] == 'Test Task'  # Unchanged
    
    def test_update_task_not_found(self, client, auth_headers):
        """Test updating a non-existent task."""
        update_data = {'title': 'Updated'}
        response = client.put('/api/tasks/99999', json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_task_assignment_notification(self, client, auth_headers, test_task, another_user, mocker):
        """Test that updating assignment triggers notification."""
        mock_task = mocker.patch('app.routes.tasks.send_task_assignment_email')
        
        update_data = {
            'assigned_to_id': another_user.id
        }
        
        response = client.put(f'/api/tasks/{test_task.id}', json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        mock_task.delay.assert_called_once()


class TestDeleteTask:
    """Test DELETE /api/tasks/<id> endpoint."""
    
    def test_delete_task_success(self, client, auth_headers, test_task, db_session):
        """Test deleting a task successfully."""
        task_id = test_task.id
        
        response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.json['message']
        
        # Verify task was deleted from database
        task = Task.query.get(task_id)
        assert task is None
    
    def test_delete_task_not_found(self, client, auth_headers):
        """Test deleting a non-existent task."""
        response = client.delete('/api/tasks/99999', headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_task_cache_invalidation(self, client, auth_headers, test_task):
        """Test that deleting a task invalidates cache."""
        task_id = test_task.id
        
        # Get tasks (should cache)
        response1 = client.get('/api/tasks', headers=auth_headers)
        initial_count = len(response1.json)
        
        # Delete task
        client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
        
        # Get tasks again (cache should be invalidated)
        response2 = client.get('/api/tasks', headers=auth_headers)
        assert len(response2.json) == initial_count - 1


class TestReportGeneration:
    """Test report generation endpoints."""
    
    def test_request_report_success(self, client, auth_headers, multiple_tasks, mocker):
        """Test requesting a report generation."""
        mock_task = mocker.patch('app.routes.tasks.generate_user_report')
        mock_task.delay.return_value.id = 'test-task-id'
        
        response = client.post('/api/tasks/reports/generate', 
                              json={'report_type': 'summary'}, 
                              headers=auth_headers)
        
        assert response.status_code == 202
        assert 'task_id' in response.json
        assert 'status_url' in response.json
        mock_task.delay.assert_called_once()
    
    def test_request_report_invalid_type(self, client, auth_headers):
        """Test requesting a report with invalid type."""
        response = client.post('/api/tasks/reports/generate',
                              json={'report_type': 'invalid'},
                              headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_get_report_status(self, client, auth_headers, mocker):
        """Test checking report generation status."""
        # Mock AsyncResult
        mock_result = mocker.MagicMock()
        mock_result.state = 'SUCCESS'
        mock_result.result = {'test': 'data'}
        
        mocker.patch('app.routes.tasks.AsyncResult', return_value=mock_result)
        
        response = client.get('/api/tasks/reports/status/test-task-id', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['state'] == 'SUCCESS'
        assert 'result' in response.json


class TestPerformanceOptimizations:
    """Test performance optimizations."""
    
    def test_query_uses_eager_loading(self, client, auth_headers, assigned_task, mocker):
        """Test that queries use eager loading for relationships."""
        # This test verifies the joinedload is being used
        response = client.get('/api/tasks', headers=auth_headers)
        
        assert response.status_code == 200
        # If eager loading works, assignee data should be included
        tasks_with_assignee = [t for t in response.json if t.get('assigned_to_id')]
        assert len(tasks_with_assignee) > 0
    
    def test_database_indexes_exist(self, app, db_session):
        """Test that database indexes are created."""
        from sqlalchemy import inspect
        
        inspector = inspect(db_session.engine)
        indexes = inspector.get_indexes('tasks')
        
        # Check that our custom indexes exist
        index_names = [idx['name'] for idx in indexes]
        assert 'idx_user_status' in index_names
        assert 'idx_user_priority' in index_names
        assert 'idx_created_at' in index_names
