import os
from dotenv import load_dotenv

from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate
from flask_cors import CORS

from db import db

from Resources.Parking import blp as ParkingBluepint


def create_app(db_url=None):
    app = Flask(__name__)
    cors = CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    load_dotenv()
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Parki REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['CORS_METHODS'] = ['GET', 'POST', 'PUT', 'DELETE']

    db.init_app(app)
    migrate = Migrate(app, db, compare_type=True)
    api = Api(app)

    api.register_blueprint(ParkingBluepint)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()