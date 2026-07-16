from marshmallow import fields, validate
from app import ma
from app.models.category import Category


class CategorySchema(ma.SQLAlchemyAutoSchema):
    """Schema for category serialization."""
    class Meta:
        model = Category
        load_instance = True
    
    post_count = fields.Method('get_post_count', dump_only=True)
    
    def get_post_count(self, obj):
        return obj.posts.count()
