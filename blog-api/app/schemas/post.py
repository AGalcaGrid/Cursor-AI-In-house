from marshmallow import fields, validate, post_load
from app import ma
from app.models.post import Post


class PostSchema(ma.SQLAlchemyAutoSchema):
    """Schema for post serialization."""
    class Meta:
        model = Post
        include_fk = True
        load_instance = True
    
    author = fields.Nested('UserSchema', only=('id', 'username'), dump_only=True)
    category = fields.Nested('CategorySchema', only=('id', 'name', 'slug'), dump_only=True)
    comment_count = fields.Method('get_comment_count', dump_only=True)
    
    def get_comment_count(self, obj):
        return obj.comments.count()


class PostCreateSchema(ma.Schema):
    """Schema for post creation."""
    title = fields.String(
        required=True,
        validate=validate.Length(min=5, max=200)
    )
    content = fields.String(
        required=True,
        validate=validate.Length(min=10)
    )
    excerpt = fields.String(
        validate=validate.Length(max=500),
        allow_none=True
    )
    category_id = fields.Integer(allow_none=True)
    is_published = fields.Boolean(load_default=True)


class PostUpdateSchema(ma.Schema):
    """Schema for post updates."""
    title = fields.String(validate=validate.Length(min=5, max=200))
    content = fields.String(validate=validate.Length(min=10))
    excerpt = fields.String(validate=validate.Length(max=500), allow_none=True)
    category_id = fields.Integer(allow_none=True)
    is_published = fields.Boolean()
