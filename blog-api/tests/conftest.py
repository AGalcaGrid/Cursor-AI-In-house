import pytest
from datetime import datetime


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    from app import create_app, db as _db
    
    _app = create_app('testing')
    _app.config['TESTING'] = True
    _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    _app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with _app.app_context():
        _db.create_all()
        yield _app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def _db(app):
    """Get database instance."""
    from app import db
    return db


@pytest.fixture
def user(app, _db):
    """Create a test user."""
    from app.models.user import User
    
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('password123')
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def category(app, _db):
    """Create a test category."""
    from app.models.category import Category
    
    category = Category(
        name='Technology',
        slug='technology',
        description='Tech posts'
    )
    _db.session.add(category)
    _db.session.commit()
    return category


@pytest.fixture
def post(app, _db, user, category):
    """Create a test post."""
    from app.models.post import Post
    
    post = Post(
        title='Test Post Title',
        slug='test-post-title',
        content='This is the content of the test post with enough text.',
        excerpt='Test excerpt',
        author_id=user.id,
        category_id=category.id,
        is_published=True
    )
    _db.session.add(post)
    _db.session.commit()
    return post


@pytest.fixture
def comment(app, _db, post, user):
    """Create a test comment."""
    from app.models.comment import Comment
    
    comment = Comment(
        content='This is a test comment',
        post_id=post.id,
        author_id=user.id
    )
    _db.session.add(comment)
    _db.session.commit()
    return comment


@pytest.fixture
def auth_headers(client, user):
    """Get auth headers for test user."""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


def auth_header(token):
    """Helper to create authorization header."""
    return {'Authorization': f'Bearer {token}'}
