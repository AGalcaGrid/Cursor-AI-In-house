from marshmallow import fields, validate, validates, validates_schema, ValidationError, post_load
from app import ma
from app.models.ticket import Ticket
from app.utils.security import sanitize_input


class TicketSchema(ma.SQLAlchemyAutoSchema):
    """Schema for ticket serialization."""
    class Meta:
        model = Ticket
        include_fk = True
        load_instance = True
    
    customer = fields.Nested('CustomerSchema', only=['id', 'name', 'email'], dump_only=True)
    assigned_agent = fields.Nested('AgentSchema', only=['id', 'name', 'email'], dump_only=True)


class TicketCreateSchema(ma.Schema):
    """Schema for ticket creation per PRD FR-001."""
    subject = fields.String(
        required=True,
        validate=validate.Length(min=5, max=200,
            error='Subject must be between 5 and 200 characters')
    )
    description = fields.String(
        required=True,
        validate=validate.Length(min=20, max=5000,
            error='Description must be between 20 and 5000 characters')
    )
    priority = fields.String(
        validate=validate.OneOf(
            Ticket.PRIORITIES,
            error='Priority must be one of: low, medium, high, urgent'
        ),
        load_default='medium'
    )
    category = fields.String(
        validate=validate.OneOf(
            Ticket.CATEGORIES,
            error='Category must be one of: technical, billing, general, feature_request'
        ),
        allow_none=True
    )
    customer_email = fields.Email(
        required=False,
        error_messages={'invalid': 'Invalid email format'}
    )
    
    @validates('subject')
    def validate_subject(self, value):
        """Validate subject contains only allowed characters per PRD."""
        import re
        if not re.match(r'^[a-zA-Z0-9\s.,!?\-_()\[\]@#$%&*+=:;\'"]+$', value):
            raise ValidationError('Subject contains invalid characters')
    
    @post_load
    def sanitize_fields(self, data, **kwargs):
        """Sanitize input fields after loading."""
        if 'subject' in data:
            data['subject'] = sanitize_input(data['subject'])
        if 'description' in data:
            data['description'] = sanitize_input(data['description'])
        return data


class TicketUpdateSchema(ma.Schema):
    """Schema for ticket updates."""
    subject = fields.String(
        validate=validate.Length(min=5, max=200)
    )
    description = fields.String(
        validate=validate.Length(min=20)
    )
    priority = fields.String(
        validate=validate.OneOf(Ticket.PRIORITIES)
    )
    category = fields.String(
        validate=validate.OneOf(Ticket.CATEGORIES),
        allow_none=True
    )
    
    @post_load
    def sanitize_fields(self, data, **kwargs):
        """Sanitize input fields after loading."""
        return sanitize_input(data)


class TicketAssignSchema(ma.Schema):
    """Schema for ticket assignment."""
    agent_id = fields.Integer(required=True)


class TicketStatusUpdateSchema(ma.Schema):
    """Schema for ticket status updates with transition validation."""
    status = fields.String(
        required=True,
        validate=validate.OneOf(
            Ticket.STATUSES,
            error='Invalid status'
        )
    )
    reason = fields.String(
        validate=validate.Length(max=500),
        allow_none=True
    )
    
    @validates('status')
    def validate_status(self, value):
        """Validate status value."""
        if value not in Ticket.STATUSES:
            raise ValidationError(f'Invalid status. Must be one of: {", ".join(Ticket.STATUSES)}')


class TicketFilterSchema(ma.Schema):
    """Schema for ticket filtering/search per PRD FR-025, FR-026."""
    status = fields.String(validate=validate.OneOf(Ticket.STATUSES))
    statuses = fields.List(fields.String(validate=validate.OneOf(Ticket.STATUSES)))  # Multiple status selection
    priority = fields.String(validate=validate.OneOf(Ticket.PRIORITIES))
    category = fields.String(validate=validate.OneOf(Ticket.CATEGORIES))
    assigned_to_id = fields.Integer()
    customer_id = fields.Integer()
    customer_email = fields.String()
    ticket_number = fields.String()
    search = fields.String(validate=validate.Length(max=100))
    # Date range filters per PRD FR-026
    created_from = fields.DateTime()
    created_to = fields.DateTime()
    updated_from = fields.DateTime()
    updated_to = fields.DateTime()
    resolved_from = fields.DateTime()
    resolved_to = fields.DateTime()
    unassigned = fields.Boolean()  # Filter unassigned tickets
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))  # Per PRD FR-027


class TicketPriorityUpdateSchema(ma.Schema):
    """Schema for priority updates with required reason per PRD FR-024."""
    priority = fields.String(
        required=True,
        validate=validate.OneOf(Ticket.PRIORITIES)
    )
    reason = fields.String(
        required=True,
        validate=validate.Length(min=5, max=500,
            error='Reason must be between 5 and 500 characters')
    )


class TicketHistorySchema(ma.Schema):
    """Schema for ticket history entries."""
    id = fields.Integer()
    old_status = fields.String()
    new_status = fields.String()
    changed_at = fields.DateTime()
    reason = fields.String()
    changed_by = fields.Nested('UserSchema', only=['id', 'email', 'role'])
