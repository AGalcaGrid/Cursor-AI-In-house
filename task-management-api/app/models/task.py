from datetime import datetime
from app import db


class Task(db.Model):
    """Task model for task management."""
    __tablename__ = 'tasks'
    
    # Performance optimization: Add composite indexes for frequently queried fields
    __table_args__ = (
        db.Index('idx_user_status', 'user_id', 'status'),
        db.Index('idx_user_priority', 'user_id', 'priority'),
        db.Index('idx_assigned_status', 'assigned_to_id', 'status'),
        db.Index('idx_project_status', 'project_id', 'status'),
        db.Index('idx_created_at', 'created_at'),
        db.Index('idx_due_date', 'due_date'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, in_progress, completed
    priority = db.Column(db.String(20), default='medium', index=True)  # low, medium, high
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True, index=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Relationships
    assignee = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks')
    
    def __repr__(self):
        return f'<Task {self.title}>'
