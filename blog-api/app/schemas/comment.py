from marshmallow import fields, validate
from app import ma
from app.models.comment import Comment


class CommentSchema(ma.SQLAlchemyAutoSchema):
    """Schema for comment serialization."""
    class Meta:
        model = Comment
        include_fk = True
        load_instance = True
    
    author = fields.Nested('UserSchema', only=('id', 'username'), dump_only=True)


class CommentCreateSchema(ma.Schema):
    """Schema for comment creation."""
    content = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2000)
    )
