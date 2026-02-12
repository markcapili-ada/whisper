import os

from dotenv import load_dotenv

load_dotenv()
# fmt: off
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    UPLOAD_FOLDER = 'uploads'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USER = os.getenv('ADMIN_USER')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    GOOGLE_CREDENTIAL = os.getenv('GOOGLE_CREDENTIAL')
    WATCH_FOLDER_ID = os.getenv('WATCH_FOLDER_ID')
    PORT = os.getenv('PORT')
    FLASK_ENV = os.getenv('FLASK_ENV')
    APP_URL = os.getenv('APP_URL')
    WHISPER_SIZE = 'tiny' if os.getenv('FLASK_ENV') == 'development' else os.getenv('WHISPER_SIZE')
    AUTOCOLLECT_URL = os.getenv('AUTOCOLLECT_URL')
    AUTOCOLLECT_USERNAME = os.getenv('AUTOCOLLECT_USERNAME')
    AUTOCOLLECT_PASSWORD = os.getenv('AUTOCOLLECT_PASSWORD')
    AUDIO_FILE_SERVER_URL = os.getenv('AUDIO_FILE_SERVER_URL')
    AUDIO_FILE_SERVER_BASIC_AUTH_USERNAME = os.getenv('AUDIO_FILE_SERVER_BASIC_AUTH_USERNAME')
    AUDIO_FILE_SERVER_BASIC_AUTH_PASSWORD = os.getenv('AUDIO_FILE_SERVER_BASIC_AUTH_PASSWORD')
    SUPPORTED_FORMAT = ['mp3','wav', 'WAV']
    REDIS_URL = os.getenv('REDIS_URL')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    WHISPER_PARAMS = {
                "beam_size": 10,
                "best_of": 5,
                "condition_on_previous_text": True,
                "fp16": False,
                "initial_prompt": "Audio mainly in English. If audio has no dialog -> 'No Dialog'. Common words used: Fundbox, Speedzone, Late Fee, instalments, E-Bike.",
                "no_speech_threshold": 0.6,
                "patience": 3,
                "suppress_tokens": [
                    -1
                ],
                "task": "transcribe",
                "temperature": 0.3,
                "verbose": True
            }
