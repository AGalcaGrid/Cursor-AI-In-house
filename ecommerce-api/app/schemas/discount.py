from marshmallow import fields, validate
from app import ma
from app.models.discount import DiscountCode


class DiscountCodeSchema(ma.SQLAlchemyAutoSchema):
    """Schema for discount code serialization."""
    is_valid = fields.Boolean(dump_only=True)
    
    class Meta:
        model = DiscountCode
        load_instance = True
        exclude = ('usage_history',)


class DiscountCodeCreateSchema(ma.Schema):
    """Schema for creating discount code."""
    code = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    description = fields.String(validate=validate.Length(max=200), allow_none=True)
    discount_type = fields.String(
        required=True,
        validate=validate.OneOf(['percentage', 'fixed'])
    )
    discount_value = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0)
    )
    min_purchase_amount = fields.Decimal(
        as_string=True,
        validate=validate.Range(min=0),
        allow_none=True
    )
    max_discount_amount = fields.Decimal(
        as_string=True,
        validate=validate.Range(min=0),
        allow_none=True
    )
    usage_limit = fields.Integer(validate=validate.Range(min=1), allow_none=True)
    usage_limit_per_user = fields.Integer(
        validate=validate.Range(min=1),
        load_default=1
    )
    is_active = fields.Boolean(load_default=True)
    valid_from = fields.DateTime(allow_none=True)
    valid_until = fields.DateTime(allow_none=True)


class ValidateDiscountSchema(ma.Schema):
    """Schema for validating discount code."""
    code = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    cart_total = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0)
    )
