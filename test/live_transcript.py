import os
import time

import numpy as np
from pydub import AudioSegment

import whisper


def main():
    SECONDS = 2
    CHUNK_SIZE_MS = SECONDS * 1000  #
    processed_duration = 0
    AUDIO_FILE = "recordings/output_audio.wav"
    model = whisper.load_model("large-v3")

    def process_new_audio():
        nonlocal processed_duration

        audio = AudioSegment.from_file(AUDIO_FILE)
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

                result = model.transcribe(audio=audio_np, language="en")
                print(f"Chunk {processed_duration // 1000}s-{(processed_duration + CHUNK_SIZE_MS) // 1000}s transcription: {result['text']}")

                with open("transcription.txt", "a", encoding="utf-8") as f:
                    f.write(result["text"] + "\n")

                processed_duration += CHUNK_SIZE_MS

        else:
            print("No new audio to process.")

    try:
        while True:
            if os.path.exists(AUDIO_FILE):
                process_new_audio()
            else:
                print(f"Waiting for {AUDIO_FILE} to appear...")
                processed_duration = 0
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped monitoring.")


main()
