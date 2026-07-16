from marshmallow import fields, validate
from app import ma
from app.models.order import Order, OrderItem
from app.schemas.product import ProductSchema


class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    """Schema for order item serialization."""
    total_price = fields.Decimal(as_string=True, dump_only=True)
    
    class Meta:
        model = OrderItem
        load_instance = True
        exclude = ('order', 'product')


class OrderSchema(ma.SQLAlchemyAutoSchema):
    """Schema for order serialization."""
    items = fields.Nested(OrderItemSchema, many=True, dump_only=True)
    total_items = fields.Integer(dump_only=True)
    can_be_cancelled = fields.Boolean(dump_only=True)
    
    class Meta:
        model = Order
        load_instance = True
        exclude = ('user',)


class CheckoutSchema(ma.Schema):
    """Schema for checkout."""
    # Shipping information
    shipping_first_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    shipping_last_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    shipping_email = fields.Email(required=True)
    shipping_phone = fields.String(validate=validate.Length(max=20), allow_none=True)
    shipping_street_address = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    shipping_apartment = fields.String(validate=validate.Length(max=50), allow_none=True)
    shipping_city = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    shipping_state = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    shipping_postal_code = fields.String(
        required=True,
        validate=validate.Length(min=1, max=20)
    )
    shipping_country = fields.String(
        validate=validate.Length(min=2, max=100),
        load_default='US'
    )
    
    # Billing information
    billing_same_as_shipping = fields.Boolean(load_default=True)
    billing_street_address = fields.String(validate=validate.Length(max=200), allow_none=True)
    billing_apartment = fields.String(validate=validate.Length(max=50), allow_none=True)
    billing_city = fields.String(validate=validate.Length(max=100), allow_none=True)
    billing_state = fields.String(validate=validate.Length(max=100), allow_none=True)
    billing_postal_code = fields.String(validate=validate.Length(max=20), allow_none=True)
    billing_country = fields.String(validate=validate.Length(max=100), allow_none=True)
    
    # Payment information
    payment_method = fields.String(
        required=True,
        validate=validate.OneOf(['card', 'paypal'])
    )
    
    # Notes
    notes = fields.String(allow_none=True)


class PaymentIntentSchema(ma.Schema):
    """Schema for creating payment intent."""
    amount = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0.5)
    )
