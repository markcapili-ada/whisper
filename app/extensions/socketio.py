from flask import current_app
from socketio import Client

from app.config.app_config import settings as app_settings
from app.config.autocollect_be_config import settings as autocollect_settings


WAIT_TIMEOUT = 2

sio = Client()


@sio.event
def connect():
    print("Successfully connected to the server!")
    current_app.logger.info("Websocket successfully connected.")


@sio.event
def disconnect():
    print("Disconnected from the server.")
    current_app.logger.warning("Websocket disconnected. Reconnection attempts will follow if enabled.")


@sio.event
def connect_error(data):
    print(f"Connection failed: {data}")
    current_app.logger.error(f"Websocket connection error: {data}")


@sio.event
def my_response(data):
    print(f"Received response from server: {data}")


def sio_connect(sio: Client):
    api_pass = autocollect_settings.password
    api_user = autocollect_settings.username
    url = autocollect_settings.url
    if app_settings.env != "development":
        url = f"{autocollect_settings.url}?api_key={api_user}:{api_pass}"
        current_app.logger.info(f"Websocket connected to production")
    else:
        current_app.logger.info(f"Websocket connected to development")
    sio.connect(
        url,
        namespaces="/whisper",
        wait=True,
        retry=True,
        wait_timeout=WAIT_TIMEOUT,
    )
