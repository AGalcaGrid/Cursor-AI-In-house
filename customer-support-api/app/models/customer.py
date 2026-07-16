from datetime import datetime
from app import db
from app.models.user import User


class Customer(User):
    """Customer model extending User."""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    
    # Relationships
    tickets = db.relationship('Ticket', back_populates='customer', lazy='dynamic')
    
    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }
    
    def __repr__(self):
        return f'<Customer {self.name}>'
