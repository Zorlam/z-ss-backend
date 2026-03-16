from marshmallow import Schema, fields, validate, validates, ValidationError


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=100),
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6),
        load_only=True,
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class UserResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(dump_only=True)
    username = fields.Str(dump_only=True)
    role = fields.Str(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)