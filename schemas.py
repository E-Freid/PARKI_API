from marshmallow import Schema, fields


class ParkingSchema(Schema):
    id = fields.Integer(dump_only=True)
    park_id = fields.Integer(required=True, load_only=True)
    name = fields.String(required=True)
    address = fields.String(required=True)
    status = fields.String(dump_only=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    distance = fields.Float(dump_only=True)


class UpdateParkingSchema(Schema):
    park_id = fields.Integer()
    name = fields.String()
    address = fields.String()
    status = fields.String()
    latitude = fields.Float()
    longitude = fields.Float()