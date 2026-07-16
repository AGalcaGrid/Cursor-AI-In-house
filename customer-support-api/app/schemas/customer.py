from marshmallow import fields, validate, validates, ValidationError
from app import ma
from app.models.customer import Customer
from app.utils.security import validate_password_strength


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    """Schema for customer serialization."""
    class Meta:
        model = Customer
        exclude = ('password_hash',)
        load_instance = True


class CustomerCreateSchema(ma.Schema):
    """Schema for customer registration."""
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=8),
        load_only=True
    )
    phone = fields.String(
        validate=validate.Length(max=20),
        allow_none=True
    )
    company = fields.String(
        validate=validate.Length(max=100),
        allow_none=True
    )
    
    @validates('password')
    def validate_password(self, value):
        is_valid, error = validate_password_strength(value)
        if not is_valid:
            raise ValidationError(error)


class CustomerUpdateSchema(ma.Schema):
    """Schema for customer profile updates."""
    name = fields.String(validate=validate.Length(min=2, max=100))
    phone = fields.String(validate=validate.Length(max=20), allow_none=True)
    company = fields.String(validate=validate.Length(max=100), allow_none=True)
