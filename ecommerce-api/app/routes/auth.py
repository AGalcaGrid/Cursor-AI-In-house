from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db, limiter
from app.models.user import User
from app.schemas.user import UserSchema, UserRegistrationSchema, UserLoginSchema
from app.utils.errors import UnauthorizedError, ConflictError
from app.utils.security import get_current_user

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register a new user."""
    try:
        data = user_registration_schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': err.messages
        }), 400
    
    if User.query.filter_by(email=data['email']).first():
        raise ConflictError('Email already registered')
    
    user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'status': 'success',
        'message': 'User registered successfully',
        'data': {
            'user': user_schema.dump(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login user."""
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
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'status': 'success',
        'data': {
            'user': user_schema.dump(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({
        'status': 'success',
        'data': {'access_token': access_token}
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Get current user profile."""
    user = get_current_user()
    if not user:
        raise UnauthorizedError('User not found')
    
    return jsonify({
        'status': 'success',
        'data': user_schema.dump(user)
    }), 200
