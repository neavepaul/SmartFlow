import cv2
import numpy as np

# Function to apply color-based masking to isolate green stickers
def apply_color_mask(frame):
    lower_green = np.array([0, 30, 0])
    upper_green = np.array([100, 255, 100])
    mask = cv2.inRange(frame, lower_green, upper_green)
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
    return masked_frame

# Read the video file
video_path = 'green2.mp4'  # Replace with the actual path to your video file
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    # Apply color-based masking to isolate green stickers
    masked_frame = apply_color_mask(frame)

    # Display the original frame and the masked frame
    cv2.imshow('Original Frame', frame)
    cv2.imshow('Masked Frame', masked_frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
