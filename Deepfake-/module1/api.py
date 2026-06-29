from fastapi import FastAPI
from fastapi import UploadFile

from fastapi import File

import os
import uuid
import json

from frame_extractor import extract_frames
from face_extractor import extract_faces
from inference import predict_faces
from utils import clear_folder

app = FastAPI(
    title="SENTINEL Module 1",
    version="1.0"
)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)

FRAMES_DIR = os.path.join(
    BASE_DIR,
    "extracted_frames"
)

FACES_DIR = os.path.join(
    BASE_DIR,
    "extracted_faces"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)


@app.get("/")
def root():

    return {
        "message":
        "SENTINEL Deepfake Detection API Running"
    }


@app.post("/analyze-video")
async def analyze_video(
    video: UploadFile = File(...)
):

    clear_folder(
        FRAMES_DIR
    )

    clear_folder(
        FACES_DIR
    )

    unique_name = (
        str(uuid.uuid4())
        + ".mp4"
    )

    video_path = os.path.join(
        UPLOAD_DIR,
        unique_name
    )

    with open(
        video_path,
        "wb"
    ) as buffer:

        buffer.write(
            await video.read()
        )

    extract_frames(
        video_path,
        FRAMES_DIR
    )

    extract_faces(
        FRAMES_DIR,
        FACES_DIR
    )

    result = predict_faces(
        FACES_DIR
    )

    report_path = os.path.join(
        REPORT_DIR,
        "report.json"
    )

    with open(
        report_path,
        "w"
    ) as f:

        json.dump(
            result,
            f,
            indent=4
        )
    return result
@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
    