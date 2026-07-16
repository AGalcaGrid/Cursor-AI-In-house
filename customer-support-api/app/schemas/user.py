from marshmallow import fields, validate
from app import ma
from app.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema for user serialization."""
    class Meta:
        model = User
        exclude = ('password_hash',)
        load_instance = True


class UserLoginSchema(ma.Schema):
    """Schema for user login."""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
