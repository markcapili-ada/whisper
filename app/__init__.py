import logging

from flask import Flask

from app.api import api
from app.config.app_config import settings as app_settings
from app.extensions.celery import celery_init_app


def create_app():

    app = Flask(__name__)
    app.config.from_object(app_settings)
    # Set up logging
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
    )

    with app.app_context():
        api.init_app(app)
        celery = celery_init_app(app)

    return app, celery
