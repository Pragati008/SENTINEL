import os
import json

import torch
import torch.nn as nn

import torchvision.models as models
import torchvision.transforms as transforms

from PIL import Image

device = "cpu"

model = models.efficientnet_b3()

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    2
)

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "sentinel_deepfake_b3.pth"
)

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=device
    )
)

model.eval()

transform = transforms.Compose([

    transforms.Resize(
        (300,300)
    ),

    transforms.ToTensor(),

    transforms.Normalize(

        mean=[
            0.485,
            0.456,
            0.406
        ],

        std=[
            0.229,
            0.224,
            0.225
        ]
    )
])


def predict_faces(face_dir):

    scores = []

    flagged_frames = []

    files = sorted(
        os.listdir(face_dir)
    )

    for i, img_name in enumerate(files):

        path = os.path.join(
            face_dir,
            img_name
        )

        img = Image.open(
            path
        ).convert("RGB")

        img = transform(
            img
        )

        img = img.unsqueeze(0)

        with torch.no_grad():

            output = model(img)

            prob = torch.softmax(
                output,
                dim=1
            )[0][1]

            score = prob.item()

            scores.append(
                score
            )

            if score > 0.80:

                flagged_frames.append(
                    img_name
                )

    if len(scores) == 0:

        return {

            "result":
            "No Face Detected"

        }

    avg_score = sum(scores) / len(scores)

    confidence = round(
        avg_score * 100,
        2
    )

    if avg_score < 0.30:

        prediction = "REAL"

        trust_score = 95

        risk_level = "LOW"

    elif avg_score < 0.70:

        prediction = "SUSPICIOUS"

        trust_score = 60

        risk_level = "MEDIUM"

    else:

        prediction = "DEEPFAKE"

        trust_score = 10

        risk_level = "HIGH"

    result = {

        "module":
        "Deepfake Detection",

        "prediction":
        prediction,

        "confidence":
        confidence,

        "trust_score":
        trust_score,

        "risk_level":
        risk_level,

        "flagged_frames":
        flagged_frames
    }

    return result