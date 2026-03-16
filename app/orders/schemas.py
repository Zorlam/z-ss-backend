from marshmallow import Schema, fields, validate


class CreateOrderSchema(Schema):
    shipping_address = fields.Str(required=True, validate=validate.Length(min=5))
    notes = fields.Str(load_default=None)


class UpdateOrderStatusSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
        ),
    )