import os
import uuid
from dotenv import load_dotenv
import requests
import cv2
import sys
import time

load_dotenv()

def create_uuid():
    return str(uuid.uuid4())

def read_camera_uuid():
    if os.getenv("PRUSA_CAMERA_UUID"):
        return os.getenv("PRUSA_CAMERA_UUID")

    if os.path.exists("/app/fingerprint/camera_uuid.txt"):
        with open("/app/fingerprint/camera_uuid.txt", "r") as file:
            return file.read().strip()
    else:
        new_uuid = create_uuid()
        print(f"Generated new camera UUID: {new_uuid}")
        print(f"Saving camera UUID to file: /app/fingerprint/camera_uuid.txt")
        print(f"Also consider adding PRUSA_CAMERA_UUID={new_uuid} to your .env file")
        sys.stdout.flush()
        with open("/app/fingerprint/camera_uuid.txt", "w") as file:
            file.write(new_uuid)
        return new_uuid

def get_frame_from_rtsp():
    rtsp_url = os.getenv("RTSP_URL")
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        print("Fehler beim Öffnen des RTSP-Streams")
        return None
    
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Fehler beim Lesen des Frames")
        return None
    return frame

def crop_frame(frame, x, y, w, h):
    return frame[y:y+h, x:x+w]

def upload_frame_to_prusa(frame):
    api_url = os.getenv("PRUSA_API_URL")
    prusa_camera_token = os.getenv("PRUSA_CAMERA_TOKEN")
    headers = { "Token": prusa_camera_token, "Fingerprint": read_camera_uuid()}
    response = requests.put(f"{api_url}/c/snapshot", headers=headers, data=cv2.imencode('.jpg', frame)[1].tobytes())
    if not response.ok:
        raise ValueError("Failed to upload frame to Prusa")
    return response.json()


if __name__ == "__main__":
    try:
        print("Starting Prusa RTSP Camera Uploader")
        sys.stdout.flush()
        x = int(os.getenv("CROP_X", 0))
        y = int(os.getenv("CROP_Y", 0))
        w = int(os.getenv("CROP_W", 0))
        h = int(os.getenv("CROP_H", 0))
        while 1:
            frame = get_frame_from_rtsp()
            if frame is not None:
                frame = crop_frame(frame, x, y, w, h)
                upload_frame_to_prusa(frame)
                time.sleep(30)
            else:
                time.sleep(1)
    except Exception as e:
        print(f"Error occurred: {e}")