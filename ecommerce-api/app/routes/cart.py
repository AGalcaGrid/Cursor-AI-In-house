from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import secrets

from app import db
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.discount import DiscountCode
from app.schemas.cart import CartSchema, AddToCartSchema, UpdateCartItemSchema, ApplyDiscountSchema
from app.utils.errors import NotFoundError, StockError, ValidationError as CustomValidationError
from app.utils.security import jwt_required_optional, get_current_user

cart_bp = Blueprint('cart', __name__)
cart_schema = CartSchema()
add_to_cart_schema = AddToCartSchema()
update_cart_item_schema = UpdateCartItemSchema()
apply_discount_schema = ApplyDiscountSchema()


def get_or_create_cart():
    """Get or create cart for current user or session."""
    user = get_current_user()
    
    if user:
        # Authenticated user
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()
    else:
        # Guest user - use session
        session_id = session.get('cart_session_id')
        if not session_id:
            session_id = secrets.token_hex(16)
            session['cart_session_id'] = session_id
        
        cart = Cart.query.filter_by(session_id=session_id).first()
        if not cart:
            cart = Cart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()
    
    # Check if cart is expired
    if cart.is_expired:
        cart.clear()
        db.session.commit()
    
    return cart


@cart_bp.route('', methods=['GET'])
@jwt_required_optional
def get_cart():
    """Get current cart."""
    cart = get_or_create_cart()
    
    return jsonify({
        'status': 'success',
        'data': cart_schema.dump(cart)
    }), 200


@cart_bp.route('/items', methods=['POST'])
@jwt_required_optional
def add_to_cart():
    """Add item to cart."""
    try:
        data = add_to_cart_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    cart = get_or_create_cart()
    product = Product.query.get(data['product_id'])
    
    if not product or not product.is_active:
        raise NotFoundError('Product not found')
    
    if not product.in_stock:
        raise StockError('Product is out of stock')
    
    success, message = cart.add_item(product, data['quantity'])
    
    if not success:
        raise CustomValidationError(message)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': message,
        'data': cart_schema.dump(cart)
    }), 200


@cart_bp.route('/items/<int:product_id>', methods=['PUT'])
@jwt_required_optional
def update_cart_item(product_id):
    """Update cart item quantity."""
    try:
        data = update_cart_item_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    cart = get_or_create_cart()
    
    success, message = cart.update_item_quantity(product_id, data['quantity'])
    
    if not success:
        raise CustomValidationError(message)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': message,
        'data': cart_schema.dump(cart)
    }), 200


@cart_bp.route('/items/<int:product_id>', methods=['DELETE'])
@jwt_required_optional
def remove_from_cart(product_id):
    """Remove item from cart."""
    cart = get_or_create_cart()
    
    success = cart.remove_item(product_id)
    
    if not success:
        raise NotFoundError('Item not found in cart')
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Item removed from cart',
        'data': cart_schema.dump(cart)
    }), 200


@cart_bp.route('/clear', methods=['POST'])
@jwt_required_optional
def clear_cart():
    """Clear all items from cart."""
    cart = get_or_create_cart()
    cart.clear()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Cart cleared',
        'data': cart_schema.dump(cart)
    }), 200


@cart_bp.route('/discount', methods=['POST'])
@jwt_required_optional
def apply_discount():
    """Apply discount code to cart."""
    try:
        data = apply_discount_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    cart = get_or_create_cart()
    
    discount_code = DiscountCode.query.filter_by(code=data['code'].upper()).first()
    
    if not discount_code:
        raise NotFoundError('Invalid discount code')
    
    if not discount_code.is_valid:
        raise CustomValidationError('Discount code is not valid or has expired')
    
    # Check minimum purchase amount
    if discount_code.min_purchase_amount and cart.subtotal < discount_code.min_purchase_amount:
        raise CustomValidationError(
            f'Minimum purchase amount of ${discount_code.min_purchase_amount} required'
        )
    
    # Check user usage limit (if authenticated)
    user = get_current_user()
    if user:
        can_use, message = discount_code.can_be_used_by_user(user.id)
        if not can_use:
            raise CustomValidationError(message)
    
    cart.discount_code_id = discount_code.id
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Discount code applied',
        'data': cart_schema.dump(cart)
    }), 200


@cart_bp.route('/discount', methods=['DELETE'])
@jwt_required_optional
def remove_discount():
    """Remove discount code from cart."""
    cart = get_or_create_cart()
    cart.discount_code_id = None
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Discount code removed',
        'data': cart_schema.dump(cart)
    }), 200
