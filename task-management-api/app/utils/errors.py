from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError


class APIError(Exception):
    """Base API error class."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv


class NotFoundError(APIError):
    """Resource not found error."""
    def __init__(self, message='Resource not found'):
        super().__init__(message, status_code=404)


class UnauthorizedError(APIError):
    """Unauthorized access error."""
    def __init__(self, message='Unauthorized'):
        super().__init__(message, status_code=401)


class ForbiddenError(APIError):
    """Forbidden access error."""
    def __init__(self, message='Access denied'):
        super().__init__(message, status_code=403)


class ConflictError(APIError):
    """Resource conflict error."""
    def __init__(self, message='Resource already exists'):
        super().__init__(message, status_code=409)


def register_error_handlers(app):
    """Register error handlers for the Flask app."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            'error': 'Validation error',
            'details': error.messages,
            'status_code': 400
        }), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        return jsonify({
            'error': 'Database integrity error',
            'message': 'A resource with this data already exists',
            'status_code': 409
        }), 409
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            'error': 'Method not allowed',
            'message': 'The method is not allowed for this endpoint',
            'status_code': 405
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
