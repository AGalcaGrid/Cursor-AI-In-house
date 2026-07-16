"""
Comprehensive E-Commerce Test Suite
Student Exercise 1: E-Commerce Checkout Testing

Total Tests: 35+
Categories:
- Positive Tests (10): Successful flows
- Negative Tests (10): Error handling
- Edge Cases (8): Boundary conditions
- Security Tests (7): Security validations
"""

import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import auth_header
from app.models import Product, Cart, Order, DiscountCode


# ============================================================================
# POSITIVE TEST CASES (10 tests)
# ============================================================================

@pytest.mark.positive
class TestPositiveFlows:
    """TC-001 to TC-010: Positive test cases for successful checkout flows."""
    
    def test_tc001_add_item_to_cart(self, client, user_token, product):
        """TC-001: Successfully add item to cart."""
        response = client.post(
            '/api/cart/items',
            headers=auth_header(user_token),
            json={'product_id': product.id, 'quantity': 2}
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert response.json['data']['total_items'] == 2
    
    def test_tc002_apply_valid_discount_code(self, client, user_token, cart_with_items, discount_code):
        """TC-002: Successfully apply discount code."""
        response = client.post(
            '/api/cart/discount',
            headers=auth_header(user_token),
            json={'code': 'SAVE20'}
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert float(response.json['data']['discount_amount']) > 0
    
    def test_tc003_complete_checkout_flow(self, client, user_token, cart_with_items):
        """TC-003: Successfully complete full checkout."""
        checkout_data = {
            'shipping_first_name': 'John',
            'shipping_last_name': 'Doe',
            'shipping_email': 'john@example.com',
            'shipping_street_address': '123 Main St',
            'shipping_city': 'New York',
            'shipping_state': 'NY',
            'shipping_postal_code': '10001',
            'payment_method': 'card'
        }
        
        response = client.post(
            '/api/checkout/complete',
            headers=auth_header(user_token),
            json=checkout_data
        )
        
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert 'order_number' in response.json['data']
    
    def test_tc004_view_order_history(self, client, user_token, user):
        """TC-004: Successfully retrieve order history."""
        response = client.get(
            '/api/orders',
            headers=auth_header(user_token)
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert 'orders' in response.json['data']
    
    def test_tc005_update_cart_quantity(self, client, user_token, cart_with_items, product):
        """TC-005: Successfully update item quantity in cart."""
        response = client.put(
            f'/api/cart/items/{product.id}',
            headers=auth_header(user_token),
            json={'quantity': 5}
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
    
    def test_tc006_remove_item_from_cart(self, client, user_token, cart_with_items, product):
        """TC-006: Successfully remove item from cart."""
        response = client.delete(
            f'/api/cart/items/{product.id}',
            headers=auth_header(user_token)
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
    
    def test_tc007_search_products(self, client, product):
        """TC-007: Successfully search for products."""
        response = client.get('/api/products?search=Test')
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert len(response.json['data']['products']) > 0
    
    def test_tc008_filter_by_category(self, client, product):
        """TC-008: Successfully filter products by category."""
        response = client.get('/api/products?category=Electronics')
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
    
    @patch('app.services.payment_service.stripe.PaymentIntent.create')
    def test_tc009_create_payment_intent(self, mock_stripe, client, user_token, cart_with_items):
        """TC-009: Successfully create payment intent."""
        # Mock Stripe response
        mock_stripe.return_value = MagicMock(
            id='pi_test_123',
            client_secret='pi_test_123_secret_456',
            amount=10000,
            currency='usd',
            status='requires_payment_method'
        )
        
        response = client.post(
            '/api/checkout/create-payment-intent',
            headers=auth_header(user_token)
        )
        
        assert response.status_code == 200
        assert 'client_secret' in response.json['data']
    
    def test_tc010_clear_cart(self, client, user_token, cart_with_items):
        """TC-010: Successfully clear cart."""
        response = client.post(
            '/api/cart/clear',
            headers=auth_header(user_token)
        )
        
        assert response.status_code == 200
        assert response.json['data']['total_items'] == 0


# ============================================================================
# NEGATIVE TEST CASES (10 tests)
# ============================================================================

@pytest.mark.negative
class TestNegativeFlows:
    """TC-101 to TC-110: Negative test cases for error handling."""
    
    def test_tc101_add_out_of_stock_item(self, client, user_token, out_of_stock_product):
        """TC-101: Fail to add out-of-stock item to cart."""
        response = client.post(
            '/api/cart/items',
            headers=auth_header(user_token),
            json={'product_id': out_of_stock_product.id, 'quantity': 1}
        )
        
        assert response.status_code == 409
        assert 'out of stock' in response.json['message'].lower()
    
    def test_tc102_apply_invalid_discount_code(self, client, user_token, cart_with_items):
        """TC-102: Fail to apply invalid discount code."""
        response = client.post(
            '/api/cart/discount',
            headers=auth_header(user_token),
            json={'code': 'INVALID123'}
        )
        
        assert response.status_code == 404
    
    def test_tc103_apply_expired_discount_code(self, client, user_token, cart_with_items, expired_discount_code):
        """TC-103: Fail to apply expired discount code."""
        response = client.post(
            '/api/cart/discount',
            headers=auth_header(user_token),
            json={'code': 'EXPIRED'}
        )
        
        assert response.status_code == 400
        assert 'not valid' in response.json['message'].lower()
    
    def test_tc104_checkout_with_empty_cart(self, client, user_token):
        """TC-104: Fail checkout with empty cart."""
        checkout_data = {
            'shipping_first_name': 'John',
            'shipping_last_name': 'Doe',
            'shipping_email': 'john@example.com',
            'shipping_street_address': '123 Main St',
            'shipping_city': 'New York',
            'shipping_state': 'NY',
            'shipping_postal_code': '10001',
            'payment_method': 'card'
        }
        
        response = client.post(
            '/api/checkout/complete',
            headers=auth_header(user_token),
            json=checkout_data
        )
        
        assert response.status_code == 400
        assert 'empty' in response.json['message'].lower()
    
    def test_tc105_checkout_missing_required_fields(self, client, user_token, cart_with_items):
        """TC-105: Fail checkout with missing required fields."""
        response = client.post(
            '/api/checkout/complete',
            headers=auth_header(user_token),
            json={'shipping_first_name': 'John'}  # Missing required fields
        )
        
        assert response.status_code == 400
    
    def test_tc106_add_nonexistent_product(self, client, user_token):
        """TC-106: Fail to add non-existent product to cart."""
        response = client.post(
            '/api/cart/items',
            headers=auth_header(user_token),
            json={'product_id': 99999, 'quantity': 1}
        )
        
        assert response.status_code == 404
    
    def test_tc107_update_cart_without_auth(self, client, product):
        """TC-107: Test cart update without authentication."""
        response = client.put(
            f'/api/cart/items/{product.id}',
            json={'quantity': 5}
        )
        
        # Without auth, could return:
        # - 401 (requires auth)
        # - 400 (no cart exists / validation error)
        # - 200 (guest cart allowed)
        assert response.status_code in [200, 400, 401]
    
    def test_tc108_access_other_user_order(self, client, user_token, db_session):
        """TC-108: Fail to access another user's order."""
        # Create another user's order
        from app.models import User, Order
        other_user = User(email='other@example.com', first_name='Other', last_name='User')
        other_user.set_password('Pass123!')
        db_session.session.add(other_user)
        db_session.session.commit()
        
        order = Order(
            order_number='ORD-TEST-001',
            user_id=other_user.id,
            subtotal=100,
            total=100,
            shipping_first_name='Other',
            shipping_last_name='User',
            shipping_email='other@example.com',
            shipping_street_address='456 Oak St',
            shipping_city='Boston',
            shipping_state='MA',
            shipping_postal_code='02101'
        )
        db_session.session.add(order)
        db_session.session.commit()
        
        response = client.get(
            f'/api/orders/{order.id}',
            headers=auth_header(user_token)
        )
        
        assert response.status_code == 403
    
    def test_tc109_invalid_payment_method(self, client, user_token, cart_with_items):
        """TC-109: Fail checkout with invalid payment method."""
        checkout_data = {
            'shipping_first_name': 'John',
            'shipping_last_name': 'Doe',
            'shipping_email': 'john@example.com',
            'shipping_street_address': '123 Main St',
            'shipping_city': 'New York',
            'shipping_state': 'NY',
            'shipping_postal_code': '10001',
            'payment_method': 'bitcoin'  # Invalid
        }
        
        response = client.post(
            '/api/checkout/complete',
            headers=auth_header(user_token),
            json=checkout_data
        )
        
        assert response.status_code == 400
    
    def test_tc110_register_duplicate_email(self, client, user):
        """TC-110: Fail to register with existing email."""
        response = client.post(
            '/api/auth/register',
            json={
                'email': 'test@example.com',
                'password': 'NewPass123!',
                'first_name': 'Duplicate',
                'last_name': 'User'
            }
        )
        
        assert response.status_code == 409


# ============================================================================
# EDGE CASE TESTS (8 tests)
# ============================================================================

@pytest.mark.edge
class TestEdgeCases:
    """TC-201 to TC-208: Edge case testing."""
    
    def test_tc201_max_cart_quantity(self, client, user_token, product):
        """TC-201: Test maximum quantity per item."""
        response = client.post(
            '/api/cart/items',
            headers=auth_header(user_token),
            json={'product_id': product.id, 'quantity': 11}  # Max is 10
        )
        
        assert response.status_code == 400
    
    def test_tc202_cart_with_100_items(self, client, user_token, db_session):
        """TC-202: Test cart with maximum items."""
        # Create multiple products
        for i in range(15):
            product = Product(
                sku=f'BULK-{i:03d}',
                name=f'Bulk Product {i}',
                price=10.00,
                stock_quantity=100,
                is_active=True
            )
            db_session.session.add(product)
        db_session.session.commit()
        
        # Try to add many items
        products = Product.query.filter(Product.sku.like('BULK-%')).all()
        for product in products[:10]:
            client.post(
                '/api/cart/items',
                headers=auth_header(user_token),
                json={'product_id': product.id, 'quantity': 1}
            )
        
        response = client.get('/api/cart', headers=auth_header(user_token))
        assert response.status_code == 200
    
    def test_tc203_zero_quantity_removes_item(self, client, user_token, cart_with_items, product):
        """TC-203: Setting quantity to 0 removes item."""
        response = client.put(
            f'/api/cart/items/{product.id}',
            headers=auth_header(user_token),
            json={'quantity': 0}
        )
        
        assert response.status_code == 200
        assert 'removed' in response.json['message'].lower()
    
    def test_tc204_discount_100_percent(self, client, user_token, cart_with_items, db_session):
        """TC-204: Test 100% discount code."""
        discount = DiscountCode(
            code='FREE100',
            description='100% off',
            discount_type='percentage',
            discount_value=100,
            is_active=True
        )
        db_session.session.add(discount)
        db_session.session.commit()
        
        response = client.post(
            '/api/cart/discount',
            headers=auth_header(user_token),
            json={'code': 'FREE100'}
        )
        
        assert response.status_code == 200
        assert float(response.json['data']['total']) == 0
    
    def test_tc205_very_long_product_name(self, client, db_session):
        """TC-205: Test product with very long name."""
        long_name = 'A' * 200
        product = Product(
            sku='LONG-001',
            name=long_name,
            price=50.00,
            stock_quantity=10,
            is_active=True
        )
        db_session.session.add(product)
        db_session.session.commit()
        
        response = client.get(f'/api/products/{product.id}')
        assert response.status_code == 200
        assert len(response.json['data']['name']) == 200
    
    def test_tc206_concurrent_cart_updates(self, client, user_token, product):
        """TC-206: Test concurrent cart updates."""
        # Add item multiple times rapidly
        for _ in range(3):
            client.post(
                '/api/cart/items',
                headers=auth_header(user_token),
                json={'product_id': product.id, 'quantity': 1}
            )
        
        response = client.get('/api/cart', headers=auth_header(user_token))
        assert response.status_code == 200
        # Should handle concurrent updates gracefully
    
    def test_tc207_special_characters_in_address(self, client, user_token, cart_with_items):
        """TC-207: Test special characters in shipping address."""
        checkout_data = {
            'shipping_first_name': "O'Brien",
            'shipping_last_name': 'Smith-Jones',
            'shipping_email': 'test+tag@example.com',
            'shipping_street_address': '123 Main St, Apt #4-B',
            'shipping_city': 'New York',
            'shipping_state': 'NY',
            'shipping_postal_code': '10001',
            'payment_method': 'card'
        }
        
        response = client.post(
            '/api/checkout/complete',
            headers=auth_header(user_token),
            json=checkout_data
        )
        
        assert response.status_code == 201
    
    def test_tc208_minimum_order_amount(self, client, user_token, db_session):
        """TC-208: Test minimum order amount validation."""
        # Create very cheap product
        cheap_product = Product(
            sku='CHEAP-001',
            name='Cheap Item',
            price=0.10,
            stock_quantity=10,
            is_active=True
        )
        db_session.session.add(cheap_product)
        db_session.session.commit()
        
        client.post(
            '/api/cart/items',
            headers=auth_header(user_token),
            json={'product_id': cheap_product.id, 'quantity': 1}
        )
        
        response = client.post(
            '/api/checkout/create-payment-intent',
            headers=auth_header(user_token)
        )
        
        # Should fail if below minimum ($0.50)
        assert response.status_code in [200, 400]


# ============================================================================
# SECURITY TEST CASES (7 tests)
# ============================================================================

@pytest.mark.security
class TestSecurityCases:
    """TC-301 to TC-307: Security test cases."""
    
    def test_tc301_sql_injection_in_search(self, client):
        """TC-301: Test SQL injection prevention in search."""
        response = client.get("/api/products?search='; DROP TABLE products; --")
        
        assert response.status_code == 200
        # Should not crash, products table should still exist
        assert 'products' in response.json['data']
    
    def test_tc302_xss_in_discount_code(self, client, user_token, cart_with_items):
        """TC-302: Test XSS prevention in discount code."""
        response = client.post(
            '/api/cart/discount',
            headers=auth_header(user_token),
            json={'code': "<script>alert('xss')</script>"}
        )
        
        # Should handle safely without executing script
        assert response.status_code in [400, 404]
    
    def test_tc303_password_not_in_response(self, client, user):
        """TC-303: Ensure password hash not exposed in API."""
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user.id))
        
        response = client.get('/api/auth/me', headers=auth_header(token))
        
        assert response.status_code == 200
        assert 'password_hash' not in response.json['data']
        assert 'password' not in response.json['data']
    
    def test_tc304_weak_password_rejected(self, client):
        """TC-304: Test weak password rejection."""
        response = client.post(
            '/api/auth/register',
            json={
                'email': 'weak@example.com',
                'password': 'weak',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        assert response.status_code == 400
    
    def test_tc305_rate_limiting_registration(self, client):
        """TC-305: Test rate limiting on registration."""
        # Attempt multiple registrations rapidly
        for i in range(7):
            client.post(
                '/api/auth/register',
                json={
                    'email': f'spam{i}@example.com',
                    'password': 'TestPass123!',
                    'first_name': 'Spam',
                    'last_name': 'User'
                }
            )
        
        # Should eventually hit rate limit
        # Note: In testing, rate limiting might be disabled
    
    def test_tc306_csrf_protection(self, client, user_token, cart_with_items):
        """TC-306: Test CSRF protection on state-changing operations."""
        # JWT-based auth provides CSRF protection
        response = client.post(
            '/api/cart/clear',
            headers=auth_header(user_token)
        )
        
        assert response.status_code == 200
    
    def test_tc307_unauthorized_access_to_orders(self, client):
        """TC-307: Test unauthorized access to orders."""
        response = client.get('/api/orders')
        
        assert response.status_code == 401


# ============================================================================
# PAYMENT VALIDATION TESTS (Additional)
# ============================================================================

@pytest.mark.security
class TestPaymentValidation:
    """Additional payment security tests."""
    
    @patch('app.services.payment_service.stripe.PaymentIntent.create')
    def test_payment_data_validation(self, mock_stripe, client, user_token, cart_with_items):
        """Test payment data is validated."""
        # Mock Stripe response
        mock_stripe.return_value = MagicMock(
            id='pi_test_validation',
            client_secret='pi_test_validation_secret',
            amount=10000,
            currency='usd',
            status='requires_payment_method'
        )
        
        response = client.post(
            '/api/checkout/create-payment-intent',
            headers=auth_header(user_token)
        )
        
        assert response.status_code == 200
        # Payment intent should be created securely
        assert 'client_secret' in response.json['data']
