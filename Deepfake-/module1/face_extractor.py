import cv2
import os

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


def extract_faces(
    frame_dir,
    output_dir
):

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    face_count = 0

    for img_name in os.listdir(
        frame_dir
    ):

        img_path = os.path.join(
            frame_dir,
            img_name
        )

        img = cv2.imread(
            img_path
        )

        if img is None:
            continue

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        if len(faces) == 0:
            continue

        faces = sorted(
            faces,
            key=lambda x:
            x[2] * x[3],
            reverse=True
        )

        x, y, w, h = faces[0]

        face = img[
            y:y+h,
            x:x+w
        ]

        face = cv2.resize(
            face,
            (300, 300)
        )

        save_path = os.path.join(
            output_dir,
            img_name
        )

        cv2.imwrite(
            save_path,
            face
        )

        face_count += 1

    print(
        f"{face_count} faces extracted"
    )