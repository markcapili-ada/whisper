import json
import os
import time
from datetime import datetime

import numpy as np
import torch
from celery import shared_task
from flask import current_app
from pydub import AudioSegment

from app.helpers.transcription_helper import store_transcription
from app.services.audio_service import AudioService
from app.services.llm_service import LLMService
from app.services.webhook_service import push_data_to_webhook, push_webhook
from app.utils import get_file_absolute


@shared_task(bind=True)
def transcribe_task(self, filename, file_format, is_webhook=False, webhook_url=None):
    from app import create_app

    app, _ = create_app()
    with app.app_context():
        from app.services.whisper_service import WhisperService

        try:
            whisper_service = WhisperService()
            uploads_dir = get_file_absolute("uploads")
            file_path = uploads_dir / filename

            current_app.logger.info(f"Transcribing {filename}")

            # Load model and transcribe
            result = whisper_service.transcribe(str(file_path))

            # Clear CUDA cache if using GPU
            if hasattr(torch, 'cuda'):
                torch.cuda.empty_cache()

            res = {
                "transcription": result["text"],
            }

            filename_without_ext = filename.replace(f".{file_format}", "")
            # Store to file system
            store_transcription(res, filename_without_ext)
            parts = filename_without_ext.split("-")

            audio_created_at = datetime.strptime(parts[0], "%Y%m%d")

            current_app.logger.info(f"{filename}: transcribed")
            if is_webhook:
                push_webhook(
                    {
                        "filename": filename,
                        "transcript": result["text"],
                    },
                    webhook_url,
                )
                current_app.logger.info(f"Pushed transcription to {webhook_url} for {filename}")
            else:
                # This is for autocollect that is still using the basic auth
                callee_channel_id = parts[1]
                caller_channel_id = parts[2]

                push_data_to_webhook(
                    {
                        "callee_channel_id": callee_channel_id,
                        "caller_channel_id": caller_channel_id,
                        "audio_created_at": audio_created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "transcription": result["text"],
                    }
                )
                current_app.logger.info(f"Pushed transcription to autocollect webhook for {filename}")
            # Clean up the uploaded file after processing
            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as e:
            current_app.logger.error(f"[transcribe_task] Error transcribing {filename}: {str(e)}")
            # Ensure cleanup even on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise  # Re-raise the exception for Celery to handle


