FROM python:3.12-slim

# Systemdependencies für OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p /app/fingerprint

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY prusa_rtsp_cam.py /app/

# user
RUN useradd -ms /bin/bash prusa_user
RUN chown prusa_user:prusa_user /app

USER prusa_user



CMD ["python", "prusa_rtsp_cam.py"]