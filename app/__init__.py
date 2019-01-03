from flask_api import FlaskAPI
from config.config import app_config


def create_app(config_name):
    app = FlaskAPI(__name__)
    app.config.from_object('config')
    app.config.from_object(app_config[config_name])

    return app
