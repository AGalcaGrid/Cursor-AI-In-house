import logging
import time
import uuid
from functools import wraps
from flask import request, g, current_app
from datetime import datetime

logger = logging.getLogger('api.requests')

def setup_request_logging(app):
    """Configure request/response logging for the Flask application."""
    
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    if app.config.get('LOG_TO_FILE', False):
        file_handler = logging.FileHandler('logs/api_requests.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

    @app.before_request
    def before_request():
        """Log incoming request details and start timing."""
        g.request_id = str(uuid.uuid4())[:8]
        g.request_start_time = time.time()
        
        log_data = {
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'query_string': request.query_string.decode('utf-8') if request.query_string else None,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')[:100],
            'content_type': request.content_type,
            'content_length': request.content_length,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        if request.is_json and request.data:
            try:
                body = request.get_json(silent=True)
                if body:
                    sanitized_body = _sanitize_request_body(body)
                    log_data['body'] = sanitized_body
            except Exception:
                pass
        
        logger.info(f"[{g.request_id}] --> {request.method} {request.path} | "
                   f"IP: {request.remote_addr} | "
                   f"Content-Length: {request.content_length or 0}")
        
        if current_app.debug:
            logger.debug(f"[{g.request_id}] Request details: {log_data}")

    @app.after_request
    def after_request(response):
        """Log response details and timing."""
        request_duration = time.time() - getattr(g, 'request_start_time', time.time())
        request_id = getattr(g, 'request_id', 'unknown')
        
        log_data = {
            'request_id': request_id,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'content_type': response.content_type,
            'content_length': response.content_length,
            'duration_ms': round(request_duration * 1000, 2),
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        log_level = logging.INFO
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING
        
        logger.log(log_level, 
                  f"[{request_id}] <-- {request.method} {request.path} | "
                  f"Status: {response.status_code} | "
                  f"Duration: {log_data['duration_ms']}ms | "
                  f"Size: {response.content_length or 0} bytes")
        
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Response-Time'] = f"{log_data['duration_ms']}ms"
        
        if current_app.debug:
            logger.debug(f"[{request_id}] Response details: {log_data}")
        
        return response

    @app.teardown_request
    def teardown_request(exception=None):
        """Log any exceptions that occurred during request processing."""
        if exception:
            request_id = getattr(g, 'request_id', 'unknown')
            logger.error(f"[{request_id}] Exception during request: {str(exception)}", 
                        exc_info=True)


def _sanitize_request_body(body: dict) -> dict:
    """Remove sensitive fields from request body for logging."""
    sensitive_fields = {'password', 'token', 'secret', 'api_key', 'authorization', 
                       'credit_card', 'ssn', 'refresh_token', 'access_token'}
    
    if not isinstance(body, dict):
        return body
    
    sanitized = {}
    for key, value in body.items():
        if key.lower() in sensitive_fields:
            sanitized[key] = '[REDACTED]'
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_request_body(value)
        elif isinstance(value, list):
            sanitized[key] = [_sanitize_request_body(item) if isinstance(item, dict) else item 
                            for item in value]
        else:
            sanitized[key] = value
    
    return sanitized


def log_slow_request(threshold_ms: float = 1000):
    """Decorator to log slow requests that exceed the threshold."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            if duration_ms > threshold_ms:
                request_id = getattr(g, 'request_id', 'unknown')
                logger.warning(f"[{request_id}] SLOW REQUEST: {request.method} {request.path} "
                             f"took {duration_ms:.2f}ms (threshold: {threshold_ms}ms)")
            
            return result
        return decorated_function
    return decorator


class RequestLogger:
    """Context manager for logging specific operations within a request."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.request_id = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.request_id = getattr(g, 'request_id', 'unknown')
        logger.debug(f"[{self.request_id}] Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type:
            logger.error(f"[{self.request_id}] Operation '{self.operation_name}' failed "
                        f"after {duration_ms:.2f}ms: {exc_val}")
        else:
            logger.debug(f"[{self.request_id}] Operation '{self.operation_name}' "
                        f"completed in {duration_ms:.2f}ms")
        
        return False
