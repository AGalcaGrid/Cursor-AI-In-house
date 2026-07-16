from marshmallow import fields, validate
from app import ma
from app.models.product import Product


class ProductSchema(ma.SQLAlchemyAutoSchema):
    """Schema for product serialization."""
    in_stock = fields.Boolean(dump_only=True)
    is_low_stock = fields.Boolean(dump_only=True)
    discount_percentage = fields.Integer(dump_only=True)
    
    class Meta:
        model = Product
        load_instance = True
        exclude = ('cart_items', 'order_items')


class ProductCreateSchema(ma.Schema):
    """Schema for creating product."""
    sku = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    description = fields.String(allow_none=True)
    price = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0)
    )
    compare_at_price = fields.Decimal(
        as_string=True,
        validate=validate.Range(min=0),
        allow_none=True
    )
    cost = fields.Decimal(
        as_string=True,
        validate=validate.Range(min=0),
        allow_none=True
    )
    category = fields.String(validate=validate.Length(max=100), allow_none=True)
    brand = fields.String(validate=validate.Length(max=100), allow_none=True)
    image_url = fields.String(validate=validate.Length(max=500), allow_none=True)
    stock_quantity = fields.Integer(
        validate=validate.Range(min=0),
        load_default=0
    )
    low_stock_threshold = fields.Integer(
        validate=validate.Range(min=0),
        load_default=10
    )
    weight = fields.Decimal(
        as_string=True,
        validate=validate.Range(min=0),
        allow_none=True
    )
    is_active = fields.Boolean(load_default=True)
    is_featured = fields.Boolean(load_default=False)


class ProductUpdateSchema(ma.Schema):
    """Schema for updating product."""
    name = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    price = fields.Decimal(as_string=True, validate=validate.Range(min=0))
    compare_at_price = fields.Decimal(as_string=True, validate=validate.Range(min=0), allow_none=True)
    category = fields.String(validate=validate.Length(max=100), allow_none=True)
    brand = fields.String(validate=validate.Length(max=100), allow_none=True)
    image_url = fields.String(validate=validate.Length(max=500), allow_none=True)
    stock_quantity = fields.Integer(validate=validate.Range(min=0))
    is_active = fields.Boolean()
    is_featured = fields.Boolean()
