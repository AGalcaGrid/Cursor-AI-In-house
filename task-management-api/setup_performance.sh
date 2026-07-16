#!/bin/bash

# Performance Optimization Setup Script
# This script sets up Redis, Celery, and runs tests

echo "🚀 Setting up Performance Optimizations..."
echo ""

# Check if Redis is installed
echo "📦 Checking Redis installation..."
if command -v redis-server &> /dev/null; then
    echo "✅ Redis is installed"
else
    echo "❌ Redis is not installed"
    echo "Please install Redis:"
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt-get install redis-server"
    exit 1
fi

# Start Redis if not running
echo ""
echo "🔄 Starting Redis..."
if pgrep -x "redis-server" > /dev/null; then
    echo "✅ Redis is already running"
else
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start redis
    else
        sudo systemctl start redis
    fi
    echo "✅ Redis started"
fi

# Verify Redis connection
echo ""
echo "🔍 Verifying Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is responding"
else
    echo "❌ Cannot connect to Redis"
    exit 1
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Run database migrations
echo ""
echo "🗄️  Running database migrations..."
flask db upgrade
echo "✅ Migrations complete"

# Run tests
echo ""
echo "🧪 Running tests..."
pytest --cov=app --cov-report=term-missing
echo ""

# Check coverage
echo ""
echo "📊 Checking test coverage..."
coverage_percent=$(pytest --cov=app --cov-report=term | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
if [ -z "$coverage_percent" ]; then
    echo "⚠️  Could not determine coverage percentage"
else
    if (( $(echo "$coverage_percent >= 90" | bc -l) )); then
        echo "✅ Test coverage: ${coverage_percent}% (Target: 90%+)"
    else
        echo "⚠️  Test coverage: ${coverage_percent}% (Target: 90%+)"
    fi
fi

# Print next steps
echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Start the Flask API:"
echo "   python run.py"
echo ""
echo "2. Start Celery worker (in a new terminal):"
echo "   celery -A celery_worker.celery worker --loglevel=info"
echo ""
echo "3. Start Celery beat for scheduled tasks (in a new terminal):"
echo "   celery -A celery_worker.celery beat --loglevel=info"
echo ""
echo "4. Test the API:"
echo "   curl http://localhost:5003/api/tasks -H 'Authorization: Bearer <token>'"
echo ""
echo "5. Generate a report:"
echo "   curl -X POST http://localhost:5003/api/tasks/reports/generate \\"
echo "     -H 'Authorization: Bearer <token>' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"report_type\": \"summary\"}'"
echo ""
echo "📚 See PERFORMANCE_OPTIMIZATION.md for detailed documentation"
echo ""
