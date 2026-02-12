from moviepy import AudioFileClip


def convert_audio(input_file, output_file):
    audio = AudioFileClip(input_file)
    audio.write_audiofile(output_file, fps=8000, nbytes=2, buffersize=2000, codec="pcm_s16le")
    print(f"Audio converted successfully: {output_file}")
