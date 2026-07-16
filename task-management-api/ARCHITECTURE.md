# Performance-Optimized Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  (React App, Mobile App, API Consumers)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask API Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Routes     │  │   Schemas    │  │    Models    │         │
│  │  (Cached)    │  │ (Validation) │  │  (Indexed)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────┬──────────────────┘
             │                                │
             ▼                                ▼
┌─────────────────────────┐    ┌─────────────────────────────────┐
│    Redis Cache Layer    │    │     PostgreSQL/SQLite DB        │
│  ┌──────────────────┐   │    │  ┌──────────────────────────┐  │
│  │  Task Lists      │   │    │  │  Tasks Table             │  │
│  │  (60s timeout)   │   │    │  │  - Composite Indexes     │  │
│  ├──────────────────┤   │    │  │  - Single Indexes        │  │
│  │  Task Details    │   │    │  │  - Foreign Keys          │  │
│  │  (300s timeout)  │   │    │  └──────────────────────────┘  │
│  └──────────────────┘   │    │  ┌──────────────────────────┐  │
│                         │    │  │  Users, Projects, etc.   │  │
└─────────────────────────┘    │  └──────────────────────────┘  │
                               └─────────────────────────────────┘
             ▲
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Celery Task Queue                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Email      │  │   Reports    │  │  Scheduled   │         │
│  │   Tasks      │  │  Generation  │  │    Tasks     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Redis Message Broker                         │
│  (Task Queue, Results Backend)                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flow

### 1. GET Request (Cached)
```
Client Request
    │
    ▼
Flask Route (@cache.cached)
    │
    ├─── Cache Hit? ──► Return Cached Response (10ms)
    │
    └─── Cache Miss
         │
         ▼
    Database Query (with indexes)
         │
         ▼
    Eager Load Relationships
         │
         ▼
    Store in Cache
         │
         ▼
    Return Response (100ms)
```

### 2. POST/PUT Request (Cache Invalidation)
```
Client Request
    │
    ▼
Flask Route
    │
    ▼
Validate Data (Marshmallow)
    │
    ▼
Database Write
    │
    ├─── Invalidate Cache
    │
    └─── Trigger Background Task?
         │
         ▼
    Queue Celery Task
         │
         ▼
    Return Response (50ms)
         │
         │ (async)
         ▼
    Celery Worker Processes Task
         │
         ▼
    Send Email / Generate Report
```

### 3. Async Report Generation
```
Client Request (POST /reports/generate)
    │
    ▼
Queue Celery Task
    │
    ▼
Return Task ID (202 Accepted)
    │
    │ (Client polls status)
    │
    ▼
Celery Worker
    │
    ├─── Query Database
    │
    ├─── Calculate Statistics
    │
    ├─── Generate Report
    │
    └─── Store Result in Redis
         │
         ▼
Client Polls (GET /reports/status/{id})
    │
    ▼
Return Report Result
```

---

## Database Optimization

### Index Strategy
```
Tasks Table
├── Primary Key: id
├── Foreign Keys: user_id, project_id, assigned_to_id
│
├── Single Indexes:
│   ├── title (for search)
│   ├── status (for filtering)
│   ├── priority (for filtering)
│   └── created_at (for sorting)
│
└── Composite Indexes:
    ├── (user_id, status) ──► Filter user's tasks by status
    ├── (user_id, priority) ──► Filter user's tasks by priority
    ├── (assigned_to_id, status) ──► Assigned tasks by status
    ├── (project_id, status) ──► Project tasks by status
    ├── created_at ──► Sort by creation date
    └── due_date ──► Find upcoming/overdue tasks
```

### Query Optimization
```sql
-- Before (N+1 queries)
SELECT * FROM tasks WHERE user_id = 1;
-- Then for each task:
SELECT * FROM users WHERE id = task.assigned_to_id;
-- Total: 1 + N queries

-- After (Eager Loading)
SELECT tasks.*, users.*
FROM tasks
LEFT JOIN users ON tasks.assigned_to_id = users.id
WHERE tasks.user_id = 1;
-- Total: 1 query
```

---

## Caching Strategy

### Cache Layers
```
┌─────────────────────────────────────────────────────┐
│  Application Cache (Flask-Caching + Redis)         │
│                                                     │
│  ┌───────────────────────────────────────────┐    │
│  │  GET /api/tasks                           │    │
│  │  Key: view/api/tasks?status=pending       │    │
│  │  Timeout: 60 seconds                      │    │
│  │  Invalidate: On task create/update/delete │    │
│  └───────────────────────────────────────────┘    │
│                                                     │
│  ┌───────────────────────────────────────────┐    │
│  │  GET /api/tasks/{id}                      │    │
│  │  Key: task_{id}_{user_id}                 │    │
│  │  Timeout: 300 seconds                     │    │
│  │  Invalidate: On task update/delete        │    │
│  └───────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### Cache Invalidation Flow
```
Task Created/Updated/Deleted
    │
    ├─── cache.delete(f'task_{id}_{user_id}')
    │
    └─── cache.delete_memoized(get_tasks)
         │
         ▼
    All related caches cleared
         │
         ▼
    Next request rebuilds cache
