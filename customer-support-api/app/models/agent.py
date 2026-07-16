from datetime import datetime
from app import db
from app.models.user import User


class Agent(User):
    """Support agent model extending User."""
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    max_tickets = db.Column(db.Integer, default=10)
    
    # Relationships
    assigned_tickets = db.relationship('Ticket', back_populates='assigned_agent', lazy='dynamic',
                                       foreign_keys='Ticket.assigned_to_id')
    
    __mapper_args__ = {
        'polymorphic_identity': 'agent'
    }
    
    @property
    def current_ticket_count(self):
        """Get count of currently active tickets."""
        from app.models.ticket import Ticket
        return Ticket.query.filter(
            Ticket.assigned_to_id == self.id,
            Ticket.status.in_(['assigned', 'in_progress', 'waiting'])
        ).count()
    
    @property
    def can_accept_tickets(self):
        """Check if agent can accept more tickets."""
        return self.is_available and self.current_ticket_count < self.max_tickets
    
    def __repr__(self):
        return f'<Agent {self.name}>'


class Admin(User):
    """Admin user model extending User."""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }
    
    def __repr__(self):
        return f'<Admin {self.name}>'
