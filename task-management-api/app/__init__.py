from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_caching import Cache
from flask_mail import Mail
from flasgger import Swagger
from celery import Celery

from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
cache = Cache()
mail = Mail()
celery = Celery()


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"]}})
    Swagger(app)
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # Setup request/response logging
    from app.utils.logging_middleware import setup_request_logging
    setup_request_logging(app)
    
    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    from app.routes.projects import projects_bp
    from app.routes.notifications import notifications_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    
    # Create database tables
    with app.app_context():
        try:
            # Ensure instance directory exists
            import os
            instance_path = os.path.join(app.root_path, '..', 'instance')
            os.makedirs(instance_path, exist_ok=True)
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error creating database: {e}")
            # Try one more time after ensuring directory exists
            try:
                db.create_all()
            except Exception as e2:
                app.logger.error(f"Failed to create database on retry: {e2}")
    
    return app
