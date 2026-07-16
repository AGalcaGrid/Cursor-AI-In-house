from marshmallow import fields, validate
from app import ma
from app.models.task import Task


class TaskSchema(ma.SQLAlchemyAutoSchema):
    """Schema for task serialization."""
    class Meta:
        model = Task
        include_fk = True
        load_instance = True


class TaskCreateSchema(ma.Schema):
    """Schema for task creation."""
    title = fields.String(
        required=True, 
        validate=validate.Length(min=1, max=200)
    )
    description = fields.String(allow_none=True)
    status = fields.String(
        validate=validate.OneOf(['pending', 'in_progress', 'completed']),
        load_default='pending'
    )
    priority = fields.String(
        validate=validate.OneOf(['low', 'medium', 'high']),
        load_default='medium'
    )
    due_date = fields.DateTime(allow_none=True)
    project_id = fields.Integer(allow_none=True)
    assigned_to_id = fields.Integer(allow_none=True)


class TaskUpdateSchema(ma.Schema):
    """Schema for task updates."""
    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    status = fields.String(
        validate=validate.OneOf(['pending', 'in_progress', 'completed'])
    )
    priority = fields.String(
        validate=validate.OneOf(['low', 'medium', 'high'])
    )
    due_date = fields.DateTime(allow_none=True)
    project_id = fields.Integer(allow_none=True)
    assigned_to_id = fields.Integer(allow_none=True)
