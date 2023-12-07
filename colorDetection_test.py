#!/usr/bin/env python3

import cv2
import numpy as np


class ShapeHandling:
    def __init__(self):
        self.frequency = 2

    def find_color(self, image, lower_bound, upper_bound):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        kernel = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        segmented_img = cv2.bitwise_and(image, image, mask=mask)
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3)
        return output

if __name__ == "__main__":
    # Initialize ShapeHandling instance
    shape_handling = ShapeHandling()

    # Define color ranges for each shape (adjust these values based on your requirements)
    color_ranges = {
        "red": (np.array([0, 100, 100]), np.array([15, 255, 255])),
        "yellow": (np.array([20, 100, 100]), np.array([30, 175, 255])),
        "blue": (np.array([100, 200, 100]), np.array([110, 255, 255])),
        "green": (np.array([70, 100, 100]), np.array([85, 175, 255]))
    }

    # Open a connection to the camera (usually 0 for built-in camera)
    cap = cv2.VideoCapture(0)

    while True:
        # Read a frame from the camera
        y , frame = cap.read()

        # Apply color detection for each color range
        for color, (lower_bound, upper_bound) in color_ranges.items():
            output = shape_handling.find_color(frame, lower_bound, upper_bound)
            cv2.imshow(f"{color.capitalize()} Detection", output)
            # cv2.waitKey(1)  # Allow the window to update

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()