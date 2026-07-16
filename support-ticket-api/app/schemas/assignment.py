from marshmallow import fields
from app import ma
from app.models.assignment import Assignment


class AssignmentSchema(ma.SQLAlchemyAutoSchema):
    """Schema for assignment serialization (FR-010)."""
    class Meta:
        model = Assignment
        include_fk = True
        load_instance = True
    
    assigned_to = fields.Nested('UserSchema', only=('id', 'name', 'email'), dump_only=True)
    assigned_by = fields.Nested('UserSchema', only=('id', 'name', 'email'), dump_only=True)
