from app.config.enums import AudioMeta


def is_file_type_supported(filename: str):
    SUPPORTED_FORMATS = AudioMeta.SUPPORTED_FORMATS.value
    file_extension = filename.split('.')[-1]  # Extract file extension
    if file_extension not in SUPPORTED_FORMATS:
        return False
    return True
