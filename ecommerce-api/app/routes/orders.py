from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models.order import Order
from app.schemas.order import OrderSchema
from app.utils.errors import NotFoundError, ForbiddenError
from app.utils.security import get_current_user
from app.services.email_service import EmailService

orders_bp = Blueprint('orders', __name__)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get all orders for current user."""
    user = get_current_user()
    if not user:
        raise NotFoundError('User not found')
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status')
    
    query = Order.query.filter_by(user_id=user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'status': 'success',
        'data': {
            'orders': orders_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total
            }
        }
    }), 200


@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get single order by ID."""
    user = get_current_user()
    if not user:
        raise NotFoundError('User not found')
    
    order = Order.query.get(order_id)
    
    if not order:
        raise NotFoundError('Order not found')
    
    if order.user_id != user.id:
        raise ForbiddenError('Access denied')
    
    return jsonify({
        'status': 'success',
        'data': order_schema.dump(order)
    }), 200


@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order."""
    user = get_current_user()
    if not user:
        raise NotFoundError('User not found')
    
    order = Order.query.get(order_id)
    
    if not order:
        raise NotFoundError('Order not found')
    
    if order.user_id != user.id:
        raise ForbiddenError('Access denied')
    
    if not order.can_be_cancelled:
        raise ForbiddenError('Order cannot be cancelled at this stage')
    
    # Restore stock
    for item in order.items:
        item.product.increase_stock(item.quantity)
    
    order.update_status('cancelled')
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Order cancelled successfully',
        'data': order_schema.dump(order)
    }), 200


@orders_bp.route('/<string:order_number>', methods=['GET'])
@jwt_required()
def get_order_by_number(order_number):
    """Get order by order number."""
    user = get_current_user()
    if not user:
        raise NotFoundError('User not found')
    
    order = Order.query.filter_by(order_number=order_number).first()
    
    if not order:
        raise NotFoundError('Order not found')
    
    if order.user_id != user.id:
        raise ForbiddenError('Access denied')
    
    return jsonify({
        'status': 'success',
        'data': order_schema.dump(order)
    }), 200
