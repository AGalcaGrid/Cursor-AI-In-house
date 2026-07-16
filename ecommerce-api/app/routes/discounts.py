from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app import db
from app.models.discount import DiscountCode
from app.schemas.discount import DiscountCodeSchema, DiscountCodeCreateSchema, ValidateDiscountSchema
from app.utils.errors import NotFoundError, ValidationError as CustomValidationError

discounts_bp = Blueprint('discounts', __name__)
discount_code_schema = DiscountCodeSchema()
discount_codes_schema = DiscountCodeSchema(many=True)
discount_code_create_schema = DiscountCodeCreateSchema()
validate_discount_schema = ValidateDiscountSchema()


@discounts_bp.route('/validate', methods=['POST'])
def validate_discount():
    """Validate a discount code."""
    try:
        data = validate_discount_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    discount_code = DiscountCode.query.filter_by(code=data['code'].upper()).first()
    
    if not discount_code:
        raise NotFoundError('Invalid discount code')
    
    if not discount_code.is_valid:
        raise CustomValidationError('Discount code is not valid or has expired')
    
    # Check minimum purchase amount
    if discount_code.min_purchase_amount and data['cart_total'] < discount_code.min_purchase_amount:
        raise CustomValidationError(
            f'Minimum purchase amount of ${discount_code.min_purchase_amount} required'
        )
    
    # Calculate discount amount
    if discount_code.discount_type == 'percentage':
        discount_amount = data['cart_total'] * (discount_code.discount_value / 100)
        if discount_code.max_discount_amount:
            discount_amount = min(discount_amount, discount_code.max_discount_amount)
    else:  # fixed
        discount_amount = min(discount_code.discount_value, data['cart_total'])
    
    return jsonify({
        'status': 'success',
        'data': {
            'discount_code': discount_code_schema.dump(discount_code),
            'discount_amount': float(discount_amount),
            'final_total': float(data['cart_total'] - discount_amount)
        }
    }), 200


@discounts_bp.route('', methods=['POST'])
def create_discount():
    """Create a new discount code (admin only in production)."""
    try:
        data = discount_code_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    # Check if code already exists
    if DiscountCode.query.filter_by(code=data['code'].upper()).first():
        raise CustomValidationError('Discount code already exists')
    
    data['code'] = data['code'].upper()
    discount_code = DiscountCode(**data)
    
    db.session.add(discount_code)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Discount code created successfully',
        'data': discount_code_schema.dump(discount_code)
    }), 201


@discounts_bp.route('', methods=['GET'])
def get_discounts():
    """Get all discount codes (admin only in production)."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    is_active = request.args.get('is_active', type=bool)
    
    query = DiscountCode.query
    
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    pagination = query.order_by(DiscountCode.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'status': 'success',
        'data': {
            'discount_codes': discount_codes_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total
            }
        }
    }), 200
