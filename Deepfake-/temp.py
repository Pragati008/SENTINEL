import cv2

video = cv2.VideoCapture(
    r"C:\Users\reetg\OneDrive\Desktop\SENTINAL\uploads\test.mp4"
)

print(video.isOpened())