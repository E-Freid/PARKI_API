from flask import request
from flask_cors import cross_origin
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from schemas import ParkingSchema, UpdateParkingSchema
from datetime import datetime, timedelta
from geopy.distance import great_circle
import time

from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from Models import ParkingModel
from GetStatusThread import GetStatusThread

last_update_time = datetime.now()
BATCH_SIZE = 3
blp = Blueprint("parkings", __name__, description="operations on parkings.")


def sort_parkings_by_location(parkings, lat, lon):
    if lat and lon:
        try:
            user_location = (float(lat), float(lon))
            for parking in parkings:
                parking.distance = great_circle((parking.latitude, parking.longitude), user_location).km
            parkings.sort(key=lambda p: p.distance)
        except ValueError:
            abort(400, message="Invalid latitude or longitude.")


def calculate_distance(parking, lat, lon):
    return great_circle((parking.latitude, parking.longitude), (lat, lon)).km



@cross_origin()
@blp.route("/parking")
class ParkingList(MethodView):
    @blp.response(200, ParkingSchema(many=True))
    def get(self):
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        parkings = ParkingModel.query.all()

        sort_parkings_by_location(parkings, lat, lon)

        return parkings, 200

    @blp.arguments(ParkingSchema)
    def post(self, parking_data):
        parking = ParkingModel(**parking_data)
        try:
            db.session.add(parking)
            db.session.commit()
            return {"message": "Parking added successfully."}, 201
        except IntegrityError:
            abort(400, message="Parking with that ID already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while adding the parking.")


@blp.route("/parking/<int:id>")
class Parking(MethodView):
    @blp.response(200, ParkingSchema)
    def get(self, id):
        parking = ParkingModel.query.get_or_404(id)
        return parking

    @blp.arguments(UpdateParkingSchema)
    @blp.response(200, ParkingSchema)
    def put(self, parking_data, id):
        parking = ParkingModel.query.get_or_404(id)
        update_data = {"park_id": None, "name": None, "address": None, "status": None, "latitude": None, "longitude": None}
        for data in ["park_id", "name", "address", "status", "latitude", "longitude"]:
            if data in parking_data:
                update_data[data] = parking_data[data]
        parking.park_id = update_data["park_id"] or parking.park_id
        parking.name = update_data["name"] or parking.name
        parking.address = update_data["address"] or parking.address
        parking.status = update_data["status"] or parking.status
        parking.latitude = update_data["latitude"] or parking.latitude
        parking.longitude = update_data["longitude"] or parking.longitude
        try:
            db.session.add(parking)
            db.session.commit()
            return parking, 200
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the parking.")

    def delete(self, id):
        parking = ParkingModel.query.get_or_404(id)
        try:
            db.session.delete(parking)
            db.session.commit()
            return {"message": "Parking deleted successfully."}, 200
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the parking.")


@blp.route("/parking/free")
class FreeParkingList(MethodView):
    @blp.response(200, ParkingSchema(many=True))
    def get(self):
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        parkings = ParkingModel.query.filter(ParkingModel.status.in_(["פנוי", "יש מעט מקומות"])).all()

        sort_parkings_by_location(parkings, lat, lon)

        return parkings


@blp.route("/statuses")
class UpdateStatuses(MethodView):
    @blp.response(200, ParkingSchema(many=True))
    def post(self):
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        if not lat or not lon:
            abort(400, message="Latitude and longitude are required.")

        parkings = ParkingModel.query.filter(~ParkingModel.status.in_(["פעיל", "אין מידע"])).all()
        parkings_with_distance = [(parking, calculate_distance(parking, lat, lon)) for parking in parkings]
        closest_parkings = sorted(parkings_with_distance, key=lambda x: x[1])[:5]

        threads = []
        for parking, distance in closest_parkings:
            status_thread = GetStatusThread(parking.park_id)
            status_thread.start()
            threads.append(status_thread)

        returned_parkings = []
        for thread in threads:
            thread.join()
            parking = ParkingModel.query.filter_by(park_id=thread.parking_id).first()
            parking.status = thread.result
            try:
                db.session.add(parking)
                db.session.commit()
                parking.distance = calculate_distance(parking, lat, lon)
                returned_parkings.append(parking)
            except SQLAlchemyError:
                abort(500, message="An error occurred while updating the parking.")

        return returned_parkings
