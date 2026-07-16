from app.routes.auth import auth_bp
from app.routes.tasks import tasks_bp
from app.routes.projects import projects_bp
from app.routes.notifications import notifications_bp

__all__ = ['auth_bp', 'tasks_bp', 'projects_bp', 'notifications_bp']
