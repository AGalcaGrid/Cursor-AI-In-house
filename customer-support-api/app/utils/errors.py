from flask import jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy.exc import IntegrityError


class APIException(Exception):
    """Base API exception class."""
    status_code = 500
    code = 'INTERNAL_ERROR'
    
    def __init__(self, message='An error occurred', status_code=None, code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status'] = 'error'
        rv['message'] = self.message
        rv['code'] = self.code
        return rv


class ValidationException(APIException):
    """Validation error exception."""
    status_code = 400
    code = 'VALIDATION_ERROR'
    
    def __init__(self, message='Validation failed', errors=None):
        super().__init__(message)
        self.errors = errors or {}
    
    def to_dict(self):
        rv = super().to_dict()
        rv['errors'] = self.errors
        return rv


class NotFoundError(APIException):
    """Resource not found exception."""
    status_code = 404
    code = 'NOT_FOUND'
    
    def __init__(self, message='Resource not found'):
        super().__init__(message)


class UnauthorizedError(APIException):
    """Unauthorized access exception."""
    status_code = 401
    code = 'UNAUTHORIZED'
    
    def __init__(self, message='Authentication required'):
        super().__init__(message)


class ForbiddenError(APIException):
    """Forbidden access exception."""
    status_code = 403
    code = 'FORBIDDEN'
    
    def __init__(self, message='Insufficient permissions'):
        super().__init__(message)


class ConflictError(APIException):
    """Resource conflict exception."""
    status_code = 409
    code = 'CONFLICT'
    
    def __init__(self, message='Resource already exists'):
        super().__init__(message)


class InvalidStatusTransition(APIException):
    """Invalid ticket status transition."""
    status_code = 400
    code = 'INVALID_STATUS_TRANSITION'
    
    def __init__(self, current_status, new_status):
        message = f"Cannot transition from '{current_status}' to '{new_status}'"
        super().__init__(message)


class RateLimitExceeded(APIException):
    """Rate limit exceeded exception."""
    status_code = 429
    code = 'RATE_LIMIT_EXCEEDED'
    
    def __init__(self, message='Too many requests. Please try again later.'):
        super().__init__(message)


def register_error_handlers(app):
    """Register error handlers for the Flask app."""
    
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation_error(error):
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'message': 'Validation failed',
            'errors': error.messages
        }), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        return jsonify({
            'status': 'error',
            'code': 'CONFLICT',
            'message': 'A resource with this data already exists'
        }), 409
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'status': 'error',
            'code': 'NOT_FOUND',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            'status': 'error',
            'code': 'METHOD_NOT_ALLOWED',
            'message': 'The method is not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(429)
    def handle_rate_limit(error):
        return jsonify({
            'status': 'error',
            'code': 'RATE_LIMIT_EXCEEDED',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'status': 'error',
            'code': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred'
        }), 500
