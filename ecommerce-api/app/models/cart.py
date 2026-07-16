from datetime import datetime, timedelta
from app import db
from flask import current_app


class Cart(db.Model):
    """Shopping cart model."""
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), index=True)  # For guest users
    discount_code_id = db.Column(db.Integer, db.ForeignKey('discount_codes.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    user = db.relationship('User', back_populates='cart')
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')
    discount_code = db.relationship('DiscountCode')
    
    def __init__(self, **kwargs):
        super(Cart, self).__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(
                days=current_app.config.get('CART_EXPIRY_DAYS', 7)
            )
    
    @property
    def is_expired(self):
        """Check if cart has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self):
        """Calculate cart subtotal before discounts."""
        return sum(item.total_price for item in self.items)
    
    @property
    def discount_amount(self):
        """Calculate discount amount."""
        if not self.discount_code or not self.discount_code.is_valid:
            return 0
        
        if self.discount_code.discount_type == 'percentage':
            discount = self.subtotal * (self.discount_code.discount_value / 100)
            if self.discount_code.max_discount_amount:
                discount = min(discount, self.discount_code.max_discount_amount)
            return discount
        elif self.discount_code.discount_type == 'fixed':
            return min(self.discount_code.discount_value, self.subtotal)
        
        return 0
    
    @property
    def total(self):
        """Calculate cart total after discounts."""
        return max(self.subtotal - self.discount_amount, 0)
    
    def add_item(self, product, quantity=1):
        """Add item to cart or update quantity if exists."""
        existing_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product.id
        ).first()
        
        if existing_item:
            new_quantity = existing_item.quantity + quantity
            max_quantity = current_app.config.get('MAX_ITEM_QUANTITY', 10)
            
            if new_quantity > max_quantity:
                return False, f"Maximum quantity per item is {max_quantity}"
            
            if new_quantity > product.stock_quantity:
                return False, f"Only {product.stock_quantity} items available in stock"
            
            existing_item.quantity = new_quantity
            existing_item.updated_at = datetime.utcnow()
        else:
            if self.total_items >= current_app.config.get('MAX_CART_ITEMS', 100):
                return False, "Cart is full"
            
            if quantity > product.stock_quantity:
                return False, f"Only {product.stock_quantity} items available in stock"
            
            cart_item = CartItem(
                cart_id=self.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            )
            self.items.append(cart_item)
        
        self.updated_at = datetime.utcnow()
        return True, "Item added to cart"
    
    def update_item_quantity(self, product_id, quantity):
        """Update quantity of item in cart."""
        cart_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if not cart_item:
            return False, "Item not found in cart"
        
        if quantity <= 0:
            db.session.delete(cart_item)
            return True, "Item removed from cart"
        
        max_quantity = current_app.config.get('MAX_ITEM_QUANTITY', 10)
        if quantity > max_quantity:
            return False, f"Maximum quantity per item is {max_quantity}"
        
        if quantity > cart_item.product.stock_quantity:
            return False, f"Only {cart_item.product.stock_quantity} items available"
        
        cart_item.quantity = quantity
        cart_item.updated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        return True, "Quantity updated"
    
    def remove_item(self, product_id):
        """Remove item from cart."""
        cart_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if cart_item:
            db.session.delete(cart_item)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def clear(self):
        """Clear all items from cart."""
        for item in self.items:
            db.session.delete(item)
        self.discount_code_id = None
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Cart {self.id} - {self.total_items} items>'


class CartItem(db.Model):
    """Cart item model."""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price at time of adding
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    cart = db.relationship('Cart', back_populates='items')
    product = db.relationship('Product', back_populates='cart_items')
    
    @property
    def total_price(self):
        """Calculate total price for this cart item."""
        return self.price * self.quantity
    
    def __repr__(self):
        return f'<CartItem {self.product.name} x{self.quantity}>'
