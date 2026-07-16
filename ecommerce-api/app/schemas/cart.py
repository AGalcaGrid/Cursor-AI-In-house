from marshmallow import fields, validate
from app import ma
from app.models.cart import Cart, CartItem
from app.schemas.product import ProductSchema


class CartItemSchema(ma.SQLAlchemyAutoSchema):
    """Schema for cart item serialization."""
    product = fields.Nested(ProductSchema, dump_only=True)
    total_price = fields.Decimal(as_string=True, dump_only=True)
    
    class Meta:
        model = CartItem
        load_instance = True
        exclude = ('cart',)


class CartSchema(ma.SQLAlchemyAutoSchema):
    """Schema for cart serialization."""
    items = fields.Nested(CartItemSchema, many=True, dump_only=True)
    total_items = fields.Integer(dump_only=True)
    subtotal = fields.Decimal(as_string=True, dump_only=True)
    discount_amount = fields.Decimal(as_string=True, dump_only=True)
    total = fields.Decimal(as_string=True, dump_only=True)
    is_expired = fields.Boolean(dump_only=True)
    
    class Meta:
        model = Cart
        load_instance = True
        exclude = ('user', 'session_id')


class AddToCartSchema(ma.Schema):
    """Schema for adding item to cart."""
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(
        validate=validate.Range(min=1, max=10),
        load_default=1
    )


class UpdateCartItemSchema(ma.Schema):
    """Schema for updating cart item quantity."""
    quantity = fields.Integer(
        required=True,
        validate=validate.Range(min=0, max=10)
    )


class ApplyDiscountSchema(ma.Schema):
    """Schema for applying discount code."""
    code = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
