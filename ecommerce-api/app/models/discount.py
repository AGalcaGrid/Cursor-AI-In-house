from datetime import datetime
from app import db


class DiscountCode(db.Model):
    """Discount code model."""
    __tablename__ = 'discount_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    min_purchase_amount = db.Column(db.Numeric(10, 2))
    max_discount_amount = db.Column(db.Numeric(10, 2))
    usage_limit = db.Column(db.Integer)  # Total times code can be used
    usage_limit_per_user = db.Column(db.Integer, default=1)
    times_used = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    usage_history = db.relationship('DiscountUsage', back_populates='discount_code', cascade='all, delete-orphan')
    
    @property
    def is_valid(self):
        """Check if discount code is currently valid."""
        now = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False
        
        return True
    
    def can_be_used_by_user(self, user_id):
        """Check if user can use this discount code."""
        if not self.is_valid:
            return False, "Discount code is not valid"
        
        if self.usage_limit_per_user:
            user_usage_count = DiscountUsage.query.filter_by(
                discount_code_id=self.id,
                user_id=user_id
            ).count()
            
            if user_usage_count >= self.usage_limit_per_user:
                return False, "You have already used this discount code"
        
        return True, "Discount code is valid"
    
    def increment_usage(self):
        """Increment usage counter."""
        self.times_used += 1
    
    def __repr__(self):
        return f'<DiscountCode {self.code}>'


class DiscountUsage(db.Model):
    """Track discount code usage."""
    __tablename__ = 'discount_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    discount_code_id = db.Column(db.Integer, db.ForeignKey('discount_codes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    discount_code = db.relationship('DiscountCode', back_populates='usage_history')
    user = db.relationship('User')
    order = db.relationship('Order')
    
    def __repr__(self):
        return f'<DiscountUsage {self.discount_code.code} by User {self.user_id}>'
