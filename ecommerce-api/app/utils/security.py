import re
import bleach
from functools import wraps
from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.utils.errors import UnauthorizedError, ForbiddenError


def sanitize_input(data):
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        data: Input data (string, dict, or list)
    
    Returns:
        Sanitized data
    """
    if isinstance(data, str):
        return bleach.clean(data, tags=[], strip=True)
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data


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


def jwt_required_optional(f):
    """
    Decorator for optional JWT authentication.
    Allows both authenticated and guest users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except:
            pass
        return f(*args, **kwargs)
    return decorated_function


def validate_card_number(card_number):
    """
    Validate credit card number using Luhn algorithm.
    
    Args:
        card_number: Card number string
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Remove spaces and dashes
    card_number = re.sub(r'[\s-]', '', str(card_number))
    
    # Check if only digits
    if not card_number.isdigit():
        return False
    
    # Check length (13-19 digits)
    if len(card_number) < 13 or len(card_number) > 19:
        return False
    
    # Luhn algorithm
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0


def mask_card_number(card_number):
    """
    Mask card number, showing only last 4 digits.
    
    Args:
        card_number: Card number string
    
    Returns:
        str: Masked card number
    """
    card_number = re.sub(r'[\s-]', '', str(card_number))
    if len(card_number) < 4:
        return '****'
    return '*' * (len(card_number) - 4) + card_number[-4:]
