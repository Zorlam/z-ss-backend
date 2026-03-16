from marshmallow import Schema, fields


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    slug = fields.Str(required=True)
    description = fields.Str(load_default=None)


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(load_default=None)
    price = fields.Decimal(required=True, as_string=True)
    image_url = fields.Str(load_default=None)
    stock = fields.Int(load_default=0)
    category_id = fields.Int(load_default=None)
    sku = fields.Str(load_default=None)
    is_active = fields.Bool(load_default=True)
    sizes = fields.Str(load_default=None)
    material = fields.Str(load_default=None)
    care_instructions = fields.Str(load_default=None)
    color = fields.Str(load_default=None)


class ProductUpdateSchema(Schema):
    name = fields.Str(load_default=None)
    description = fields.Str(load_default=None)
    price = fields.Decimal(as_string=True, load_default=None)
    image_url = fields.Str(load_default=None)
    stock = fields.Int(load_default=None)
    category_id = fields.Int(load_default=None)
    sku = fields.Str(load_default=None)
    is_active = fields.Bool(load_default=None)
    sizes = fields.Str(load_default=None)
    material = fields.Str(load_default=None)
    care_instructions = fields.Str(load_default=None)
    color = fields.Str(load_default=None)