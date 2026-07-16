"""Celery worker entry point."""
from app import create_app, celery

# Create Flask app to initialize Celery
app = create_app()
app.app_context().push()

# Import tasks to register them with Celery
from app.tasks import celery_tasks

if __name__ == '__main__':
    celery.start()
