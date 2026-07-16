"""Pytest configuration and fixtures for testing."""
import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.models.notification import Notification


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['CACHE_TYPE'] = 'simple'  # Use simple cache for testing
    app.config['CELERY_TASK_ALWAYS_EAGER'] = True  # Run tasks synchronously in tests
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        # Clear all tables before each test
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield db
        db.session.remove()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        name='Test User',
        email='test@example.com',
        role='user'
    )
    user.set_password('TestPassword123!')
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin user."""
    user = User(
        name='Admin User',
        email='admin@example.com',
        role='admin'
    )
    user.set_password('AdminPassword123!')
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def another_user(db_session):
    """Create another test user."""
    user = User(
        name='Another User',
        email='another@example.com',
        role='user'
    )
    user.set_password('AnotherPassword123!')
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'TestPassword123!'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_headers(client, admin_user):
    """Get authentication headers for admin user."""
    response = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'password': 'AdminPassword123!'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def test_task(db_session, test_user):
    """Create a test task."""
    task = Task(
        title='Test Task',
        description='This is a test task',
        status='pending',
        priority='medium',
        user_id=test_user.id,
        due_date=datetime.utcnow() + timedelta(days=7)
    )
    db_session.session.add(task)
    db_session.session.commit()
    return task


@pytest.fixture
def completed_task(db_session, test_user):
    """Create a completed task."""
    task = Task(
        title='Completed Task',
        description='This task is completed',
        status='completed',
        priority='high',
        user_id=test_user.id
    )
    db_session.session.add(task)
    db_session.session.commit()
    return task


@pytest.fixture
def assigned_task(db_session, test_user, another_user):
    """Create a task assigned to another user."""
    task = Task(
        title='Assigned Task',
        description='This task is assigned',
        status='in_progress',
        priority='high',
        user_id=test_user.id,
        assigned_to_id=another_user.id
    )
    db_session.session.add(task)
    db_session.session.commit()
    return task


@pytest.fixture
def test_project(db_session, test_user):
    """Create a test project."""
    project = Project(
        name='Test Project',
        description='This is a test project',
        owner_id=test_user.id
    )
    db_session.session.add(project)
    db_session.session.commit()
    return project


@pytest.fixture
def multiple_tasks(db_session, test_user):
    """Create multiple tasks with different statuses and priorities."""
    tasks = [
        Task(
            title=f'Task {i}',
            description=f'Description for task {i}',
            status=['pending', 'in_progress', 'completed'][i % 3],
            priority=['low', 'medium', 'high'][i % 3],
            user_id=test_user.id,
            due_date=datetime.utcnow() + timedelta(days=i)
        )
        for i in range(10)
    ]
    db_session.session.add_all(tasks)
    db_session.session.commit()
    return tasks


@pytest.fixture
def test_notification(db_session, test_user, test_task):
    """Create a test notification."""
    notification = Notification(
        user_id=test_user.id,
        type='task_assigned',
        title='Task Assigned',
        message='You have been assigned a new task',
        task_id=test_task.id,
        read=False
    )
    db_session.session.add(notification)
    db_session.session.commit()
    return notification


@pytest.fixture
def mock_cache(mocker):
    """Mock Redis cache for testing."""
    return mocker.patch('app.cache')


@pytest.fixture
def mock_celery(mocker):
    """Mock Celery tasks for testing."""
    return mocker.patch('app.tasks.celery_tasks')
