from flask import Flask
from config import app_config


def create_app(config_name):
    application = Flask(__name__)
    application.config.from_object(app_config[config_name])

    return application


app = create_app("development")
from app.views import *
