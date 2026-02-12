import deepspeed
import numpy as np
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor


# Model and processor setup
model_id = "openai/whisper-large-v3"
processor = AutoProcessor.from_pretrained(model_id)

# Load the model
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)

# DeepSpeed configuration
ds_config = {
    "train_micro_batch_size_per_gpu": 1,
    "fp16": {"enabled": True},  # Enable mixed precision for faster inference
    "tensor_parallel": {"tp_size": torch.cuda.device_count()},  # Use all available GPUs
}

# Initialize DeepSpeed inference engine
model_engine = deepspeed.init_inference(
    model=model,
    config=ds_config,
    mp_size=torch.cuda.device_count(),  # Number of GPUs for tensor parallelism
    dtype=torch.float16,  # Use FP16 for reduced memory
)


# Example audio input (replace with actual audio data)
audio_sample = np.random.randn(16000 * 30).astype("float32")  # 30 seconds of dummy audio

# Preprocess the input audio
inputs = processor(audio_sample, return_tensors="pt", sampling_rate=16000)
input_features = inputs.input_features.to("cuda:0")  # Send to the first GPU

# Run inference with the model
with torch.no_grad():
    generated_ids = model_engine.generate(input_features)

# Decode the output
transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)
print("Transcription:", transcription[0])
