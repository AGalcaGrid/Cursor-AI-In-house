# Customer Support Ticket System API

A comprehensive customer support ticket management system built with Flask, implementing the PRD requirements FR-001 through FR-015.

## Features

### Core Ticket Management
- **FR-001**: Ticket creation with validation (subject 5-200 chars, description min 20 chars)
- **FR-002**: Auto-generated ticket numbers (TICK-YYYYMMDD-XXXX)
- **FR-004**: Automatic "open" status on creation

### Ticket Assignment
- **FR-005**: Admin can manually assign tickets to agents
- **FR-006**: Auto-assignment based on workload (planned)
- **FR-008**: Status changes to "assigned" when assigned
- **FR-010**: Assignment history tracking

### Status Management
- **FR-011**: Status workflow (open → assigned → in_progress → resolved → closed)
- **FR-012**: Status transition validation
- **FR-013**: Status changes logged with timestamp

### Comments System
- **FR-015**: Both customers and agents can add comments
- **FR-016**: Internal comments (visible only to agents/admins)

### Priority & SLA
- **FR-020**: Priority levels with SLA deadlines
- **FR-021**: SLA breach detection and highlighting

### Role-Based Access Control
- **FR-032**: Three roles (customer, agent, admin)
- **FR-033**: Permission-based access to tickets

## Tech Stack

- Flask 3.0
- SQLAlchemy (ORM)
- Marshmallow (validation/serialization)
- Flask-JWT-Extended (authentication)
- Flask-Caching (performance)
- Flasgger (Swagger UI)

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py

# Seed test data
python run.py seed
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/logout` | Logout |

### Tickets
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickets` | List tickets (filtered by role) |
| POST | `/api/tickets` | Create ticket |
| GET | `/api/tickets/:id` | Get ticket details |
| PUT | `/api/tickets/:id` | Update ticket |
| DELETE | `/api/tickets/:id` | Delete ticket (admin only) |
| PUT | `/api/tickets/:id/status` | Update status |
| PUT | `/api/tickets/:id/priority` | Update priority |
| POST | `/api/tickets/:id/assign` | Assign to agent |
| GET | `/api/tickets/:id/history` | Get assignment history |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickets/:id/comments` | Get comments |
| POST | `/api/tickets/:id/comments` | Add comment |
| DELETE | `/api/tickets/:id/comments/:cid` | Delete comment |

### Agents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents` | List agents |
| GET | `/api/agents/:id` | Get agent details |
| GET | `/api/agents/:id/tickets` | Get agent's tickets |
| PUT | `/api/agents/:id/availability` | Update availability |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard` | Dashboard statistics |
| GET | `/api/admin/reports/tickets` | Ticket reports |
| GET | `/api/admin/reports/sla` | SLA compliance report |

## Swagger Documentation

Access Swagger UI at: `http://localhost:5000/apidocs/`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tickets.py -v
```

## Test Users (after seeding)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@support.com | Admin123! |
| Agent | agent@support.com | Agent123! |
| Customer | customer@example.com | Customer123! |

## Validation Rules

### Ticket Creation
- **Subject**: 5-200 characters, alphanumeric and common punctuation
- **Description**: 20-5000 characters
- **Priority**: low, medium, high, urgent
- **Category**: technical, billing, general, feature_request
- **Email**: Valid email format

### Status Transitions
```
open → assigned, closed
assigned → in_progress, closed
in_progress → waiting, resolved, closed
waiting → in_progress
resolved → closed, reopened
closed → reopened (within 7 days only)
reopened → in_progress
```

### SLA Deadlines
| Priority | Response | Resolution |
|----------|----------|------------|
| Urgent | 2 hours | 24 hours |
| High | 4 hours | 48 hours |
| Medium | 8 hours | 5 days |
| Low | 24 hours | 10 days |

## Project Structure

```
support-ticket-api/
├── app/
│   ├── __init__.py          # App factory
│   ├── models/
│   │   ├── user.py          # User model
│   │   ├── ticket.py        # Ticket model with SLA
│   │   ├── comment.py       # Comment model
│   │   ├── assignment.py    # Assignment history
│   │   └── attachment.py    # File attachments
│   ├── schemas/
│   │   ├── user.py          # User schemas
│   │   ├── ticket.py        # Ticket schemas
│   │   ├── comment.py       # Comment schemas
│   │   └── assignment.py    # Assignment schemas
│   ├── routes/
│   │   ├── auth.py          # Authentication
│   │   ├── tickets.py       # Ticket CRUD
│   │   ├── comments.py      # Comments
│   │   ├── agents.py        # Agent management
│   │   └── admin.py         # Admin dashboard
│   └── utils/
│       └── errors.py        # Error handlers
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_auth.py         # Auth tests
│   ├── test_tickets.py      # Ticket tests
│   ├── test_comments.py     # Comment tests
│   └── test_admin.py        # Admin tests
├── config.py                # Configuration
├── run.py                   # Entry point
├── requirements.txt         # Dependencies
└── README.md
```

## Error Response Format

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "errors": {
    "field_name": ["Error detail 1", "Error detail 2"]
  }
}
```

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| VALIDATION_ERROR | 400 | Input validation failed |
| UNAUTHORIZED | 401 | Authentication required |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Duplicate resource |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |
