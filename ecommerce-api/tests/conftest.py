import pytest
from app import create_app, db as _db
from app.models import User, Product, Cart, DiscountCode, Order
from flask_jwt_extended import create_access_token


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db_session):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def user(db_session):
    """Create test user."""
    user = User(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        phone='+1234567890'
    )
    user.set_password('TestPass123!')
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def user_token(user):
    """Create JWT token for test user."""
    return create_access_token(identity=str(user.id))


@pytest.fixture
def product(db_session):
    """Create test product."""
    product = Product(
        sku='TEST-001',
        name='Test Product',
        description='A test product',
        price=99.99,
        compare_at_price=129.99,
        category='Electronics',
        brand='TestBrand',
        stock_quantity=100,
        is_active=True
    )
    db_session.session.add(product)
    db_session.session.commit()
    return product


@pytest.fixture
def out_of_stock_product(db_session):
    """Create out of stock product."""
    product = Product(
        sku='OOS-001',
        name='Out of Stock Product',
        description='This product is out of stock',
        price=49.99,
        category='Electronics',
        stock_quantity=0,
        is_active=True
    )
    db_session.session.add(product)
    db_session.session.commit()
    return product


@pytest.fixture
def discount_code(db_session):
    """Create test discount code."""
    discount = DiscountCode(
        code='SAVE20',
        description='20% off',
        discount_type='percentage',
        discount_value=20,
        is_active=True
    )
    db_session.session.add(discount)
    db_session.session.commit()
    return discount


@pytest.fixture
def expired_discount_code(db_session):
    """Create expired discount code."""
    from datetime import datetime, timedelta
    discount = DiscountCode(
        code='EXPIRED',
        description='Expired discount',
        discount_type='percentage',
        discount_value=10,
        is_active=True,
        valid_until=datetime.utcnow() - timedelta(days=1)
    )
    db_session.session.add(discount)
    db_session.session.commit()
    return discount


@pytest.fixture
def cart_with_items(db_session, user, product):
    """Create cart with items."""
    cart = Cart(user_id=user.id)
    db_session.session.add(cart)
    db_session.session.commit()
    
    cart.add_item(product, 2)
    db_session.session.commit()
    return cart


def auth_header(token):
    """Helper to create authorization header."""
    return {'Authorization': f'Bearer {token}'}
