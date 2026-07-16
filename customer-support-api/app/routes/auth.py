from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from marshmallow import ValidationError

from app import db, limiter
from app.models.user import User
from app.models.customer import Customer
from app.models.agent import Agent
from app.schemas.user import UserSchema, UserLoginSchema
from app.schemas.customer import CustomerCreateSchema
from app.utils.errors import UnauthorizedError, ConflictError
from app.utils.security import get_current_user

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()
user_login_schema = UserLoginSchema()
customer_create_schema = CustomerCreateSchema()


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """
    Register a new customer account
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: John Doe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: SecurePass123
            phone:
              type: string
              example: "+1234567890"
            company:
              type: string
              example: Acme Inc
    responses:
      201:
        description: Customer registered successfully
      400:
        description: Validation error
      409:
        description: Email already registered
    """
    try:
        data = customer_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    if User.query.filter_by(email=data['email']).first():
        raise ConflictError('Email already registered')
    
    customer = Customer(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        company=data.get('company'),
        role='customer'
    )
    customer.set_password(data['password'])
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Customer registered successfully',
        'data': user_schema.dump(customer)
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """
    Login and get JWT tokens
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: SecurePass123
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    try:
        data = user_login_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        raise UnauthorizedError('Invalid email or password')
    
    if not user.is_active:
        raise UnauthorizedError('Account is deactivated')
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'status': 'success',
        'data': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_schema.dump(user)
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: New access token
      401:
        description: Invalid refresh token
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({
        'status': 'success',
        'data': {'access_token': access_token}
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """
    Get current user profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Current user data
      401:
        description: Unauthorized
    """
    user = get_current_user()
    if not user:
        raise UnauthorizedError('User not found')
    
    return jsonify({
        'status': 'success',
        'data': user_schema.dump(user)
    }), 200
