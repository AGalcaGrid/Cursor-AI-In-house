from app.routes.auth import auth_bp
from app.routes.tickets import tickets_bp
from app.routes.customers import customers_bp
from app.routes.agents import agents_bp
from app.routes.comments import comments_bp
from app.routes.admin import admin_bp

__all__ = [
    'auth_bp', 'tickets_bp', 'customers_bp',
    'agents_bp', 'comments_bp', 'admin_bp'
]