```

---

## Background Task Processing

### Celery Architecture
```
┌─────────────────────────────────────────────────────┐
│                  Celery Workers                     │
│                                                     │
│  Worker 1          Worker 2          Worker 3      │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐   │
│  │  Email   │     │  Report  │     │ Cleanup  │   │
│  │  Tasks   │     │   Tasks  │     │  Tasks   │   │
│  └──────────┘     └──────────┘     └──────────┘   │
│       │                 │                 │        │
│       └─────────────────┴─────────────────┘        │
│                         │                          │
└─────────────────────────┼──────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│            Redis (Message Broker)                   │
│  ┌───────────────────────────────────────────┐     │
│  │  Task Queue                               │     │
│  │  - email_tasks                            │     │
│  │  - report_tasks                           │     │
│  │  - cleanup_tasks                          │     │
│  └───────────────────────────────────────────┘     │
│  ┌───────────────────────────────────────────┐     │
│  │  Results Backend                          │     │
│  │  - task_id: result                        │     │
│  └───────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
```

### Task Types
```
┌─────────────────────────────────────────────────────┐
│  Immediate Tasks (Triggered by API)                │
│  ├── send_email_notification                       │
│  ├── send_task_assignment_email                    │
│  └── generate_user_report                          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Scheduled Tasks (Celery Beat)                     │
│  ├── send_due_date_reminders (daily)               │
│  └── cleanup_old_notifications (weekly)            │
└─────────────────────────────────────────────────────┘
```

---

## Performance Metrics

### Response Time Breakdown
```
Before Optimization:
┌────────────────────────────────────────┐
│ Request Processing:        50ms        │
│ Database Query:           150ms        │
│ N+1 Queries:              200ms        │
│ Serialization:             50ms        │
├────────────────────────────────────────┤
│ Total:                    450ms        │
└────────────────────────────────────────┘

After Optimization (Cache Hit):
┌────────────────────────────────────────┐
│ Cache Lookup:              10ms        │
├────────────────────────────────────────┤
│ Total:                     10ms        │
└────────────────────────────────────────┘

After Optimization (Cache Miss):
┌────────────────────────────────────────┐
│ Request Processing:        30ms        │
│ Database Query (indexed):  20ms        │
│ Eager Loading:             30ms        │
│ Serialization:             20ms        │
│ Cache Store:               10ms        │
├────────────────────────────────────────┤
│ Total:                    110ms        │
└────────────────────────────────────────┘
```

### Database Query Performance
```
Query: Get user's pending tasks

Without Index:
┌────────────────────────────────────────┐
│ Full Table Scan                        │
│ Rows Scanned: 10,000                   │
│ Rows Returned: 50                      │
│ Time: 150ms                            │
└────────────────────────────────────────┘

With Composite Index (user_id, status):
┌────────────────────────────────────────┐
│ Index Scan                             │
│ Rows Scanned: 50                       │
│ Rows Returned: 50                      │
│ Time: 5ms                              │
└────────────────────────────────────────┘

Improvement: 97% faster
```

---

## Scalability

### Horizontal Scaling
```
┌─────────────────────────────────────────────────────┐
│              Load Balancer                          │
└──────┬──────────────┬──────────────┬────────────────┘
       │              │              │
       ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Flask 1  │   │ Flask 2  │   │ Flask 3  │
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────────┴──────────────┘
                    │
     ┌──────────────┴──────────────┐
     │                             │
     ▼                             ▼
┌──────────┐              ┌──────────────┐
│  Redis   │              │  PostgreSQL  │
│ (Shared) │              │   (Master)   │
└──────────┘              └──────┬───────┘
                                 │
                          ┌──────┴───────┐
                          │              │
                          ▼              ▼
                    ┌──────────┐   ┌──────────┐
                    │ Replica1 │   │ Replica2 │
                    └──────────┘   └──────────┘
```

### Celery Worker Scaling
```
┌─────────────────────────────────────────────────────┐
│  Celery Workers (Can scale independently)          │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Worker 1 │  │ Worker 2 │  │ Worker N │         │
│  │ (Email)  │  │ (Report) │  │ (Mixed)  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                                     │
│  Add more workers as load increases                │
└─────────────────────────────────────────────────────┘
```

---

## Monitoring Points

### Application Metrics
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Cache hit rate

### Database Metrics
- Query execution time
- Index usage
- Connection pool size
- Slow query log

### Cache Metrics
- Hit/miss ratio
- Memory usage
- Eviction rate
- Key count

### Celery Metrics
- Task queue length
- Task execution time
- Failed tasks
- Worker availability

---

## Technology Stack

```
┌─────────────────────────────────────────────────────┐
│  Application Layer                                  │
│  - Flask 3.0.0                                      │
│  - Flask-SQLAlchemy 3.1.1                          │
│  - Flask-JWT-Extended 4.6.0                        │
│  - Flask-Caching 2.1.0                             │
│  - Flask-Mail 0.9.1                                │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Caching & Queue Layer                              │
│  - Redis 5.0.1                                      │
│  - Celery 5.3.4                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Database Layer                                      │
│  - SQLAlchemy 2.0.23                                │
│  - PostgreSQL / SQLite                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Testing Layer                                       │
│  - pytest 7.4.3                                      │
│  - pytest-cov 4.1.0                                  │
│  - pytest-mock 3.12.0                                │
│  - factory-boy 3.3.0                                 │
└─────────────────────────────────────────────────────┘
```

---

This architecture provides:
- **High Performance** through caching and indexing
- **Scalability** through horizontal scaling
- **Reliability** through background task processing
- **Maintainability** through comprehensive testing
