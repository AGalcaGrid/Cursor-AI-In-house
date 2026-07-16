import html
import re
from functools import wraps
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
import bleach

from app.utils.errors import ForbiddenError, UnauthorizedError


def sanitize_input(data):
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        data: Input data (string, dict, or list)
    
    Returns:
        Sanitized data
    """
    if isinstance(data, str):
        # Use bleach to clean HTML and escape dangerous content
        return bleach.clean(data, tags=[], strip=True)
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data


def sanitize_html(data, allowed_tags=None):
    """
    Sanitize HTML content allowing specific tags.
    
    Args:
        data: HTML string
        allowed_tags: List of allowed HTML tags
    
    Returns:
        Sanitized HTML string
    """
    if allowed_tags is None:
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a']
    
    allowed_attrs = {
        'a': ['href', 'title'],
    }
    
    return bleach.clean(data, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def get_current_user():
    """
    Get the current authenticated user from JWT.
    
    Returns:
        User object or None
    """
    from app.models.user import User
    
    try:
        user_id = int(get_jwt_identity())
        return User.query.get(user_id)
    except (TypeError, ValueError):
        return None


def role_required(*roles):
    """
    Decorator to require specific user roles.
    
    Args:
        *roles: Allowed roles (e.g., 'admin', 'agent', 'customer')
    
    Usage:
        @role_required('admin', 'agent')
        def admin_only_route():
            pass
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            
            if user is None:
                raise UnauthorizedError('Authentication required')
            
            if not user.is_active:
                raise ForbiddenError('Account is deactivated')
            
            if user.role not in roles:
                raise ForbiddenError(f'Requires one of these roles: {", ".join(roles)}')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    return role_required('admin')(f)


def agent_required(f):
    """Decorator to require agent or admin role."""
    return role_required('agent', 'admin')(f)


def customer_required(f):
    """Decorator to require customer role."""
    return role_required('customer')(f)


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email string to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password):
    """
    Validate password strength.
    
    Args:
        password: Password string to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'
    
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'
    
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one digit'
    
    return True, None
