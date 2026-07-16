"""
Sentry Error Tracking Integration
Provides error tracking, performance monitoring, and release tracking.
"""

import os
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def init_sentry(app):
    """Initialize Sentry SDK for error tracking and performance monitoring."""
    
    sentry_dsn = app.config.get('SENTRY_DSN') or os.environ.get('SENTRY_DSN')
    
    if not sentry_dsn:
        logger.warning("SENTRY_DSN not configured. Sentry error tracking disabled.")
        return False
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                logging_integration,
            ],
            # Performance monitoring
            traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
            profiles_sample_rate=float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),
            
            # Release tracking
            release=app.config.get('VERSION', os.environ.get('APP_VERSION', '1.0.0')),
            environment=app.config.get('ENV', os.environ.get('FLASK_ENV', 'development')),
            
            # Additional options
            send_default_pii=False,
            attach_stacktrace=True,
            
            # Filter sensitive data
            before_send=_before_send,
            before_send_transaction=_before_send_transaction,
        )
        
        logger.info(f"Sentry initialized for environment: {app.config.get('ENV', 'development')}")
        return True
        
    except ImportError:
        logger.warning("sentry-sdk not installed. Run: pip install sentry-sdk[flask]")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def _before_send(event, hint):
    """Filter and modify events before sending to Sentry."""
    
    # Remove sensitive data from request
    if 'request' in event:
        request_data = event['request']
        
        # Remove sensitive headers
        if 'headers' in request_data:
            sensitive_headers = ['authorization', 'cookie', 'x-api-key']
            for header in sensitive_headers:
                if header in request_data['headers']:
                    request_data['headers'][header] = '[FILTERED]'
        
        # Remove sensitive body fields
        if 'data' in request_data and isinstance(request_data['data'], dict):
            sensitive_fields = ['password', 'token', 'secret', 'api_key', 'credit_card']
            for field in sensitive_fields:
                if field in request_data['data']:
                    request_data['data'][field] = '[FILTERED]'
    
    # Add custom tags
    if 'tags' not in event:
        event['tags'] = {}
    
    return event


def _before_send_transaction(event, hint):
    """Filter transactions before sending."""
    
    # Skip health check endpoints from performance monitoring
    if 'transaction' in event:
        skip_endpoints = ['/health', '/ready', '/live', '/metrics']
        if any(event['transaction'].endswith(ep) for ep in skip_endpoints):
            return None
    
    return event


def capture_exception(error, **kwargs):
    """Capture an exception and send to Sentry."""
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(error, **kwargs)
    except ImportError:
        logger.error(f"Exception occurred (Sentry not available): {error}")


def capture_message(message, level='info', **kwargs):
    """Capture a message and send to Sentry."""
    try:
        import sentry_sdk
        sentry_sdk.capture_message(message, level=level, **kwargs)
    except ImportError:
        logger.log(getattr(logging, level.upper(), logging.INFO), message)


def set_user(user_id, email=None, username=None):
    """Set user context for Sentry events."""
    try:
        import sentry_sdk
        sentry_sdk.set_user({
            'id': str(user_id),
            'email': email,
            'username': username
        })
    except ImportError:
        pass


def set_tag(key, value):
    """Set a tag for the current scope."""
    try:
        import sentry_sdk
        sentry_sdk.set_tag(key, value)
    except ImportError:
        pass


def set_context(name, data):
    """Set additional context for the current scope."""
    try:
        import sentry_sdk
        sentry_sdk.set_context(name, data)
    except ImportError:
        pass


def track_performance(operation_name):
    """Decorator to track performance of a function."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                import sentry_sdk
                with sentry_sdk.start_span(op="function", description=operation_name):
                    return f(*args, **kwargs)
            except ImportError:
                return f(*args, **kwargs)
        return decorated_function
    return decorator


class SentrySpan:
    """Context manager for creating Sentry spans."""
    
    def __init__(self, op, description):
        self.op = op
        self.description = description
        self.span = None
    
    def __enter__(self):
        try:
            import sentry_sdk
            self.span = sentry_sdk.start_span(op=self.op, description=self.description)
            self.span.__enter__()
        except ImportError:
            pass
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            self.span.__exit__(exc_type, exc_val, exc_tb)
        return False
    
    def set_data(self, key, value):
        """Set data on the span."""
        if self.span:
            self.span.set_data(key, value)
    
    def set_status(self, status):
        """Set status on the span."""
        if self.span:
            self.span.set_status(status)
