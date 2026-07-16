# Monitoring & Observability Guide

This document describes the monitoring setup for the Support Ticket API.

## Table of Contents

- [Overview](#overview)
- [Prometheus Metrics](#prometheus-metrics)
- [Sentry Error Tracking](#sentry-error-tracking)
- [Health Checks](#health-checks)
- [Logging](#logging)
- [Configuration](#configuration)
- [Dashboards](#dashboards)
- [Alerting](#alerting)

---

## Overview

The application includes three monitoring layers:

| Layer | Tool | Purpose |
|-------|------|---------|
| **Metrics** | Prometheus | Request counts, latency, custom business metrics |
| **Error Tracking** | Sentry | Exception tracking, performance monitoring |
| **Logging** | Structured Logging | Request/response logs, operation tracking |

---

## Prometheus Metrics

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `/metrics` | Prometheus metrics endpoint |
| `/health` | Health check with component status |
| `/ready` | Kubernetes readiness probe |
| `/live` | Kubernetes liveness probe |

### Available Metrics

#### HTTP Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, endpoint, status_code | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | method, endpoint | Request latency |
| `http_requests_in_progress` | Gauge | method, endpoint | Current in-flight requests |

#### Application Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `app_tickets_total` | Gauge | status, priority | Total tickets by status/priority |
| `app_tickets_created_total` | Counter | priority | Tickets created |
| `app_tickets_resolved_total` | Counter | - | Tickets resolved |
| `app_active_users` | Gauge | - | Active user sessions |
| `app_errors_total` | Counter | error_type, endpoint | Application errors |

#### Database Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `db_query_duration_seconds` | Histogram | operation | Query latency |
| `db_connections_active` | Gauge | - | Active DB connections |

#### Cache Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `cache_hits_total` | Counter | cache_name | Cache hits |
| `cache_misses_total` | Counter | cache_name | Cache misses |

### Usage in Code

```python
from app.utils.metrics import (
    record_ticket_created,
    record_ticket_resolved,
    track_db_query,
    track_cache
)

# Record ticket creation
record_ticket_created(priority='high')

# Track database query
@track_db_query('get_ticket')
def get_ticket(ticket_id):
    return Ticket.query.get(ticket_id)

# Track cache
with track_cache('tickets') as cache_tracker:
    result = cache.get('ticket:123')
    if result:
        cache_tracker.record_hit()
```

### Prometheus Scrape Config

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'support-ticket-api'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

---

## Sentry Error Tracking

### Features

- **Exception Tracking**: Automatic capture of unhandled exceptions
- **Performance Monitoring**: Transaction tracing and profiling
- **Release Tracking**: Track errors by release version
- **User Context**: Associate errors with users

### Configuration

Set environment variables:

```bash
# Required
export SENTRY_DSN="https://xxx@xxx.ingest.sentry.io/xxx"

# Optional
export SENTRY_TRACES_SAMPLE_RATE="0.1"    # 10% of transactions
export SENTRY_PROFILES_SAMPLE_RATE="0.1"  # 10% profiling
export APP_VERSION="1.0.0"
export FLASK_ENV="production"
```

### Usage in Code

```python
from app.utils.sentry_integration import (
    capture_exception,
    capture_message,
    set_user,
    set_tag,
    track_performance,
    SentrySpan
)

# Capture exception manually
try:
    risky_operation()
except Exception as e:
    capture_exception(e)

# Capture message
capture_message("Important event occurred", level='info')

# Set user context (after authentication)
set_user(user_id=123, email='user@example.com')

# Add custom tags
set_tag('ticket_id', '12345')

# Track function performance
@track_performance('process_ticket')
def process_ticket(ticket_id):
    # ... processing logic
    pass

# Manual span tracking
with SentrySpan(op='db.query', description='Get ticket by ID') as span:
    ticket = Ticket.query.get(ticket_id)
    span.set_data('ticket_id', ticket_id)
```

### Filtered Data

The following data is automatically filtered from Sentry:

- **Headers**: `authorization`, `cookie`, `x-api-key`
- **Body Fields**: `password`, `token`, `secret`, `api_key`, `credit_card`
- **Endpoints**: `/health`, `/ready`, `/live`, `/metrics` (excluded from performance)

---

## Health Checks

### `/health` Endpoint

Returns component health status:

```json
{
  "status": "healthy",
  "timestamp": 1709654321.123,
  "checks": {
    "database": {"status": "healthy"},
    "cache": {"status": "healthy"}
  }
}
```

**Response Codes:**
- `200`: All components healthy
- `503`: One or more components unhealthy

### `/ready` Endpoint

Kubernetes readiness probe:

```json
{"status": "ready"}
```

### `/live` Endpoint

Kubernetes liveness probe:

```json
{"status": "alive"}
```

### Docker Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
```

---

## Logging

### Log Format

```
2024-03-05 14:30:00 - api.requests - INFO - [abc123] --> GET /api/tickets | IP: 192.168.1.1 | Content-Length: 0
2024-03-05 14:30:00 - api.requests - INFO - [abc123] <-- GET /api/tickets | Status: 200 | Duration: 45.23ms | Size: 1234 bytes
```

### Log Levels

| Level | Usage |
|-------|-------|
| `DEBUG` | Detailed request/response data |
| `INFO` | Normal request flow |
| `WARNING` | 4xx responses, slow requests |
| `ERROR` | 5xx responses, exceptions |

### Response Headers

Each response includes:
- `X-Request-ID`: Unique request identifier
- `X-Response-Time`: Request duration

### Slow Request Tracking

```python
from app.utils.logging_middleware import log_slow_request

@log_slow_request(threshold_ms=1000)
def slow_operation():
    # Operations taking >1000ms will be logged as warnings
    pass
```

### Operation Logging

```python
from app.utils.logging_middleware import RequestLogger

with RequestLogger('database_query') as logger:
    result = db.session.execute(query)
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | - | Sentry DSN (required for error tracking) |
| `SENTRY_TRACES_SAMPLE_RATE` | 0.1 | Performance sampling rate (0.0-1.0) |
| `SENTRY_PROFILES_SAMPLE_RATE` | 0.1 | Profiling sampling rate (0.0-1.0) |
| `APP_VERSION` | 1.0.0 | Application version for release tracking |
| `FLASK_ENV` | development | Environment name |
| `LOG_TO_FILE` | false | Enable file logging |
| `prometheus_multiproc_dir` | - | Directory for multiprocess Prometheus |

### Flask Config

```python
# config.py
class ProductionConfig:
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    VERSION = os.environ.get('APP_VERSION', '1.0.0')
    LOG_TO_FILE = True
```

---

## Dashboards

### Grafana Dashboard (Example)

Create a dashboard with these panels:

#### Request Rate
```promql
rate(http_requests_total[5m])
```

#### Error Rate
```promql
rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m])
```

#### P95 Latency
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### Tickets by Status
```promql
app_tickets_total
```

### Recommended Panels

1. **Request Rate** - Requests per second
2. **Error Rate** - 5xx errors percentage
3. **Latency Distribution** - P50, P95, P99
4. **Active Requests** - In-flight requests
5. **Ticket Metrics** - Created, resolved, by status
6. **Database Performance** - Query latency
7. **Cache Hit Rate** - Hits vs misses

---

## Alerting

### Prometheus Alerting Rules

```yaml
# alerts.yml
groups:
  - name: support-ticket-api
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s"

      - alert: ServiceDown
        expr: up{job="support-ticket-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
```

### Sentry Alerts

Configure in Sentry dashboard:
1. **Issue Alerts**: New errors, error spikes
2. **Metric Alerts**: Error count, transaction duration
3. **Uptime Alerts**: Endpoint monitoring

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export SENTRY_DSN="your-sentry-dsn"
export FLASK_ENV="production"
```

### 3. Run Application

```bash
python run.py
```

### 4. Verify Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Metrics
curl http://localhost:5000/metrics

# Readiness
curl http://localhost:5000/ready
```

### 5. Configure Prometheus

Add scrape target in `prometheus.yml` and restart Prometheus.

### 6. Import Grafana Dashboard

Import the provided dashboard JSON or create custom panels.

---

## Troubleshooting

### Metrics Not Appearing

1. Check `/metrics` endpoint is accessible
2. Verify Prometheus scrape config
3. Check for firewall/network issues

### Sentry Not Receiving Events

1. Verify `SENTRY_DSN` is set correctly
2. Check network connectivity to Sentry
3. Review Sentry SDK logs

### High Memory Usage

For multiprocess deployments (gunicorn), set:
```bash
export prometheus_multiproc_dir=/tmp/prometheus_multiproc
mkdir -p $prometheus_multiproc_dir
```

---

## Summary

| Component | Endpoint | Purpose |
|-----------|----------|---------|
| Prometheus | `/metrics` | Metrics collection |
| Health | `/health` | Component health |
| Readiness | `/ready` | K8s readiness |
| Liveness | `/live` | K8s liveness |
| Sentry | N/A | Error tracking |
| Logging | stdout/file | Request logs |
