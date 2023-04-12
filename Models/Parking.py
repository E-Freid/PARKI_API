from db import db


class ParkingModel(db.Model):
    __tablename__ = "parkings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    park_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)