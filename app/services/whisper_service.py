import os
from typing import Any

import numpy as np
import torch
import torchvision
import whisperx
from flask import current_app
from pydub import AudioSegment
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from app.config.app_config import settings


# For the warnings
torchvision.disable_beta_transforms_warning()
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True


class WhisperService:
    # Check for Apple Silicon (M1/M2/M3) first, then CUDA, then fall back to CPU
    device = "mps" if torch.backends.mps.is_available() and settings.ai_env == "MPS" else "cuda" if torch.cuda.is_available() and settings.ai_env == "GPU" else "cpu"
    torch_dtype = torch.float32
    turbo_model_id = "openai/whisper-large-v3-turbo"
    turbo_model = None

    def transcribe(self, file_path, diarization=False, with_segments=False):
        result = None  # Initialize result variable
        try:
            audio_file = file_path
            audio = whisperx.load_audio(audio_file)
            batch_size = 16

            # Determine appropriate compute type based on device
            compute_type = "float16" if self.device == "cuda" else "float32"

            asr_options = {"hotwords": None}
            model = whisperx.load_model("large-v2", self.device, compute_type=compute_type, asr_options=asr_options)
            model_a, metadata = whisperx.load_align_model(language_code="en", device=self.device)
            result = model.transcribe(
                audio,
                batch_size=batch_size,
                language="en",
                print_progress=True,
            )
            print(result)

            if with_segments:
                res = {"text": ""}
                for entry in result["segments"]:
                    if "text" in entry:

                        res["text"] += f"({entry['start']}:{entry['end']}){entry['text']}\n"
                # Optionally, strip trailing newline if present
                res["text"] = res["text"].rstrip('\n')
                return res

            if not diarization:
                res = {"text": ""}
                for entry in result["segments"]:
                    if "text" in entry:
                        res["text"] = f"{res['text']} {entry['text']}"
                return res

            # For diarization:
            result = whisperx.align(
                result["segments"],
                model_a,
                metadata,
                audio,
                self.device,
                return_char_alignments=False,
            )
            # TODO ADD HF TOKEN VIA ENV
            diarize_model = whisperx.DiarizationPipeline(device=self.device, model_name="pyannote/speaker-diarization-3.1")
            diarize_segments = diarize_model(audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)
            transcription_with_speakers = self.structure_transcription(result["segments"])
            res = {}
            res["text"] = transcription_with_speakers

            return res

        except Exception as e:
            print(f"Error transcribing file: {e}")
            current_app.logger.info(f"Error transcribing a file: {e}")

        finally:
            if os.path.isfile(file_path):
                os.remove(file_path)

    def structure_transcription(self, transcription_data):
        structured_transcription = []

        for entry in transcription_data:
            # Check if both 'speaker' and 'text' keys exist in the entry
            if "speaker" in entry and "text" in entry:
                speaker = entry["speaker"]
                text = entry["text"]
                structured_transcription.append(f"{speaker}: {text}")

        return "\n".join(structured_transcription)

    def load_turbo_model(self):
        self.turbo_model = AutoModelForSpeechSeq2Seq.from_pretrained(self.turbo_model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
        self.turbo_model.to(self.device)

        processor = AutoProcessor.from_pretrained(self.turbo_model_id)

        pipe = pipeline(
            "automatic-speech-recognition",
            model=self.turbo_model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
        return pipe

    def whisper_turbo_transcribe(self, pipe, audio_np):
        result = pipe(audio_np)
        return result
