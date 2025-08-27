from marshmallow import Schema, fields, validate


class TodoCreateSchema(Schema):
    title = fields.Str(required=True, description="Short title for the todo", validate=validate.Length(min=1, max=255))
    description = fields.Str(required=False, load_default="", description="Detailed description")
    status = fields.Str(required=False, load_default="pending", validate=validate.OneOf(["pending", "done"]),
                        description="Status of the todo")


class TodoUpdateSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=1, max=255))
    description = fields.Str(required=False)
    status = fields.Str(required=False, validate=validate.OneOf(["pending", "done"]))


class TodoSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    status = fields.Str(required=True)
