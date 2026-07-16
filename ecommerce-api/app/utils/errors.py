from flask import jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError as MarshmallowValidationError


class APIError(Exception):
    """Base API error class."""
    status_code = 400
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status'] = 'error'
        rv['message'] = self.message
        return rv


class ValidationError(APIError):
    """Validation error."""
    status_code = 400


class NotFoundError(APIError):
    """Resource not found error."""
    status_code = 404


class UnauthorizedError(APIError):
    """Unauthorized access error."""
    status_code = 401


class ForbiddenError(APIError):
    """Forbidden access error."""
    status_code = 403


class ConflictError(APIError):
    """Resource conflict error."""
    status_code = 409


class PaymentError(APIError):
    """Payment processing error."""
    status_code = 402


class StockError(APIError):
    """Insufficient stock error."""
    status_code = 409


def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_error(error):
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'errors': error.messages
        }), 400
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            'status': 'error',
            'message': error.description
        }), error.code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
