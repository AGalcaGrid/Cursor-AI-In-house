from marshmallow import fields, validate, validates, ValidationError
from app import ma
from app.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema for user serialization."""
    class Meta:
        model = User
        exclude = ('password_hash',)
        load_instance = True


class UserCreateSchema(ma.Schema):
    """Schema for user registration."""
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=80)
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        load_only=True
    )
    
    @validates('username')
    def validate_username(self, value):
        if User.query.filter_by(username=value).first():
            raise ValidationError('Username already exists')
    
    @validates('email')
    def validate_email(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError('Email already registered')


class UserLoginSchema(ma.Schema):
    """Schema for user login."""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
