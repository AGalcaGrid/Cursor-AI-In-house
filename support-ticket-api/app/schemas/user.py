import re
from marshmallow import fields, validate, validates, ValidationError
from app import ma
from app.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema for user serialization."""
    class Meta:
        model = User
        exclude = ('password_hash',)
        load_instance = True


class UserCreateSchema(ma.Schema):
    """Schema for user registration with validation."""
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=8),
        load_only=True
    )
    role = fields.String(
        validate=validate.OneOf(['customer', 'agent', 'admin']),
        load_default='customer'
    )
    
    @validates('email')
    def validate_email(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError('Email already registered')
    
    @validates('password')
    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit')


class UserLoginSchema(ma.Schema):
    """Schema for user login."""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class AgentSchema(ma.SQLAlchemyAutoSchema):
    """Schema for agent serialization."""
    class Meta:
        model = User
        exclude = ('password_hash',)
        load_instance = True
    
    open_tickets_count = fields.Method('get_open_tickets_count', dump_only=True)
    
    def get_open_tickets_count(self, obj):
        return obj.assigned_tickets.filter_by(status='open').count() if obj.assigned_tickets else 0
