#!/usr/bin/env python3

import cv2
import numpy as np

# Replace the following line with the address of your local camera (typically 0 for the default camera)
LOCAL_CAMERA_INDEX = 0

START_POS = -1

# Create a VideoCapture object for the local camera
cap = cv2.VideoCapture(LOCAL_CAMERA_INDEX)


class ShapeHandling:
    def __init__(self):
        self.frequency = 2


    def find_shapes(self, image, shape_name, START_POS, msg3, target_count, msg_type):
            edges = cv2.Canny(image, 30, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            output_image = image.copy()
            count = 0

            for contour in contours:
                approx = cv2.approxPolyDP(contour, 1.95, True)

                if len(approx) == target_count or (shape_name == "circle" and len(approx) > target_count and len(approx) < target_count + 10):
                    count += 1
                    seconds = 3
                    cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

            return output_image, count

    def find_triangles(self, image, START_POS, msg3):
        print("Finding triangles")
        return self.find_shapes(image, "Triangles", START_POS, msg3, 3)

    def find_squares(self, image, START_POS, msg3):
        print("Finding squares")
        return self.find_shapes(image, "Squares", START_POS, msg3, 4,)

    def find_octagons(self, image, START_POS, msg3):
        print("Finding octagons")
        return self.find_shapes(image, "Octagons", START_POS, msg3, 8)

    def find_circles(self, image, START_POS):
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply GaussianBlur to reduce noise and improve circle detection
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        # Use Hough Circle Transform to detect circles
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=50,
            param2=30,
            minRadius=70,
            maxRadius=90,
        )

        output_image = image.copy()
        circle_count = 0

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                circle_count += 1
                # Draw the outer circle
                cv2.circle(output_image, (i[0], i[1]), i[2], (255, 0, 0), 3)

        if circle_count == 0:
            print("No circles found")

        return output_image, circle_count


def main():
    shape_handler = ShapeHandling()
    shape_ranges = {
        "square": 4,
        "triangle": 3,
        "octagon": 8,
        "circle": 50
    }
    cap = cv2.VideoCapture(0)

    while True:
        # Capture a frame from the local camera
        ret, frame = cap.read()

        # Apply shape detection for each shape range
        for shape, sides in shape_ranges.items():
            if shape == "circle":
                output, _ = shape_handler.find_circles(frame, START_POS)
                cv2.imshow(f"{shape.capitalize()} Detection", output)
            else:
                output, _ = shape_handler.find_shapes(frame, shape, START_POS, "msg3", sides, "msg_type")
                cv2.imshow(f"{shape.capitalize()} Detection", output)
        # Display the frame
        cv2.imshow('Camera Feed', frame)

        # Check for the 'q' key to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the VideoCapture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()