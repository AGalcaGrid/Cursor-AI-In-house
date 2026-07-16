# 🚀 Cursor AI In-House Project

A comprehensive microservices-based application featuring multiple backend APIs and a unified React frontend, all containerized with Docker for seamless deployment.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Services](#services)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Development](#development)
- [Documentation](#documentation)

## 🎯 Overview

This project demonstrates a modern microservices architecture with:
- **5 Backend APIs** (Flask/Python)
- **1 Frontend Application** (React)
- **Shared Redis** for caching and message queuing
- **Celery** for background task processing
- **Docker Compose** for orchestration
- **Comprehensive Testing** with pytest and Playwright
- **CI/CD Pipeline** with GitHub Actions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Port 3000)               │
│                    Unified Dashboard & UI                    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│   Blog API     │   │ Support Ticket │   │ Task Mgmt API  │
│   Port 5000    │   │   Port 5002    │   │   Port 5003    │
└────────────────┘   └────────────────┘   └────────────────┘
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐            │
│ Customer Supp  │   │  E-Commerce    │            │
│   Port 5001    │   │   Port 5004    │            │
└────────────────┘   └────────────────┘            │
                              │                     │
                     ┌────────▼─────────────────────▼────┐
                     │         Redis (Port 6379)         │
                     │    Cache & Message Broker         │
                     └───────────────────────────────────┘
                              │
                     ┌────────▼────────┐
                     │ Celery Workers  │
                     │  & Beat Scheduler│
                     └─────────────────┘
```

## ✨ Features

### Backend APIs
- **Blog API** - Content management with posts, comments, and categories
- **Customer Support API** - Ticket management and customer service
- **Support Ticket API** - Advanced ticketing system with workflows
- **Task Management API** - Project and task tracking with Celery integration
- **E-Commerce API** - Product catalog, cart, and checkout with Stripe integration

### Frontend
- **Unified Dashboard** - Single interface for all services
- **Dark Mode** - Toggle between light and dark themes
- **Responsive Design** - Mobile-first approach with TailwindCSS
- **Real-time Updates** - WebSocket support for live data

### Infrastructure
- **Docker Compose** - One-command deployment
- **Redis Caching** - Improved performance and session management
- **Background Jobs** - Celery for async task processing
- **Rate Limiting** - API protection and throttling
- **CORS Support** - Secure cross-origin requests

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed ([Installation Guide](DOCKER_INSTALLATION_GUIDE.md))
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone git@github.com:AGalcaGrid/Cursor-AI-In-house.git
   cd Cursor-AI-In-house
   ```

2. **Start all services**
   ```bash
   ./docker-start-all.sh
   ```
   
   Or manually:
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running**
   ```bash
   docker-compose ps
   ```

4. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Blog API**: http://localhost:5000
   - **Customer Support API**: http://localhost:5001
   - **Support Ticket API**: http://localhost:5002
   - **Task Management API**: http://localhost:5003
   - **E-Commerce API**: http://localhost:5004

## 🔧 Services

### React Frontend (Port 3000)
- Modern React application with routing
- TailwindCSS for styling
- Axios for API communication
- Dark mode support

### Blog API (Port 5000)
- RESTful API for blog management
- SQLite database
- JWT authentication
- Swagger documentation at `/apidocs`

### Customer Support API (Port 5001)
- Customer service ticket management
- User authentication
- Redis caching
- Swagger documentation at `/apidocs`

### Support Ticket API (Port 5002)
- Advanced ticketing workflows
- Priority and status management
- JWT authentication
- Swagger documentation at `/apidocs`

### Task Management API (Port 5003)
- Project and task tracking
- Celery background tasks
- Email notifications
- Swagger documentation at `/apidocs`

### E-Commerce API (Port 5004)
- Product catalog
- Shopping cart
- Stripe payment integration
- Order management
- Swagger documentation at `/apidocs`

## 📚 API Documentation

Each API includes Swagger/OpenAPI documentation:

- Blog API: http://localhost:5000/apidocs
- Customer Support: http://localhost:5001/apidocs
- Support Tickets: http://localhost:5002/apidocs
- Task Management: http://localhost:5003/apidocs
- E-Commerce: http://localhost:5004/apidocs

## 🧪 Testing

### Run All Tests
```bash
# Backend tests
docker-compose exec blog-api pytest
docker-compose exec customer-support-api pytest
docker-compose exec support-ticket-api pytest
docker-compose exec task-management-api pytest
docker-compose exec ecommerce-api pytest

# Frontend tests
docker-compose exec react-app npm test

# E2E tests with Playwright
cd qa-automation
pytest tests/
```

### Test Coverage
- Unit tests for all API endpoints
- Integration tests for service interactions
- E2E tests with Playwright
- Performance tests included

See [TESTS_100_PERCENT_COMPLETE.md](TESTS_100_PERCENT_COMPLETE.md) for detailed test reports.

## 💻 Development

### Project Structure
```
.
├── blog-api/                 # Blog API service
├── customer-support-api/     # Customer support service
├── support-ticket-api/       # Support ticket service
├── task-management-api/      # Task management service
├── ecommerce-api/            # E-commerce service
├── react-app/                # React frontend
├── qa-automation/            # Playwright E2E tests
├── docker-compose.yml        # Docker orchestration
├── docker-start-all.sh       # Startup script
└── Dockerfile.python-api     # Shared Python API Dockerfile
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
# Email configuration (for Task Management API)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Stripe (for E-Commerce API)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Development Workflow
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Restart a service
docker-compose restart [service-name]

# Stop all services
docker-compose down

# Clean up (removes volumes)
docker-compose down -v
```

### Hot Reload
All services support hot reload during development:
- React app: Changes auto-refresh
- Python APIs: Flask debug mode enabled

## 📖 Documentation

Comprehensive documentation is available:

- [Docker Quick Start](DOCKER_QUICKSTART.md) - Get started with Docker
- [Docker Installation Guide](DOCKER_INSTALLATION_GUIDE.md) - Detailed setup
- [CI/CD Pipeline Status](CICD_PIPELINE_STATUS.md) - GitHub Actions setup
- [Test Coverage Analysis](TEST_COVERAGE_ANALYSIS.md) - Testing details
- [Performance Optimization](PERFORMANCE_OPTIMIZATION_SUMMARY.md) - Performance tuning
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

### API-Specific Guides
- [Blog API Verification](BLOG_API_VERIFICATION.md)
- [Customer Support Verification](CUSTOMER_SUPPORT_VERIFICATION.md)
- [Task Management Verification](TASK_MANAGEMENT_API_VERIFICATION.md)
- [E-Commerce Exercise](ECOMMERCE_EXERCISE_COMPLETE.md)

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (development), PostgreSQL-ready
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT
- **API Docs**: Flasgger (Swagger)

### Frontend
- **Framework**: React
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **Routing**: React Router
- **Icons**: Lucide React

### DevOps
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest, Playwright
- **Code Quality**: pylint, black, flake8

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is for educational and demonstration purposes.

## 🙏 Acknowledgments

Built with Cursor AI as a comprehensive demonstration of modern microservices architecture and full-stack development practices.

---

**Quick Commands Reference:**

```bash
# Start everything
./docker-start-all.sh

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Run tests
docker-compose exec [service] pytest

# Clean rebuild
docker-compose down -v && docker-compose up -d --build
```

For detailed guides, see the documentation files in the project root.
