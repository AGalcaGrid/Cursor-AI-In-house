from flask import jsonify


class APIError(Exception):
    """Base API error class."""
    status_code = 400
    code = 'ERROR'
    
    def __init__(self, message, status_code=None, code=None, errors=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.errors = errors
    
    def to_dict(self):
        rv = {
            'status': 'error',
            'message': self.message,
            'code': self.code
        }
        if self.errors:
            rv['errors'] = self.errors
        return rv


class ValidationError(APIError):
    """Validation error (400)."""
    status_code = 400
    code = 'VALIDATION_ERROR'


class UnauthorizedError(APIError):
    """Unauthorized error (401)."""
    status_code = 401
    code = 'UNAUTHORIZED'


class ForbiddenError(APIError):
    """Forbidden error (403)."""
    status_code = 403
    code = 'FORBIDDEN'


class NotFoundError(APIError):
    """Resource not found error (404)."""
    status_code = 404
    code = 'NOT_FOUND'


class ConflictError(APIError):
    """Conflict error (409)."""
    status_code = 409
    code = 'CONFLICT'


class RateLimitError(APIError):
    """Rate limit exceeded error (429)."""
    status_code = 429
    code = 'RATE_LIMIT_EXCEEDED'


def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found',
            'code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            'status': 'error',
            'message': 'Method not allowed',
            'code': 'METHOD_NOT_ALLOWED'
        }), 405
