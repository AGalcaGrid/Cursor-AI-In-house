from flask import jsonify


class APIError(Exception):
    """Base API error class."""
    status_code = 400
    
    def __init__(self, message, status_code=None, errors=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.errors = errors
    
    def to_dict(self):
        rv = {'status': 'error', 'message': self.message}
        if self.errors:
            rv['errors'] = self.errors
        return rv


class ValidationError(APIError):
    """Validation error."""
    status_code = 400


class NotFoundError(APIError):
    """Resource not found error."""
    status_code = 404


class UnauthorizedError(APIError):
    """Unauthorized error."""
    status_code = 401


class ForbiddenError(APIError):
    """Forbidden error."""
    status_code = 403


class ConflictError(APIError):
    """Conflict error (e.g., duplicate resource)."""
    status_code = 409


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
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
