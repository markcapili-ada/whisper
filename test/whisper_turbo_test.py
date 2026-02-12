import numpy as np
import torch
from pydub import AudioSegment
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float32

model_id = "openai/whisper-large-v3-turbo"

model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

audio = AudioSegment.from_file('recordings/20241129-1732868177.768-1732868181.769.wav')
chunk = audio[1000:180000]

audio_data = np.array(chunk.get_array_of_samples())
max_value = max(abs(audio_data))

if max_value > 0:
    audio_np = (audio_data / max_value).astype("float32")
else:
    audio_np = audio_data.astype("float32")


result = pipe(audio_np)
print(result["text"])
