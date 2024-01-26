import cv2
import numpy as np
import time

# Dictionary to store information about each tracked dot
tracked_dots = {}
waiting_times_left_lane = {}
waiting_times_right_lane = {}

# Function to calculate time spent in the frame for each dot
def calculate_time_in_frame(dot_id):
    if dot_id in tracked_dots:
        current_time = time.time()
        last_movement_time = tracked_dots[dot_id].get("last_movement_time", current_time)
        time_in_frame = current_time - last_movement_time
        return time_in_frame
    else:
        return 0

# Initialize video capture
cap = cv2.VideoCapture(0)

# Define a movement threshold (adjust as needed)
MOVEMENT_THRESHOLD = 5  # pixels

while True:
    ret, frame = cap.read()

    # Apply color-based masking to isolate the stickers
    lower_white = np.array([200, 200, 200])
    upper_white = np.array([255, 255, 255])
    mask = cv2.inRange(frame, lower_white, upper_white)

    # Bitwise-AND to keep only the white stickers
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

    # Convert the masked frame to grayscale
    gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)

    # Apply blob detection to find individual dots
    params = cv2.SimpleBlobDetector_Params()
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(gray)

    # List to store dot IDs that are currently in the frame
    current_dots_in_frame = []

    for keypoint in keypoints:
        x, y = map(int, keypoint.pt)

        # Assume the center of the frame as the divider between left and right lanes
        divider_x = frame.shape[1] // 2

        # Determine the lane based on x-coordinate
        if x < divider_x:
            lane_id = "left_lane"
        else:
            lane_id = "right_lane"

        dot_id = f"{x}_{y}_{lane_id}"
        current_dots_in_frame.append(dot_id)

        # Check if the dot is already being tracked
        if dot_id not in tracked_dots:
            # Store information about the tracked dot when it's first detected
            tracked_dots[dot_id] = {
                "first_detection_time": time.time(),
                "coordinates": (x, y),
                "last_coordinates": (x, y),  # To track movement
            }

        # Calculate the distance moved since the last frame
        last_x, last_y = tracked_dots[dot_id]["last_coordinates"]
        distance_moved = np.sqrt((x - last_x)**2 + (y - last_y)**2)

        # Check if the dot has moved more than the threshold
        if distance_moved > MOVEMENT_THRESHOLD:
            tracked_dots[dot_id]["last_coordinates"] = (x, y)
            # Dot is considered in motion, reset waiting time
            tracked_dots[dot_id]["last_movement_time"] = time.time()
        else:
            # Dot is not in motion, increase waiting time
            last_movement_time = tracked_dots[dot_id].get("last_movement_time", time.time())
            time_in_frame = time.time() - last_movement_time
            waiting_times = waiting_times_left_lane if lane_id == "left_lane" else waiting_times_right_lane
            waiting_times[dot_id] = time_in_frame

        # Draw a circle around the detected dot
        cv2.circle(frame, (x, y), int(keypoint.size), (0, 255, 0), 2)

        # Display the dot ID
        cv2.putText(frame, f"Dot ID: {dot_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Calculate and display the time spent in the frame for each dot
        time_in_frame = calculate_time_in_frame(dot_id)
        cv2.putText(frame, f"Time in Frame: {time_in_frame:.2f} seconds", (x, y + int(keypoint.size) + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Remove entries for dots that have left the frame
    for dot_id in list(tracked_dots.keys()):
        if dot_id not in current_dots_in_frame:
            # Dot has left the frame, remove entries
            if dot_id in waiting_times_left_lane:
                del waiting_times_left_lane[dot_id]
            if dot_id in waiting_times_right_lane:
                del waiting_times_right_lane[dot_id]
            del tracked_dots[dot_id]

    # Display
    cv2.imshow('Dot Tracking', frame)

    # Display cumulative waiting times for each lane
    print(f"Left Lane Waiting Time: {sum(waiting_times_left_lane.values()):.2f} seconds")
    print(f"Right Lane Waiting Time: {sum(waiting_times_right_lane.values()):.2f} seconds")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()
