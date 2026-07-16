from marshmallow import fields, validate, validates, ValidationError
from app import ma
from app.models.user import User, Address
from app.utils.security import validate_password_strength


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema for user serialization."""
    class Meta:
        model = User
        exclude = ('password_hash',)
        load_instance = True


class UserRegistrationSchema(ma.Schema):
    """Schema for user registration."""
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=8),
        load_only=True
    )
    first_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    last_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    phone = fields.String(validate=validate.Length(max=20), allow_none=True)
    
    @validates('password')
    def validate_password(self, value):
        is_valid, error = validate_password_strength(value)
        if not is_valid:
            raise ValidationError(error)


class UserLoginSchema(ma.Schema):
    """Schema for user login."""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class AddressSchema(ma.SQLAlchemyAutoSchema):
    """Schema for address serialization."""
    class Meta:
        model = Address
        load_instance = True
        exclude = ('user',)


class AddressCreateSchema(ma.Schema):
    """Schema for creating address."""
    address_type = fields.String(
        required=True,
        validate=validate.OneOf(['shipping', 'billing'])
    )
    street_address = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    apartment = fields.String(validate=validate.Length(max=50), allow_none=True)
    city = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    state = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    postal_code = fields.String(
        required=True,
        validate=validate.Length(min=1, max=20)
    )
    country = fields.String(
        validate=validate.Length(min=2, max=100),
        load_default='US'
    )
    is_default = fields.Boolean(load_default=False)
