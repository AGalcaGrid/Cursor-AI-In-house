from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.user import User
from app.schemas.user import UserSchema, UserCreateSchema, UserLoginSchema
from app.utils.errors import UnauthorizedError, ConflictError, ValidationError as APIValidationError

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()
user_create_schema = UserCreateSchema()
user_login_schema = UserLoginSchema()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
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
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: johndoe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: securepassword123
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
      409:
        description: Username or email already exists
    """
    try:
        data = user_create_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'User registered successfully',
        'user': user_schema.dump(user)
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and get JWT tokens
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
              example: securepassword123
    responses:
      200:
        description: Login successful
      400:
        description: Validation error
      401:
        description: Invalid credentials
    """
    try:
        data = user_login_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        raise UnauthorizedError('Invalid email or password')
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user_schema.dump(user)
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Current user profile
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(int(current_user_id))
    
    return jsonify({
        'status': 'success',
        'user': user_schema.dump(user)
    }), 200
