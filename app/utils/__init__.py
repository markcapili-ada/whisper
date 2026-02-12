import os
from pathlib import Path


def get_file_absolute(folder: str):
    base_directory = Path(folder)
    base_directory.mkdir(parents=True, exist_ok=True)
    return base_directory.resolve()
