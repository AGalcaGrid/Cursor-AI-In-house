from datetime import datetime, timedelta
from flask import current_app
from app import db


class Ticket(db.Model):
    """Ticket model for support requests."""
    __tablename__ = 'tickets'
    
    # Indexes for optimized queries
    __table_args__ = (
        db.Index('idx_ticket_number', 'ticket_number'),
        db.Index('idx_ticket_status', 'status'),
        db.Index('idx_ticket_priority', 'priority'),
        db.Index('idx_ticket_customer', 'customer_email'),
        db.Index('idx_ticket_assigned', 'assigned_to_id'),
        db.Index('idx_ticket_created', 'created_at'),
    )
    
    # Valid statuses and transitions (FR-011, FR-012)
    VALID_STATUSES = ['open', 'assigned', 'in_progress', 'waiting', 'resolved', 'closed', 'reopened']
    STATUS_TRANSITIONS = {
        'open': ['assigned', 'closed'],
        'assigned': ['in_progress', 'closed'],
        'in_progress': ['waiting', 'resolved', 'closed'],
        'waiting': ['in_progress'],
        'resolved': ['closed', 'reopened'],
        'closed': ['reopened'],  # Only within 7 days
        'reopened': ['in_progress']
    }
    
    VALID_PRIORITIES = ['low', 'medium', 'high', 'urgent']
    VALID_CATEGORIES = ['technical', 'billing', 'general', 'feature_request']
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)  # FR-002
    subject = db.Column(db.String(200), nullable=False)  # FR-001: 5-200 chars
    description = db.Column(db.Text, nullable=False)  # FR-001: min 20 chars
    status = db.Column(db.String(20), nullable=False, default='open')  # FR-004
    priority = db.Column(db.String(20), nullable=False, default='medium')
    category = db.Column(db.String(50), nullable=False, default='general')
    customer_email = db.Column(db.String(120), nullable=False)
    
    # Foreign keys
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # SLA tracking (FR-020, FR-021)
    sla_response_due = db.Column(db.DateTime, nullable=True)
    sla_resolution_due = db.Column(db.DateTime, nullable=True)
    first_response_at = db.Column(db.DateTime, nullable=True)
    sla_response_breached = db.Column(db.Boolean, default=False)
    sla_resolution_breached = db.Column(db.Boolean, default=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    @staticmethod
    def generate_ticket_number():
        """Generate unique ticket number (FR-002): TICK-YYYYMMDD-XXXX"""
        today = datetime.utcnow().strftime('%Y%m%d')
        prefix = f'TICK-{today}-'
        
        # Find the last ticket number for today
        last_ticket = Ticket.query.filter(
            Ticket.ticket_number.like(f'{prefix}%')
        ).order_by(Ticket.ticket_number.desc()).first()
        
        if last_ticket:
            last_num = int(last_ticket.ticket_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f'{prefix}{new_num:04d}'
    
    def calculate_sla_deadlines(self):
        """Calculate SLA deadlines based on priority (FR-020)."""
        sla_config = current_app.config.get('SLA_CONFIG', {})
        priority_sla = sla_config.get(self.priority, {'response': 24, 'resolution': 240})
        
        self.sla_response_due = self.created_at + timedelta(hours=priority_sla['response'])
        self.sla_resolution_due = self.created_at + timedelta(hours=priority_sla['resolution'])
    
    def can_transition_to(self, new_status):
        """Check if status transition is valid (FR-012)."""
        if new_status not in self.VALID_STATUSES:
            return False
        
        allowed = self.STATUS_TRANSITIONS.get(self.status, [])
        
        # Special case: closed can only reopen within 7 days
        if self.status == 'closed' and new_status == 'reopened':
            if self.closed_at:
                days_since_closed = (datetime.utcnow() - self.closed_at).days
                return days_since_closed <= 7
            return False
        
        return new_status in allowed
    
    def update_status(self, new_status, user_id=None):
        """Update ticket status with validation."""
        old_status = self.status
        self.status = new_status
        
        # Update timestamps based on status
        if new_status == 'resolved':
            self.resolved_at = datetime.utcnow()
        elif new_status == 'closed':
            self.closed_at = datetime.utcnow()
        elif new_status == 'reopened':
            self.resolved_at = None
            self.closed_at = None
        
        return old_status
    
    def check_sla_breach(self):
        """Check and update SLA breach status (FR-021)."""
        now = datetime.utcnow()
        
        if self.sla_response_due and not self.first_response_at:
            if now > self.sla_response_due:
                self.sla_response_breached = True
        
        if self.sla_resolution_due and self.status not in ['resolved', 'closed']:
            if now > self.sla_resolution_due:
                self.sla_resolution_breached = True
    
    def is_approaching_sla(self, hours_threshold=2):
        """Check if ticket is approaching SLA deadline."""
        now = datetime.utcnow()
        threshold = timedelta(hours=hours_threshold)
        
        if self.sla_response_due and not self.first_response_at:
            if self.sla_response_due - now <= threshold:
                return True
        
        if self.sla_resolution_due and self.status not in ['resolved', 'closed']:
            if self.sla_resolution_due - now <= threshold:
                return True
        
        return False
    
    def __repr__(self):
        return f'<Ticket {self.ticket_number}>'
