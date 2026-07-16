from marshmallow import fields, validate
from app import ma
from app.models.comment import Comment


class CommentSchema(ma.SQLAlchemyAutoSchema):
    """Schema for comment serialization."""
    class Meta:
        model = Comment
        include_fk = True
        load_instance = True
    
    author = fields.Nested('UserSchema', only=('id', 'name', 'email', 'role'), dump_only=True)


class CommentCreateSchema(ma.Schema):
    """Schema for comment creation (FR-015, FR-016)."""
    content = fields.String(
        required=True,
        validate=validate.Length(min=1, max=5000)
    )
    is_internal = fields.Boolean(load_default=False)
