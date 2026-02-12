import base64

import requests
from flask import current_app

from app.config.autocollect_be_config import settings
from app.config.webhook_config import settings as webhook_settings


def push_data_to_webhook(data):
    username = settings.username
    password = settings.password
    auth_token = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
    headers = {'Content-Type': 'application/json', 'Authorization': f'Basic {auth_token}'}
    url = f"{settings.url}/backdoor/transcription"

    response = requests.post(url=url, headers=headers, json=data)
    status_code = response.status_code
    try:
        payload = response.json()
    except ValueError:
        payload = response.text

    current_app.logger.info(f"Sent to webhook {url} | Status Code: {status_code} | Response Payload: {payload}")
    print(f"Status Code: {status_code}, Response Payload: {payload}")


# new implementation
def push_webhook(data, url):
    secret_key = webhook_settings.secret_key

    headers = {'Content-Type': 'application/json', 'X-Webhook-Token': f'{secret_key}'}

    response = requests.post(url=url, headers=headers, json=data)
    status_code = response.status_code
    try:
        payload = response.json()
    except ValueError:
        payload = response.text

    current_app.logger.info(f"Sent to webhook {url} | Status Code: {status_code} | Response Payload: {payload}")
    print(f"Status Code: {status_code}, Response Payload: {payload}")
