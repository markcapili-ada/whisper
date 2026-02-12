# Use a CUDA-enabled base image for Python 3.10
FROM nvidia/cuda:11.8.0-base-ubuntu22.04

# Set environment variables to prevent Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Singapore
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Singapore

# Set the working directory inside the container
WORKDIR /app/whisper_api
USER root
# Install system dependencies (ffmpeg and other tools for Whisper)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nano \
    ffmpeg \
    libsndfile1 \
    git \
    nvidia-container-toolkit \
    && rm -rf /var/lib/apt/lists/*

# Create a user and set permissions
# RUN useradd -m -s /bin/bash popos && \
#     echo "popos ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Copy the requirements file from host to container
COPY requirements.txt /app/whisper_api/requirements.txt

# Install Python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/whisper_api/requirements.txt

# Copy the rest of the application code from host to container
COPY ./ /app/whisper_api

# # Expose the port for Flask
# EXPOSE 5000

# CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:create_app()"]

# Switch to non-root user
# USER popos