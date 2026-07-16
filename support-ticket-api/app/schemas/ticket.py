import re
from marshmallow import fields, validate, validates, ValidationError, post_load
from app import ma
from app.models.ticket import Ticket


class TicketSchema(ma.SQLAlchemyAutoSchema):
    """Schema for ticket serialization."""
    class Meta:
        model = Ticket
        include_fk = True
        load_instance = True
    
    assigned_agent = fields.Nested('UserSchema', only=('id', 'name', 'email'), dump_only=True)
    comment_count = fields.Method('get_comment_count', dump_only=True)
    is_sla_at_risk = fields.Method('get_sla_risk', dump_only=True)
    
    def get_comment_count(self, obj):
        return obj.comments.count() if obj.comments else 0
    
    def get_sla_risk(self, obj):
        return obj.is_approaching_sla() if hasattr(obj, 'is_approaching_sla') else False


class TicketCreateSchema(ma.Schema):
    """Schema for ticket creation with validation (FR-001)."""
    subject = fields.String(
        required=True,
        validate=validate.Length(min=5, max=200, error="Subject must be at least 5 characters long")
    )
    description = fields.String(
        required=True,
        validate=validate.Length(min=20, max=5000, error="Description must be at least 20 characters long")
    )
    priority = fields.String(
        validate=validate.OneOf(['low', 'medium', 'high', 'urgent']),
        load_default='medium'
    )
    category = fields.String(
        validate=validate.OneOf(['technical', 'billing', 'general', 'feature_request']),
        load_default='general'
    )
    customer_email = fields.Email(load_default=None)
    
    @validates('subject')
    def validate_subject(self, value):
        # Only alphanumeric and common punctuation
        if not re.match(r'^[\w\s\-.,!?\'\"():;]+$', value):
            raise ValidationError('Subject contains invalid characters')
    
    @validates('customer_email')
    def validate_customer_email(self, value):
        # Skip validation if no email provided (will use authenticated user's email)
        if value is None:
            return
        # Validate proper domain
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            raise ValidationError('Invalid email format')


class TicketUpdateSchema(ma.Schema):
    """Schema for ticket updates."""
    subject = fields.String(validate=validate.Length(min=5, max=200, error="Subject must be at least 5 characters long"))
    description = fields.String(validate=validate.Length(min=20, max=5000, error="Description must be at least 20 characters long"))
    category = fields.String(
        validate=validate.OneOf(['technical', 'billing', 'general', 'feature_request'])
    )
    
    @validates('subject')
    def validate_subject(self, value):
        if value and not re.match(r'^[\w\s\-.,!?\'\"():;]+$', value):
            raise ValidationError('Subject contains invalid characters')


class TicketStatusSchema(ma.Schema):
    """Schema for status updates (FR-011, FR-012)."""
    status = fields.String(
        required=True,
        validate=validate.OneOf(['open', 'assigned', 'in_progress', 'waiting', 'resolved', 'closed', 'reopened'])
    )
    reason = fields.String(validate=validate.Length(max=500))


class TicketPrioritySchema(ma.Schema):
    """Schema for priority updates (FR-023, FR-024)."""
    priority = fields.String(
        required=True,
        validate=validate.OneOf(['low', 'medium', 'high', 'urgent'])
    )
    reason = fields.String(
        required=True,
        validate=validate.Length(min=5, max=500)
    )


class TicketAssignSchema(ma.Schema):
    """Schema for ticket assignment (FR-005)."""
    agent_id = fields.Integer(required=True)
