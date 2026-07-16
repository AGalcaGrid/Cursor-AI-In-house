from marshmallow import fields
from app import ma
from app.models.notification import Notification


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    """Schema for notification serialization."""
    class Meta:
        model = Notification
        include_fk = True
        load_instance = True


class NotificationUpdateSchema(ma.Schema):
    """Schema for marking notifications as read."""
    is_read = fields.Boolean(required=True)