@shared_task(bind=True)
def live_transcription(self, filename: str, chunk_second=8):
    from app import create_app

    app, _ = create_app()
    with app.app_context():
        from app.extensions.socketio import sio, sio_connect
        from app.services.whisper_service import WhisperService

        try:
            whisper_service = WhisperService()
            audio_service = AudioService()
            turbo_pipe = whisper_service.load_turbo_model()

            try:
                sio_connect(sio)
            except Exception as e:
                current_app.logger.error(f"[live_transcription] Error connecting to socketio: {str(e)}")

            # model = whisper.load_model("large-v2")
            SECONDS = chunk_second if chunk_second > 3 else 3
            CHUNK_SIZE_MS = SECONDS * 1000  #
            processed_duration = 0

            # Get info from the filename
            file_format = filename.split(".")[-1]
            filename_wo_ext = filename.replace(f".{file_format}", "")
            parts = filename_wo_ext.split("-")
            callee = parts[1]
            caller = parts[2]
            current_file_size = 0
            retry_get_file_counter = 0
            retry_get_file_threshold = 30
            INDEX = 0

            def process_new_audio(audio_file_path):
                nonlocal processed_duration
                nonlocal INDEX
                nonlocal retry_get_file_counter

                audio = AudioSegment.from_file(audio_file_path)
                total_duration = len(audio)

                print(f"(total_duration - processed_duration): {(total_duration - processed_duration)} ")
                if total_duration > processed_duration and (total_duration - processed_duration) >= CHUNK_SIZE_MS:
                    print(f"New audio detected. Processing from {processed_duration}ms to {total_duration}ms...")

                    while processed_duration < total_duration and (total_duration - processed_duration) >= CHUNK_SIZE_MS:
                        # Extract the next chunk
                        chunk = audio[processed_duration : processed_duration + CHUNK_SIZE_MS]

                        audio_data = np.array(chunk.get_array_of_samples())
                        max_value = max(abs(audio_data))

                        if max_value > 0:
                            audio_np = (audio_data / max_value).astype("float32")
                        else:
                            audio_np = audio_data.astype("float32")

                        # result = model.transcribe(audio=audio_np, language="en")
                        result = whisper_service.whisper_turbo_transcribe(turbo_pipe, audio_np)
                        print(f"Chunk {processed_duration // 1000}s-{(processed_duration + CHUNK_SIZE_MS) // 1000}s transcription: {result['text']}")

                        if result["text"] and result["text"].strip():
                            # sio_connect(sio)
                            data = {
                                'chunk_index': INDEX,
                                "callee_channel_id": callee,
                                "caller_channel_id": caller,
                                "transcription": result["text"],
                            }
                            sio.send(data, namespace="/whisper")
                            retry_get_file_counter = 0  # reset
                            INDEX = INDEX + 1
                            # sio.disconnect()

                        # current_app.logger.info(f"message {filename}, data: {data}")
                        processed_duration += CHUNK_SIZE_MS

                else:
                    print("No new audio to process.")
                    retry_get_file_counter += 1

            while True:
                audio_file_path, file_size = audio_service.get_file(filename=filename, save_to="recordings")
                current_app.logger.info(f"[audio_file_path] {audio_file_path}")
                if file_size == current_file_size:
                    retry_get_file_counter += 1

                if os.path.exists(audio_file_path):
                    process_new_audio(str(audio_file_path))
                    current_file_size = file_size

                else:
                    print(f"Waiting for {str(audio_file_path)} to appear...")
                    processed_duration = 0
                    current_file_size = 0

                if retry_get_file_counter == retry_get_file_threshold:
                    current_app.logger.info(f"[live_transcription] Breaking live transcript file not growing in size")
                    break
                time.sleep(1)

        except Exception as e:
            current_app.logger.error(f"[live_transcription] Error live transcription: {e}")


@shared_task(bind=True)
def live_transcription2(self, filename: str, chunk_second=8):
    from app import create_app

    app, _ = create_app()
    with app.app_context():
        from app.extensions.socketio import sio, sio_connect
        from app.services.whisper_service import WhisperService

        try:
            whisper_service = WhisperService()
            audio_service = AudioService()
            turbo_pipe = whisper_service.load_turbo_model()

            # model = whisper.load_model("large-v2")
            SECONDS = chunk_second if chunk_second > 3 else 3
            CHUNK_SIZE_MS = SECONDS * 1000  #
            processed_duration = 0

            # Get info from the filename
            # file_format = filename.split(".")[-1]
            # filename_wo_ext = filename.replace(f".{file_format}", "")
            # parts = filename_wo_ext.split("-")
            # callee = parts[1]
            # caller = parts[2]
            current_file_size = 0
            retry_get_file_counter = 0
            retry_get_file_threshold = 30
            INDEX = 0
            current_chunk = 0
            transcription_arr = []
            MAX_CHUNK_SIZE_MS = 30 * 1000

            def process_new_audio(audio_file_path):
                nonlocal processed_duration
                nonlocal INDEX
                nonlocal retry_get_file_counter
                nonlocal current_chunk
                nonlocal transcription_arr

                to_transcribe_ms = 0
                audio = AudioSegment.from_file(audio_file_path)
                total_duration = len(audio)
                if (current_chunk + 1) * MAX_CHUNK_SIZE_MS > total_duration:
                    chunk = audio[current_chunk * MAX_CHUNK_SIZE_MS : total_duration]
                    audio_data = np.array(chunk.get_array_of_samples())
                    max_value = max(abs(audio_data))

                    if max_value > 0:
                        audio_np = (audio_data / max_value).astype("float32")
                    else:
                        audio_np = audio_data.astype("float32")
                    processed_duration = total_duration - to_transcribe_ms
                    result = whisper_service.whisper_turbo_transcribe(turbo_pipe, audio_np)
                    if len(transcription_arr) < (current_chunk + 1):
                        transcription_arr.append(result["text"])
                    else:
                        transcription_arr[current_chunk] = result["text"]

                else:
                    chunk = audio[current_chunk * MAX_CHUNK_SIZE_MS : (current_chunk + 1) * MAX_CHUNK_SIZE_MS]

                    audio_data = np.array(chunk.get_array_of_samples())
                    max_value = max(abs(audio_data))

                    if max_value > 0:
                        audio_np = (audio_data / max_value).astype("float32")
                    else:
                        audio_np = audio_data.astype("float32")
                    processed_duration = total_duration - to_transcribe_ms
                    result = whisper_service.whisper_turbo_transcribe(turbo_pipe, audio_np)
                    if len(transcription_arr) < current_chunk + 1:
                        transcription_arr.append(result["text"])
                    else:
                        transcription_arr[current_chunk] = result["text"]
                    current_chunk += 1
                current_app.logger.info(f"[live_transcription] {transcription_arr}")
                with open("transcription_log.txt", "w") as log_file:
                    log_file.write(f"[live_transcription] {transcription_arr}\n")

            while True:
                audio_file_path, file_size = audio_service.get_file(filename=filename, save_to="recordings")
                current_app.logger.info(f"[audio_file_path] {audio_file_path}")
                if file_size == current_file_size:
                    retry_get_file_counter += 1

                if os.path.exists(audio_file_path):
                    process_new_audio(str(audio_file_path))
                    current_file_size = file_size

                else:
                    print(f"Waiting for {str(audio_file_path)} to appear...")
                    processed_duration = 0
                    current_file_size = 0

                if retry_get_file_counter == retry_get_file_threshold:
                    current_app.logger.info(f"[live_transcription] Breaking live transcript file not growing in size")
                    break
                time.sleep(1)

        except Exception as e:
            current_app.logger.error(f"[live_transcription] Error live transcription: {e}")


