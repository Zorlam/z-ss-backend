from marshmallow import Schema, fields, validate


class AddToCartSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))


class UpdateCartSchema(Schema):
    quantity = fields.Int(required=True, validate=validate.Range(min=1))