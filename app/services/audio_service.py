import base64
import os

import requests

from app.config.audio_file_server_config import settings
from app.helpers.audio_helper import convert_audio
from app.utils import get_file_absolute


class AudioService:
    def __init__(self) -> None:
        self.audio_server_url = settings.url
        self.username = settings.username
        self.password = settings.password
        self.auth_token = base64.b64encode(f"{self.username}:{self.password}".encode("utf-8")).decode("utf-8")

    def get_file(self, filename, save_to="uploads"):

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.auth_token}",
        }
        url = f"{self.audio_server_url}/file/?filename={filename}"
        try:
            response = requests.get(url, headers=headers)
            status_code = response.status_code
            # Download to temp file
            if status_code == 200:
                temp_dir = get_file_absolute('temp')
                file_path_temp = temp_dir / filename

                with open(file_path_temp, "wb") as file:
                    file.write(response.content)

                uploads_dir = get_file_absolute(save_to)
                file_path = uploads_dir / filename
                convert_audio(str(file_path_temp), str(file_path))
                if os.path.isfile(file_path_temp):
                    os.remove(file_path_temp)

                # get file size
                file_size = os.path.getsize(file_path)
                return file_path, file_size
            else:
                return None, None
        except Exception as e:
            print(f"[get_file] An error occurred: {e}")
            return None, None

    def upload_file_to_S3(self, file_path, s3_upload_url):
        try:
            with open(file_path, 'rb') as file:
                file_binary = file.read()
                headers = {"Content-Type": "audio/x-wav"}

                response = requests.put(s3_upload_url, data=file_binary, headers=headers)
                if response.status_code == 200:
                    print(f"[upload_file_to_S3] Uploaded file to S3: {file_path}")
                else:
                    print(f"[upload_file_to_S3] Upload failed with status code: {response.status_code}")
                    print(f"[upload_file_to_S3] Response: {response.text}")
                    raise Exception(f"[upload_file_to_S3] Upload failed with status code: {response.status_code}")
        except Exception as e:
            print(f"[upload_file_to_S3] Error uploading file to S3: {str(e)}")
            raise e
