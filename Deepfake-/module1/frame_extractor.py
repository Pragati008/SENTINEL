import cv2
import os


def extract_frames(
    video_path,
    output_dir,
    max_frames=20
):

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    cap = cv2.VideoCapture(
        video_path
    )

    if not cap.isOpened():

        print(
            "Error opening video"
        )

        return []

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    positions = [

        int(
            i * total_frames / max_frames
        )

        for i in range(max_frames)

    ]

    frame_paths = []

    for i, pos in enumerate(positions):

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            pos
        )

        ret, frame = cap.read()

        if ret:

            path = os.path.join(
                output_dir,
                f"frame_{i}.jpg"
            )

            cv2.imwrite(
                path,
                frame
            )

            frame_paths.append(
                path
            )

    cap.release()

    print(
        f"{len(frame_paths)} frames extracted"
    )

    return frame_paths