from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow
from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    with app.app_context():
        from app.routes import products, cart, checkout, orders, discounts, auth
        from app.utils.errors import register_error_handlers
        
        app.register_blueprint(products.products_bp, url_prefix='/api/products')
        app.register_blueprint(cart.cart_bp, url_prefix='/api/cart')
        app.register_blueprint(checkout.checkout_bp, url_prefix='/api/checkout')
        app.register_blueprint(orders.orders_bp, url_prefix='/api/orders')
        app.register_blueprint(discounts.discounts_bp, url_prefix='/api/discounts')
        app.register_blueprint(auth.auth_bp, url_prefix='/api/auth')
        
        register_error_handlers(app)
        
        db.create_all()
    
    return app
