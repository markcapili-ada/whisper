import json
import os
from datetime import datetime
from pathlib import Path

from flask import current_app


def store_transcription(transcription_data, filename):

    json_data = json.dumps(transcription_data, indent=4)
    current_dir = Path(__file__).parent.absolute()
    folder_path = (current_dir / '../../transcriptions').resolve()
    folder_path.mkdir(parents=True, exist_ok=True)

    # Ensure the folder exists, create it if not
    os.makedirs(folder_path, exist_ok=True)

    # Define the file path (filename with folder)
    file_path = folder_path / f"{filename}.json"
    print(filename)
    print(file_path)
    # Write the JSON data to the file
    with open(file_path, 'w') as json_file:
        json_file.write(json_data)

    print(f"JSON file saved at: {file_path}")
    current_app.logger.info(f"JSON file saved at: {file_path}")
    return f"{filename}.json"


def read_json_file(file_path):
    if file_path.is_file():
        with file_path.open('r') as json_file:
            data = json.load(json_file)
            return data
    else:
        return None
