from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from decimal import Decimal

from app import db
from app.models.cart import Cart
from app.models.order import Order, OrderItem
from app.models.discount import DiscountUsage
from app.schemas.order import CheckoutSchema, OrderSchema, PaymentIntentSchema
from app.utils.errors import NotFoundError, StockError, ValidationError as CustomValidationError, PaymentError
from app.utils.security import get_current_user
from app.services.payment_service import PaymentService
from app.services.email_service import EmailService

checkout_bp = Blueprint('checkout', __name__)
checkout_schema = CheckoutSchema()
order_schema = OrderSchema()
payment_intent_schema = PaymentIntentSchema()


@checkout_bp.route('/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """Create Stripe payment intent for checkout."""
    user = get_current_user()
    if not user:
        raise NotFoundError('User not found')
    
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart or not cart.items:
        raise CustomValidationError('Cart is empty')
    
    # Validate stock availability
    for item in cart.items:
        if item.quantity > item.product.stock_quantity:
            raise StockError(
                f'Insufficient stock for {item.product.name}. '
                f'Only {item.product.stock_quantity} available.'
            )
    
    # Calculate total
    total = float(cart.total)
    
    if total < 0.5:
        raise CustomValidationError('Minimum order amount is $0.50')
    
    # Create payment intent
    try:
        payment_intent_data = PaymentService.create_payment_intent(
            amount=total,
            metadata={
                'user_id': user.id,
                'cart_id': cart.id
            }
        )
        
        return jsonify({
            'status': 'success',
            'data': payment_intent_data
        }), 200
    except PaymentError as e:
        raise e


@checkout_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_checkout():
    """Complete checkout and create order."""
    user = get_current_user()
    if not user:
        raise NotFoundError('User not found')
    
    try:
        data = checkout_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart or not cart.items:
        raise CustomValidationError('Cart is empty')
    
    # Validate stock and reserve inventory
    for item in cart.items:
        if item.quantity > item.product.stock_quantity:
            raise StockError(
                f'Insufficient stock for {item.product.name}. '
                f'Only {item.product.stock_quantity} available.'
            )
    
    # Extract payment_method from data (it belongs to Payment model, not Order)
    payment_method = data.pop('payment_method', 'card')
    
    # Create order
    order = Order(
        order_number=Order.generate_order_number(),
        user_id=user.id,
        subtotal=cart.subtotal,
        discount_amount=cart.discount_amount,
        shipping_cost=0,  # Calculate based on shipping method
        tax_amount=cart.subtotal * Decimal('0.08'),  # 8% tax (should be calculated based on location)
        total=cart.total + (cart.subtotal * Decimal('0.08')),  # Add tax
        discount_code_id=cart.discount_code_id,
        **data
    )
    
    db.session.add(order)
    db.session.flush()  # Get order ID
    
    # Create payment record
    from app.models.payment import Payment
    payment = Payment(
        order_id=order.id,
        payment_method=payment_method,
        payment_status='succeeded',  # In real app, this would be set after payment processing
        amount=order.total
    )
    db.session.add(payment)
    
    # Create order items and reduce stock
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            product_name=cart_item.product.name,
            product_sku=cart_item.product.sku,
            quantity=cart_item.quantity,
            price=cart_item.price
        )
        db.session.add(order_item)
        
        # Reduce stock
        cart_item.product.reduce_stock(cart_item.quantity)
    
    # Record discount usage
    if cart.discount_code_id:
        discount_usage = DiscountUsage(
            discount_code_id=cart.discount_code_id,
            user_id=user.id,
            order_id=order.id,
            discount_amount=cart.discount_amount
        )
        db.session.add(discount_usage)
        cart.discount_code.increment_usage()
    
    # Clear cart
    cart.clear()
    
    db.session.commit()
    
    # Send order confirmation email
    try:
        EmailService.send_order_confirmation(order)
    except Exception as e:
        # Log error but don't fail the order
        print(f"Failed to send order confirmation email: {str(e)}")
    
    return jsonify({
        'status': 'success',
        'message': 'Order created successfully',
        'data': order_schema.dump(order)
    }), 201


@checkout_bp.route('/guest', methods=['POST'])
def guest_checkout():
    """Guest checkout (without authentication)."""
    # Similar to complete_checkout but for guest users
    # This would require session-based cart management
    return jsonify({
        'status': 'error',
        'message': 'Guest checkout not yet implemented. Please create an account.'
    }), 501
