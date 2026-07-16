from datetime import datetime, timedelta
from app import db


class Ticket(db.Model):
    """Support ticket model."""
    __tablename__ = 'tickets'
    
    # Database indexes for optimized queries
    __table_args__ = (
        db.Index('idx_ticket_customer_status', 'customer_id', 'status'),
        db.Index('idx_ticket_assigned_status', 'assigned_to_id', 'status'),
        db.Index('idx_ticket_priority', 'priority'),
        db.Index('idx_ticket_created_at', 'created_at'),
        db.Index('idx_ticket_status', 'status'),
        db.Index('idx_ticket_sla_response', 'sla_response_due_at', 'sla_response_breached'),
        db.Index('idx_ticket_sla_resolution', 'sla_resolution_due_at', 'sla_resolution_breached'),
    )
    
    # Valid status transitions per PRD FR-012
    STATUS_TRANSITIONS = {
        'open': ['assigned', 'closed'],
        'assigned': ['in_progress', 'closed'],
        'in_progress': ['waiting', 'resolved', 'closed'],
        'waiting': ['in_progress'],
        'resolved': ['closed', 'reopened'],
        'closed': ['reopened'],  # Only within 7 days per PRD
        'reopened': ['in_progress']
    }
    
    # SLA definitions per PRD FR-020
    # Format: (first_response_hours, resolution_hours)
    SLA_DEFINITIONS = {
        'urgent': (2, 24),
        'high': (4, 48),
        'medium': (8, 120),  # 5 days = 120 hours
        'low': (24, 240)     # 10 days = 240 hours
    }
    
    PRIORITIES = ['low', 'medium', 'high', 'urgent']
    STATUSES = ['open', 'assigned', 'in_progress', 'waiting', 'resolved', 'closed', 'reopened']
    CATEGORIES = ['technical', 'billing', 'general', 'feature_request']
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20), default='medium')
    category = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    first_response_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # SLA tracking per PRD FR-020
    sla_response_due_at = db.Column(db.DateTime, nullable=True)
    sla_resolution_due_at = db.Column(db.DateTime, nullable=True)
    sla_response_breached = db.Column(db.Boolean, default=False)
    sla_resolution_breached = db.Column(db.Boolean, default=False)
    
    # Foreign keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=True)
    
    # Relationships with eager loading options
    customer = db.relationship('Customer', back_populates='tickets', lazy='joined')
    assigned_agent = db.relationship('Agent', back_populates='assigned_tickets', lazy='joined', foreign_keys=[assigned_to_id])
    comments = db.relationship('Comment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    status_history = db.relationship('TicketStatusHistory', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    def can_transition_to(self, new_status):
        """Check if status transition is valid per PRD FR-012."""
        if self.status == new_status:
            return True
        
        # Special rule: closed tickets can only be reopened within 7 days
        if self.status == 'closed' and new_status == 'reopened':
            if self.closed_at:
                days_since_closed = (datetime.utcnow() - self.closed_at).days
                if days_since_closed > 7:
                    return False
        
        return new_status in self.STATUS_TRANSITIONS.get(self.status, [])
    
    def update_status(self, new_status, changed_by_id):
        """Update ticket status with history tracking."""
        if not self.can_transition_to(new_status):
            return False
        
        old_status = self.status
        self.status = new_status
        
        # Update timestamps
        if new_status == 'resolved':
            self.resolved_at = datetime.utcnow()
        elif new_status == 'closed':
            self.closed_at = datetime.utcnow()
        
        # Create history entry
        history = TicketStatusHistory(
            ticket_id=self.id,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=changed_by_id
        )
        db.session.add(history)
        return True
    
    def calculate_sla_deadlines(self):
        """Calculate SLA deadlines based on priority per PRD FR-020."""
        response_hours, resolution_hours = self.SLA_DEFINITIONS.get(self.priority, (24, 240))
        self.sla_response_due_at = self.created_at + timedelta(hours=response_hours)
        self.sla_resolution_due_at = self.created_at + timedelta(hours=resolution_hours)
    
    def check_sla_breach(self):
        """Check and update SLA breach status."""
        now = datetime.utcnow()
        
        # Check response SLA (breached if no first response by deadline)
        if not self.first_response_at and self.sla_response_due_at:
            if now > self.sla_response_due_at:
                self.sla_response_breached = True
        
        # Check resolution SLA (breached if not resolved by deadline)
        if self.status not in ['resolved', 'closed'] and self.sla_resolution_due_at:
            if now > self.sla_resolution_due_at:
                self.sla_resolution_breached = True
    
    @staticmethod
    def generate_ticket_number():
        """Generate unique ticket number per PRD FR-002 format: TICK-YYYYMMDD-XXXX."""
        import random
        import string
        date_part = datetime.utcnow().strftime('%Y%m%d')
        sequence = ''.join(random.choices(string.digits, k=4))
        return f'TICK-{date_part}-{sequence}'
    
    def __repr__(self):
        return f'<Ticket {self.ticket_number}>'


class TicketStatusHistory(db.Model):
    """Track ticket status changes per PRD FR-013."""
    __tablename__ = 'ticket_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=False)
    new_status = db.Column(db.String(20), nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(500), nullable=True)
    
    # Relationship
    changed_by = db.relationship('User', backref='status_changes')
    
    def __repr__(self):
        return f'<StatusHistory {self.old_status} -> {self.new_status}>'


class TicketAssignment(db.Model):
    """Track ticket assignments per PRD FR-010."""
    __tablename__ = 'ticket_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ticket = db.relationship('Ticket', backref='assignment_history')
    assigned_to = db.relationship('Agent', foreign_keys=[assigned_to_id])
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id])
    
    def __repr__(self):
        return f'<Assignment Ticket {self.ticket_id} to Agent {self.assigned_to_id}>'


class PriorityChangeHistory(db.Model):
    """Track priority changes with reason per PRD FR-024."""
    __tablename__ = 'priority_change_history'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    old_priority = db.Column(db.String(20), nullable=False)
    new_priority = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(500), nullable=False)  # Required per PRD FR-024
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ticket = db.relationship('Ticket', backref='priority_history')
    changed_by = db.relationship('User', backref='priority_changes')
    
    def __repr__(self):
        return f'<PriorityChange {self.old_priority} -> {self.new_priority}>'
