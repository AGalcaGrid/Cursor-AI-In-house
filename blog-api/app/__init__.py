from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_caching import Cache
from flasgger import Swagger

from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
cache = Cache()


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
    Swagger(app)
    
    # Setup request/response logging
    from app.utils.logging_middleware import setup_request_logging
    setup_request_logging(app)
    
    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.categories import categories_bp
    from app.routes.search import search_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    
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
            try:
                db.create_all()
            except Exception as e2:
                app.logger.error(f"Failed to create database on retry: {e2}")
    
    return app
