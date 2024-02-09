import cv2
import numpy as np
from filterpy.kalman import KalmanFilter
from sort import Sort
import time
from picamera2 import Picamera2

# Define the lower and upper bounds for coloured stickers
lower_color = np.array([35, 50, 50])
upper_color = np.array([85, 255, 255])

tracker = Sort()

waiting_times_left_lane = {}
waiting_times_right_lane = {}
last_appearance = {}

width = 960
height = 540
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (width, height)}))
picam2.start()

# Dividing line between the left and right lanes
lane_divider_x = width // 2

def calculate_time_in_frame(object_id, lane_id):
    if object_id in waiting_times_left_lane and lane_id == "left_lane":
        return time.time() - waiting_times_left_lane[object_id]
    elif object_id in waiting_times_right_lane and lane_id == "right_lane":
        return time.time() - waiting_times_right_lane[object_id]
    else:
        return 0

while True:
    start_time = time.time()
    frame = picam2.capture_array()

    # Convert the frame to the HSV color space to extract coloured object.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only the specified color range
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Update object information and draw bounding boxes
    detections = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h > 2500:  # minimum object size pixels
            detections.append([x, y, x+w, y+h])

    # Update tracker
    if len(detections) > 0:
        detections = np.array(detections)
        trackers = tracker.update(detections)

        # Draw bounding boxes and IDs
        for d in trackers:
            object_id = int(d[4])
            lane_id = "left_lane" if d[0] < lane_divider_x else "right_lane"

            last_appearance[object_id] = time.time()

            # bounding box
            cv2.rectangle(frame, (int(d[0]), int(d[1])), (int(d[2]), int(d[3])), (0, 255, 0), 2)

            # object ID
            cv2.putText(frame, f"ID: {object_id}", (int(d[0]), int(d[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # time per object
            time_in_frame = calculate_time_in_frame(object_id, lane_id)
            cv2.putText(frame, f"{time_in_frame:.2f}s", (int(d[0]), int(d[1] + h + 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Update cumulative waiting times and last appearance time
            if time_in_frame == 0:
                # Object is considered stopped, update waiting time
                waiting_times_left_lane[object_id] = time.time() if lane_id == "left_lane" else waiting_times_left_lane.get(object_id, 0)
                waiting_times_right_lane[object_id] = time.time() if lane_id == "right_lane" else waiting_times_right_lane.get(object_id, 0)
                last_appearance[object_id] = time.time()

    # Remove vehicles that haven't appeared for a certain time
    current_time = time.time()
    for object_id, last_time in list(last_appearance.items()):
        if current_time - last_time > 2:
            if object_id in waiting_times_left_lane:
                del waiting_times_left_lane[object_id]
            if object_id in waiting_times_right_lane:
                del waiting_times_right_lane[object_id]
            del last_appearance[object_id]

    # Display cumulative waiting times for left and right lanes
    current_time = time.time()

    total_left = 0
    total_right = 0
    for entry in waiting_times_left_lane.values():
        if entry == 0:
            continue
        total_left += current_time - entry
    for entry in waiting_times_right_lane.values():
        if entry == 0:
            continue
        total_right += current_time - entry
    
    cv2.putText(frame, f"L: {total_left:.2f}s",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.putText(frame, f"R: {total_right:.2f}s",
                (int(lane_divider_x) + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # lane divider
    cv2.line(frame, (int(lane_divider_x), 0), (int(lane_divider_x), frame.shape[0]), (255, 255, 255), 2)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