@shared_task(bind=True)
def diarized_transcription_task(
    self,
    agent_audio_filename: str,
    client_audio_filename: str,
    unique_id: str,
    webhook_url: str = None,
    combined_audio_filename: str = None,
):
    from app import create_app

    app, _ = create_app()
    with app.app_context():
        from app.services.whisper_service import WhisperService

        try:
            whisper_service = WhisperService()
            uploads_dir = get_file_absolute("uploads")
            agent_audio_file_path = uploads_dir / agent_audio_filename
            client_audio_file_path = uploads_dir / client_audio_filename
            combined_audio_file_path = uploads_dir / combined_audio_filename

            current_app.logger.info(f"Transcribing {agent_audio_filename} and {client_audio_filename}")

            # Load model and transcribe
            agent_result = whisper_service.transcribe(str(agent_audio_file_path), with_segments=True)
            client_result = whisper_service.transcribe(str(client_audio_file_path), with_segments=True)
            combined_result = whisper_service.transcribe(str(combined_audio_file_path), with_segments=True)
            llm_service = LLMService()
            diarized_result = llm_service.diarize_transcription(agent_result, client_result, combined_result)
            print(diarized_result)

            # Clear CUDA cache if using GPU
            if hasattr(torch, 'cuda'):
                torch.cuda.empty_cache()

            res = {
                "transcription": diarized_result,
            }

            store_transcription(res, unique_id)

            current_app.logger.info(f"{agent_audio_filename} and {client_audio_filename}: transcribed")

            push_webhook(
                {
                    "unique_id": unique_id,
                    "transcription": diarized_result['conversation'],
                },
                webhook_url,
            )
            current_app.logger.info(f"Pushed transcription to {webhook_url} for {agent_audio_filename} and {client_audio_filename}")

        except Exception as e:
            current_app.logger.error(f"[diarized_transcription_task] Error transcribing {agent_audio_filename} and {client_audio_filename}: {str(e)}")

            raise
        finally:
            if os.path.exists(agent_audio_file_path):
                os.remove(agent_audio_file_path)
            if os.path.exists(client_audio_file_path):
                os.remove(client_audio_file_path)
