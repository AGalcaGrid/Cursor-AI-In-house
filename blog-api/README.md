# Blog API

A RESTful API for a blogging platform built with Flask.

## Features

- User authentication (register, login) with JWT
- Blog post CRUD operations
- Comment system (create, read, delete)
- Category management
- Search posts by keyword
- Pagination (20 posts per page)
- Swagger documentation

## Tech Stack

- Flask 3.0
- SQLAlchemy (ORM)
- Marshmallow (serialization/validation)
- Flask-JWT-Extended (authentication)
- Flasgger (Swagger UI)
- SQLite (development) / PostgreSQL (production)

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py

# Seed default categories
python run.py seed
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |
| GET | `/api/auth/me` | Get current user |

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts` | List posts (paginated) |
| POST | `/api/posts` | Create post |
| GET | `/api/posts/<id>` | Get single post |
| PUT | `/api/posts/<id>` | Update post |
| DELETE | `/api/posts/<id>` | Delete post |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts/<id>/comments` | Get post comments |
| POST | `/api/posts/<id>/comments` | Create comment |
| DELETE | `/api/posts/<id>/comments/<cid>` | Delete comment |

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories` | List all categories |
| GET | `/api/categories/<id>` | Get single category |

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?q=keyword` | Search posts |

## Swagger Documentation

Access Swagger UI at: `http://localhost:5000/apidocs/`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_posts.py -v
```

## Environment Variables

Create a `.env` file:

```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///blog.db
```

## Project Structure

```
blog-api/
├── app/
│   ├── __init__.py          # App factory
│   ├── models/
│   │   ├── user.py          # User model
│   │   ├── post.py          # Post model
│   │   ├── comment.py       # Comment model
│   │   └── category.py      # Category model
│   ├── schemas/
│   │   ├── user.py          # User schemas
│   │   ├── post.py          # Post schemas
│   │   ├── comment.py       # Comment schemas
│   │   └── category.py      # Category schemas
│   ├── routes/
│   │   ├── auth.py          # Auth endpoints
│   │   ├── posts.py         # Post endpoints
│   │   ├── categories.py    # Category endpoints
│   │   └── search.py        # Search endpoint
│   └── utils/
│       └── errors.py        # Error handlers
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_auth.py         # Auth tests
│   ├── test_posts.py        # Post tests
│   ├── test_comments.py     # Comment tests
│   ├── test_categories.py   # Category tests
│   └── test_search.py       # Search tests
├── config.py                # Configuration
├── run.py                   # Entry point
├── requirements.txt         # Dependencies
└── README.md
```
