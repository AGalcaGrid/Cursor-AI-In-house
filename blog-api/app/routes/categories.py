from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.category import Category
from app.schemas.category import CategorySchema

categories_bp = Blueprint('categories', __name__)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


@categories_bp.route('', methods=['GET'])
def get_categories():
    """
    Get all categories
    ---
    tags:
      - Categories
    responses:
      200:
        description: List of categories
    """
    categories = Category.query.order_by(Category.name).all()
    
    return jsonify({
        'status': 'success',
        'categories': categories_schema.dump(categories)
    }), 200


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get a single category by ID
    ---
    tags:
      - Categories
    parameters:
      - in: path
        name: category_id
        type: integer
        required: true
    responses:
      200:
        description: Category details
      404:
        description: Category not found
    """
    category = Category.query.get_or_404(category_id)
    
    return jsonify({
        'status': 'success',
        'category': category_schema.dump(category)
    }), 200
