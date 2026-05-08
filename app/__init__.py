from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    # IMPORTAR BLUEPRINTS
    from app.routes.auth import auth
    from app.routes.dashboard import dashboard
    from app.routes.api import api

    # REGISTRAR BLUEPRINTS
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    return app