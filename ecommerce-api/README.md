# E-Commerce API

Complete e-commerce backend with shopping cart, checkout, payment processing, and order management.

## Features

✅ **Product Catalog**
- Product CRUD operations
- Search and filtering
- Category management
- Stock tracking
- Pricing with discounts

✅ **Shopping Cart**
- Add/update/remove items
- Session-based carts for guests
- User-based carts for authenticated users
- Cart expiry (7 days)
- Quantity validation
- Stock checking

✅ **Discount System**
- Percentage and fixed discounts
- Usage limits
- Validity periods
- Minimum purchase requirements
- Per-user usage tracking

✅ **Checkout & Orders**
- Complete checkout flow
- Shipping/billing addresses
- Order management
- Order history
- Order cancellation
- Stock reservation

✅ **Payment Processing**
- Stripe integration
- Payment intent creation
- Secure payment handling
- PCI compliance
- Refund processing

✅ **Email Notifications**
- Order confirmation emails
- Shipping notifications
- SendGrid integration

✅ **Security**
- JWT authentication
- Password hashing
- Input sanitization (XSS prevention)
- SQL injection prevention
- Rate limiting
- Card number validation (Luhn algorithm)

## Installation

### Option 1: Docker (Recommended)

**Easiest way to run the entire stack:**

```bash
# From project root
./docker-start-all.sh
```

Or manually:

```bash
docker compose up -d ecommerce-api
```

The API will be available at `http://localhost:5004`

**See `DOCKER_SETUP_COMPLETE.md` for full Docker documentation.**

### Option 2: Local Development

#### Prerequisites
- Python 3.9+
- pip
- virtualenv (recommended)

#### Setup

1. **Clone and navigate to directory:**
```bash
cd ecommerce-api
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application:**
```bash
python run.py
```

The API will be available at `http://localhost:5004`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Products
- `GET /api/products` - List products (with filtering)
- `GET /api/products/<id>` - Get product details
- `POST /api/products` - Create product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product
- `GET /api/products/categories` - List categories

### Cart
- `GET /api/cart` - Get current cart
- `POST /api/cart/items` - Add item to cart
- `PUT /api/cart/items/<product_id>` - Update item quantity
- `DELETE /api/cart/items/<product_id>` - Remove item
- `POST /api/cart/clear` - Clear cart
- `POST /api/cart/discount` - Apply discount code
- `DELETE /api/cart/discount` - Remove discount code

### Checkout
- `POST /api/checkout/create-payment-intent` - Create payment intent
- `POST /api/checkout/complete` - Complete checkout

### Orders
- `GET /api/orders` - List user's orders
- `GET /api/orders/<id>` - Get order details
- `GET /api/orders/<order_number>` - Get order by number
- `POST /api/orders/<id>/cancel` - Cancel order

### Discounts
- `POST /api/discounts/validate` - Validate discount code
- `POST /api/discounts` - Create discount code
- `GET /api/discounts` - List discount codes

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test Categories
```bash
# Positive tests
pytest -m positive

# Negative tests
pytest -m negative

# Edge cases
pytest -m edge

# Security tests
pytest -m security
```

### Test Statistics
- **Total Tests**: 35+
- **Positive Tests**: 10 (successful flows)
- **Negative Tests**: 10 (error handling)
- **Edge Cases**: 8 (boundary conditions)
- **Security Tests**: 7+ (security validations)

## Sample Data

### Create Sample Products
```python
from app import create_app, db
from app.models import Product

app = create_app()
with app.app_context():
    products = [
        Product(
            sku='LAPTOP-001',
            name='Premium Laptop',
            description='High-performance laptop',
            price=1299.99,
            compare_at_price=1599.99,
            category='Electronics',
            brand='TechBrand',
            stock_quantity=50,
            is_active=True,
            is_featured=True
        ),
        Product(
            sku='PHONE-001',
            name='Smartphone Pro',
            description='Latest smartphone',
            price=899.99,
            category='Electronics',
            brand='PhoneCo',
            stock_quantity=100,
            is_active=True
        ),
        Product(
            sku='HEADPHONES-001',
            name='Wireless Headphones',
            description='Noise-cancelling headphones',
            price=249.99,
            compare_at_price=299.99,
            category='Audio',
            brand='AudioTech',
            stock_quantity=75,
            is_active=True
        )
    ]
    
    for product in products:
        db.session.add(product)
    db.session.commit()
```

### Create Sample Discount Codes
```python
from app.models import DiscountCode
from datetime import datetime, timedelta

with app.app_context():
    discounts = [
        DiscountCode(
            code='SAVE20',
            description='20% off your order',
            discount_type='percentage',
            discount_value=20,
            min_purchase_amount=100,
            is_active=True
        ),
        DiscountCode(
            code='WELCOME10',
            description='$10 off first order',
            discount_type='fixed',
            discount_value=10,
            usage_limit_per_user=1,
            is_active=True
        )
    ]
    
    for discount in discounts:
        db.session.add(discount)
    db.session.commit()
```

## Configuration

### Environment Variables

```env
# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database
DATABASE_URL=sqlite:///ecommerce.db

# Stripe
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# SendGrid
SENDGRID_API_KEY=your_api_key
FROM_EMAIL=noreply@yourstore.com

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Project Structure

```
ecommerce-api/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/               # Database models
│   │   ├── user.py          # User & Address
│   │   ├── product.py       # Product catalog
│   │   ├── cart.py          # Cart & CartItem
│   │   ├── discount.py      # Discount codes
│   │   ├── order.py         # Orders & OrderItems
│   │   └── payment.py       # Payment records
│   ├── routes/              # API endpoints
│   │   ├── auth.py         # Authentication
│   │   ├── products.py     # Product CRUD
│   │   ├── cart.py         # Cart management
│   │   ├── checkout.py     # Checkout flow
│   │   ├── orders.py       # Order management
│   │   └── discounts.py    # Discount validation
│   ├── schemas/            # Marshmallow schemas
│   ├── services/           # Business logic
│   │   ├── payment_service.py  # Stripe integration
│   │   └── email_service.py    # Email sending
│   └── utils/              # Utilities
│       ├── errors.py       # Error handling
│       └── security.py     # Security functions
├── tests/                  # Test suite
│   ├── conftest.py        # Test fixtures
│   └── test_ecommerce_comprehensive.py  # 35+ tests
├── instance/              # SQLite database
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── pytest.ini           # Test configuration
└── run.py              # Application entry point
```

## License

MIT License
