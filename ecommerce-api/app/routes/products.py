from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app import db
from app.models.product import Product
from app.schemas.product import ProductSchema, ProductCreateSchema, ProductUpdateSchema
from app.utils.errors import NotFoundError, ValidationError as CustomValidationError

products_bp = Blueprint('products', __name__)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_create_schema = ProductCreateSchema()
product_update_schema = ProductUpdateSchema()


@products_bp.route('', methods=['GET'])
def get_products():
    """Get all products with filtering and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    category = request.args.get('category')
    search = request.args.get('search')
    is_featured = request.args.get('is_featured', type=bool)
    in_stock_only = request.args.get('in_stock_only', type=bool)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.brand.ilike(search_term)
            )
        )
    
    if is_featured is not None:
        query = query.filter_by(is_featured=is_featured)
    
    if in_stock_only:
        query = query.filter(Product.stock_quantity > 0)
    
    # Sorting
    sort_column = getattr(Product, sort_by, Product.created_at)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'status': 'success',
        'data': {
            'products': products_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total
            }
        }
    }), 200


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID."""
    product = Product.query.get(product_id)
    
    if not product or not product.is_active:
        raise NotFoundError('Product not found')
    
    return jsonify({
        'status': 'success',
        'data': product_schema.dump(product)
    }), 200


@products_bp.route('', methods=['POST'])
def create_product():
    """Create a new product (admin only in production)."""
    try:
        data = product_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    # Check if SKU already exists
    if Product.query.filter_by(sku=data['sku']).first():
        raise CustomValidationError('Product with this SKU already exists')
    
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Product created successfully',
        'data': product_schema.dump(product)
    }), 201


@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product (admin only in production)."""
    product = Product.query.get(product_id)
    
    if not product:
        raise NotFoundError('Product not found')
    
    try:
        data = product_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    for key, value in data.items():
        setattr(product, key, value)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Product updated successfully',
        'data': product_schema.dump(product)
    }), 200


@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Soft delete product (admin only in production)."""
    product = Product.query.get(product_id)
    
    if not product:
        raise NotFoundError('Product not found')
    
    product.is_active = False
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Product deleted successfully'
    }), 200


@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories."""
    categories = db.session.query(Product.category).filter(
        Product.category.isnot(None),
        Product.is_active == True
    ).distinct().all()
    
    category_list = [cat[0] for cat in categories if cat[0]]
    
    return jsonify({
        'status': 'success',
        'data': {'categories': sorted(category_list)}
    }), 200
