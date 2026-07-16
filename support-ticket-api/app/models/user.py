from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    # Indexes for optimized queries
    __table_args__ = (
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_role', 'role'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # customer, agent, admin
    availability_status = db.Column(db.String(20), default='available')  # available, busy, offline
    expertise_areas = db.Column(db.JSON, default=list)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Notification preferences (FR-037)
    notification_preferences = db.Column(db.JSON, default=lambda: {
        'email_ticket_created': True,
        'email_ticket_assigned': True,
        'email_status_changed': True,
        'email_new_comment': True,
        'email_sla_warning': True,
        'email_sla_breach': True,
        'email_mentions': True,
        'in_app_notifications': True
    })
    
    # Relationships
    assigned_tickets = db.relationship('Ticket', backref='assigned_agent', 
                                       lazy='dynamic', foreign_keys='Ticket.assigned_to_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def is_agent(self):
        """Check if user is agent."""
        return self.role == 'agent'
    
    def is_customer(self):
        """Check if user is customer."""
        return self.role == 'customer'
    
    def can_view_ticket(self, ticket):
        """Check if user can view a ticket."""
        if self.is_admin():
            return True
        if self.is_agent():
            return ticket.assigned_to_id == self.id or ticket.assigned_to_id is None
        return ticket.customer_email == self.email
    
    def can_modify_ticket(self, ticket):
        """Check if user can modify a ticket."""
        if self.is_admin():
            return True
        if self.is_agent():
            return ticket.assigned_to_id == self.id
        return False
    
    def __repr__(self):
        return f'<User {self.email}>'
