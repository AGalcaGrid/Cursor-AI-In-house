"""
Prometheus Metrics for Flask Application
Provides application-level metrics for monitoring and alerting.
"""

import time
from functools import wraps
from flask import request, g, Response
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry, multiprocess
)
import os


# Create a custom registry for multiprocess mode
def get_registry():
    """Get the appropriate registry based on environment."""
    if 'prometheus_multiproc_dir' in os.environ:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return registry
    return None


# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

REQUEST_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

# Application metrics
ACTIVE_USERS = Gauge(
    'app_active_users',
    'Number of active users (with valid sessions)'
)

TICKETS_TOTAL = Gauge(
    'app_tickets_total',
    'Total number of tickets',
    ['status', 'priority']
)

TICKETS_CREATED = Counter(
    'app_tickets_created_total',
    'Total tickets created',
    ['priority']
)

TICKETS_RESOLVED = Counter(
    'app_tickets_resolved_total',
    'Total tickets resolved'
)

# Database metrics
DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds',
    'Database query latency in seconds',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

DB_CONNECTIONS_ACTIVE = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

# Cache metrics
CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

# Error metrics
ERRORS_TOTAL = Counter(
    'app_errors_total',
    'Total application errors',
    ['error_type', 'endpoint']
)

# Application info
APP_INFO = Info(
    'app',
    'Application information'
)


def setup_metrics(app):
    """Initialize Prometheus metrics for the Flask application."""
    
    # Set application info
    APP_INFO.info({
        'name': 'support-ticket-api',
        'version': app.config.get('VERSION', '1.0.0'),
        'environment': app.config.get('ENV', 'development')
    })
    
    @app.before_request
    def before_request_metrics():
        """Track request start time and in-progress requests."""
        g.metrics_start_time = time.time()
        endpoint = _get_endpoint_label()
        REQUEST_IN_PROGRESS.labels(method=request.method, endpoint=endpoint).inc()
    
    @app.after_request
    def after_request_metrics(response):
        """Record request metrics after response."""
        endpoint = _get_endpoint_label()
        
        # Record request count
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
        
        # Record latency
        if hasattr(g, 'metrics_start_time'):
            latency = time.time() - g.metrics_start_time
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(latency)
        
        # Decrement in-progress
        REQUEST_IN_PROGRESS.labels(method=request.method, endpoint=endpoint).dec()
        
        return response
    
    @app.teardown_request
    def teardown_request_metrics(exception=None):
        """Track errors."""
        if exception:
            endpoint = _get_endpoint_label()
            ERRORS_TOTAL.labels(
                error_type=type(exception).__name__,
                endpoint=endpoint
            ).inc()
    
    # Register metrics endpoint
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint."""
        registry = get_registry()
        if registry:
            return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    
    # Register health endpoint
    @app.route('/health')
    def health():
        """Health check endpoint for load balancers and monitoring."""
        from app import db
        
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {}
        }
        
        # Database check
        try:
            db.session.execute(db.text('SELECT 1'))
            health_status['checks']['database'] = {'status': 'healthy'}
        except Exception as e:
            health_status['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'unhealthy'
        
        # Cache check (if Redis is configured)
        try:
            from app import cache
            if hasattr(cache, 'cache') and hasattr(cache.cache, '_read_client'):
                cache.cache._read_client.ping()
                health_status['checks']['cache'] = {'status': 'healthy'}
        except Exception as e:
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        from flask import jsonify
        return jsonify(health_status), status_code
    
    # Readiness endpoint
    @app.route('/ready')
    def ready():
        """Readiness check for Kubernetes."""
        from flask import jsonify
        return jsonify({'status': 'ready'}), 200
    
    # Liveness endpoint
    @app.route('/live')
    def live():
        """Liveness check for Kubernetes."""
        from flask import jsonify
        return jsonify({'status': 'alive'}), 200


def _get_endpoint_label():
    """Get a normalized endpoint label for metrics."""
    if request.endpoint:
        return request.endpoint
    # Fallback to path with IDs replaced
    path = request.path
    # Replace numeric IDs with placeholder
    import re
    path = re.sub(r'/\d+', '/:id', path)
    return path


def track_db_query(operation: str):
    """Decorator to track database query latency."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                latency = time.time() - start_time
                DB_QUERY_LATENCY.labels(operation=operation).observe(latency)
        return decorated_function
    return decorator


def track_cache(cache_name: str):
    """Context manager to track cache hits/misses."""
    class CacheTracker:
        def __init__(self):
            self.hit = False
        
        def record_hit(self):
            self.hit = True
            CACHE_HITS.labels(cache_name=cache_name).inc()
        
        def record_miss(self):
            CACHE_MISSES.labels(cache_name=cache_name).inc()
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if not self.hit:
                self.record_miss()
            return False
    
    return CacheTracker()


def update_ticket_metrics(status: str, priority: str, delta: int = 1):
    """Update ticket gauge metrics."""
    TICKETS_TOTAL.labels(status=status, priority=priority).inc(delta)


def record_ticket_created(priority: str):
    """Record a new ticket creation."""
    TICKETS_CREATED.labels(priority=priority).inc()


def record_ticket_resolved():
    """Record a ticket resolution."""
    TICKETS_RESOLVED.inc()
