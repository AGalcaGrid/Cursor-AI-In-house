from datetime import datetime
from app import db


class Project(db.Model):
    """Project model for organizing tasks."""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, archived, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy='dynamic')
    members = db.relationship('TeamMember', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'


class TeamMember(db.Model):
    """Team membership for project collaboration."""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), default='member')  # owner, admin, member, viewer
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Unique constraint: user can only be member once per project
    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='unique_team_member'),)
    
    def __repr__(self):
        return f'<TeamMember user={self.user_id} project={self.project_id}>'
