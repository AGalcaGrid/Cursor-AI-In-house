from datetime import datetime
from app import db


class Payment(db.Model):
    """Payment model."""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    
    payment_method = db.Column(db.String(50), nullable=False)  # card, paypal, etc.
    payment_status = db.Column(db.String(20), nullable=False, default='pending')
    # Status: pending, processing, succeeded, failed, refunded
    
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Stripe payment details
    stripe_payment_intent_id = db.Column(db.String(100), unique=True)
    stripe_charge_id = db.Column(db.String(100))
    stripe_customer_id = db.Column(db.String(100))
    
    # Card details (last 4 digits only for security)
    card_last4 = db.Column(db.String(4))
    card_brand = db.Column(db.String(20))
    card_exp_month = db.Column(db.Integer)
    card_exp_year = db.Column(db.Integer)
    
    # Transaction details
    transaction_id = db.Column(db.String(100))
    failure_code = db.Column(db.String(50))
    failure_message = db.Column(db.String(500))
    
    refund_amount = db.Column(db.Numeric(10, 2))
    refund_reason = db.Column(db.String(500))
    refunded_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    
    order = db.relationship('Order', back_populates='payment')
    
    @property
    def is_successful(self):
        """Check if payment was successful."""
        return self.payment_status == 'succeeded'
    
    @property
    def is_refunded(self):
        """Check if payment was refunded."""
        return self.payment_status == 'refunded'
    
    def mark_as_succeeded(self):
        """Mark payment as succeeded."""
        self.payment_status = 'succeeded'
        self.paid_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_failed(self, failure_code=None, failure_message=None):
        """Mark payment as failed."""
        self.payment_status = 'failed'
        self.failure_code = failure_code
        self.failure_message = failure_message
        self.updated_at = datetime.utcnow()
    
    def process_refund(self, amount, reason=None):
        """Process refund."""
        self.payment_status = 'refunded'
        self.refund_amount = amount
        self.refund_reason = reason
        self.refunded_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.payment_status}>'
