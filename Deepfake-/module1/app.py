import json
import os

from frame_extractor import extract_frames
from face_extractor import extract_faces
from inference import predict_faces
from utils import clear_folder
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

VIDEO_PATH = os.path.join(
    BASE_DIR,
    "uploads",
    "test.mp4"
)

print("Video Path:")
print(VIDEO_PATH)

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

print("Video Exists:",
      os.path.exists(VIDEO_PATH))

print("Frames Folder:",
      FRAMES_DIR)

print("Faces Folder:",
      FACES_DIR)


clear_folder(
    FRAMES_DIR
)

clear_folder(
    FACES_DIR
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)

print(
    "\nStep 1: Extracting Frames..."
)

extract_frames(
    VIDEO_PATH,
    FRAMES_DIR
)

print(
    "\nStep 2: Extracting Faces..."
)

extract_faces(
    FRAMES_DIR,
    FACES_DIR
)

print(
    "\nStep 3: Running Deepfake Detection..."
)

result = predict_faces(
    FACES_DIR
)

print(
    "\nFINAL RESULT"
)

print(
    json.dumps(
        result,
        indent=4
    )
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

print(
    f"\nReport saved at {report_path}"
)