from datetime import datetime
from app import db


class Comment(db.Model):
    """Comment model for ticket communications (FR-015, FR-016)."""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)  # FR-016: Internal vs public
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attachments = db.relationship('Attachment', backref='comment', lazy='dynamic')
    
    def __repr__(self):
        return f'<Comment {self.id} on Ticket {self.ticket_id}>'
