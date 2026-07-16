from marshmallow import fields, validate, validates, ValidationError
from app import ma
from app.models.agent import Agent
from app.utils.security import validate_password_strength


class AgentSchema(ma.SQLAlchemyAutoSchema):
    """Schema for agent serialization."""
    class Meta:
        model = Agent
        exclude = ('password_hash',)
        load_instance = True
    
    current_ticket_count = fields.Integer(dump_only=True)
    can_accept_tickets = fields.Boolean(dump_only=True)


class AgentCreateSchema(ma.Schema):
    """Schema for agent creation (admin only)."""
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
    department = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    max_tickets = fields.Integer(
        validate=validate.Range(min=1, max=50),
        load_default=10
    )
    
    @validates('password')
    def validate_password(self, value):
        is_valid, error = validate_password_strength(value)
        if not is_valid:
            raise ValidationError(error)


class AgentUpdateSchema(ma.Schema):
    """Schema for agent updates."""
    name = fields.String(validate=validate.Length(min=2, max=100))
    department = fields.String(validate=validate.Length(max=50), allow_none=True)
    is_available = fields.Boolean()
    max_tickets = fields.Integer(validate=validate.Range(min=1, max=50))
