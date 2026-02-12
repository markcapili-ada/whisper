from enum import Enum


class AudioMeta(Enum):
    SUPPORTED_FORMATS = ['mp3', 'wav', 'WAV']


class WhisperParams(Enum):
    WHISPER_PARAMS = {
        "beam_size": 10,
        "best_of": 5,
        "condition_on_previous_text": True,
        "fp16": False,
        "initial_prompt": "Audio mainly in English. If audio has no dialog -> 'No Dialog'. Common words used: Fundbox, Speedzone, Late Fee, instalments, E-Bike.",
        "no_speech_threshold": 0.6,
        "patience": 3,
        "suppress_tokens": [-1],
        "task": "transcribe",
        "temperature": 0.3,
        "verbose": True,
    }
