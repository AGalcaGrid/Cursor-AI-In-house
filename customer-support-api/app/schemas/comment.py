from marshmallow import fields, validate, post_load
from app import ma
from app.models.comment import Comment
from app.utils.security import sanitize_html


class CommentSchema(ma.SQLAlchemyAutoSchema):
    """Schema for comment serialization."""
    class Meta:
        model = Comment
        include_fk = True
        load_instance = True
    
    author = fields.Nested('UserSchema', only=['id', 'email', 'role'], dump_only=True)


class CommentCreateSchema(ma.Schema):
    """Schema for comment creation."""
    content = fields.String(
        required=True,
        validate=validate.Length(min=1, max=10000,
            error='Comment must be between 1 and 10000 characters')
    )
    is_internal = fields.Boolean(load_default=False)
    
    @post_load
    def sanitize_content(self, data, **kwargs):
        """Sanitize HTML content."""
        if 'content' in data:
            data['content'] = sanitize_html(data['content'])
        return data
