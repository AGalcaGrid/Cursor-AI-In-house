from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.user import User
from app.schemas.user import UserSchema, UserCreateSchema, UserLoginSchema
from app.utils.errors import UnauthorizedError, ValidationError as APIValidationError

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
            role:
              type: string
              enum: [customer, agent, admin]
              default: customer
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
    """
    try:
        data = user_create_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    user = User(
        name=data['name'],
        email=data['email'],
        role=data.get('role', 'customer')
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
        raise APIValidationError('Validation failed', errors=err.messages)
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        raise UnauthorizedError('Invalid email or password')
    
    if not user.is_active:
        raise UnauthorizedError('Account is deactivated')
    
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


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client should discard token)
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
    """
    return jsonify({
        'status': 'success',
        'message': 'Logout successful'
    }), 200


@auth_bp.route('/notification-preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """
    Get user notification preferences (FR-037)
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Notification preferences
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(int(current_user_id))
    
    # Return default preferences if not set
    preferences = user.notification_preferences or {
        'email_ticket_created': True,
        'email_ticket_assigned': True,
        'email_status_changed': True,
        'email_new_comment': True,
        'email_sla_warning': True,
        'email_sla_breach': True,
        'email_mentions': True,
        'in_app_notifications': True
    }
    
    return jsonify({
        'status': 'success',
        'preferences': preferences
    }), 200


@auth_bp.route('/notification-preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    """
    Update user notification preferences (FR-037)
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            email_ticket_created:
              type: boolean
            email_ticket_assigned:
              type: boolean
            email_status_changed:
              type: boolean
            email_new_comment:
              type: boolean
            email_sla_warning:
              type: boolean
            email_sla_breach:
              type: boolean
            email_mentions:
              type: boolean
            in_app_notifications:
              type: boolean
    responses:
      200:
        description: Preferences updated
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(int(current_user_id))
    
    data = request.json
    
    # Get current preferences or defaults
    current_prefs = user.notification_preferences or {}
    
    # Update only provided fields
    valid_keys = [
        'email_ticket_created', 'email_ticket_assigned', 'email_status_changed',
        'email_new_comment', 'email_sla_warning', 'email_sla_breach',
        'email_mentions', 'in_app_notifications'
    ]
    
    for key in valid_keys:
        if key in data:
            current_prefs[key] = bool(data[key])
    
    user.notification_preferences = current_prefs
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Notification preferences updated',
        'preferences': user.notification_preferences
    }), 200
