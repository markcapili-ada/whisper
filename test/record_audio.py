import wave

import pyaudio

# Configuration for audio recording
CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # 16-bit audio format
CHANNELS = 1  # Mono audio
RATE = 16000  # Sampling rate (Hz)
OUTPUT_FILE = "recordings/output_audio.wav"


def record_audio():
    """Records audio from the microphone and saves it to a WAV file in real-time."""
    audio = pyaudio.PyAudio()

    # Open the audio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Recording... Press Ctrl+C to stop.")

    # Create or overwrite the output file
    wf = wave.open(OUTPUT_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    try:
        while True:
            data = stream.read(CHUNK)
            wf.writeframes(data)  # Write data to the file in chunks
    except KeyboardInterrupt:
        print("\nRecording stopped.")
    finally:
        # Cleanup resources
        stream.stop_stream()
        stream.close()
        audio.terminate()
        wf.close()
        print(f"Audio saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    record_audio()
