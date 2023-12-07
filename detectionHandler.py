#!/usr/bin/env python3

import os
import cv2
import numpy as np
import robomodules as rm
from messages import MsgType, message_buffers, RotationCommand, TiltCommand, LaserCommand
# from local_camera_reader import LocalCameraFeed
from remote_camera_reader import RemoteCameraFeed


# Retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS", "localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)
FREQUENCY = 2

TESTING = True

class ShapeHandling(rm.ProtoModule):
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.TARGET]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)
        self.cf = RemoteCameraFeed(0)
        self.msg2 = RotationCommand()
        self.msg3 = TiltCommand()

        self.targetSearching = False
        self.rotation = 0
        self.tilt = 0
        self.up = True
        self.color = -1
        self.shape = -1

    def tick(self):
        return self.move()

        if not self.targetSearching:
            return

        # control logic for detecting colors
        if self.color == 0: # Red
            cf2 = self.find_color(self.cf.read(), np.array([0, 100, 100]), np.array([15, 255, 255]))
        elif self.color == 1: # Yellow
            cf2 = self.find_color(self.cf.read(), np.array([20, 100, 100]), np.array([30, 175, 255]))
        elif self.color == 2: # Blue
            cf2 = self.find_color(self.cf.read(), np.array([100, 200, 100]), np.array([110, 255, 255]))
        elif self.color == 3: # Green
            cf2 = self.find_color(self.cf.read(), np.array([70, 100, 100]), np.array([85, 175, 255]))
        else: # Not a valid color
            return

        if self.shape == 0: # Square
            output, _ = self.find_squares(cf2)
        elif self.shape == 1: # Circle
            output, _ = self.find_circles(cf2)
        elif self.shape == 2: # Triangle
            output, _ = self.find_triangles(cf2)
        elif self.shape == 3: # Octagon
            output, _ = self.find_octagons(cf2)
        else: # Not a valid shape
            return
        
        if TESTING:
            cv2.imshow("Testing", output)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        
        # if TESTING:
        #     cv2.destroyAllWindows()
        return self.move()

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

    def find_shapes(self, image, shape_name, target_count):
        edges = cv2.Canny(image, 30, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        output_image = image.copy()
        count = 0

        for contour in contours:
            approx = cv2.approxPolyDP(contour, 1.95, True)

            if len(approx) == target_count:
                count += 1
                seconds = 5
                msg = LaserCommand(seconds) 
                self.targetSearching = False
                self.write(msg.SerializeToString(), MsgType.LASER_COMMAND)
                cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

        return output_image, count

    def find_triangles(self, image):
        print("Finding triangles")
        return self.find_shapes(image, "Triangles", 3)

    def find_squares(self, image):
        print("Finding squares")
        return self.find_shapes(image, "Squares", 4)

    def find_octagons(self, image):
        print("Finding octagons")
        return self.find_shapes(image, "Octagons", 8)

    def find_circles(self, image):
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
                count += 1
                seconds = 5
                msg = LaserCommand(seconds)
                self.targetSearching = False
                self.write(msg.SerializeToString(), MsgType.LASER_COMMAND)
                # Draw the outer circle
                cv2.circle(output_image, (i[0], i[1]), i[2], (255, 0, 0), 3)

        return output_image, circle_count
    
    def move(self):
        if self.targetSearching:
            if self.up:
                self.tilt += 1
            else:
                self.tilt -= 1
            
            if self.tilt > 1 or self.tilt < -1:
                self.rotation += 15
                # self.rotation += 45
                self.up = not self.up
                if self.tilt > 1:
                    self.tilt = 1
                else:
                    self.tilt = -1
                self.msg2.position = self.rotation
                self.write(self.msg2.SerializeToString(), MsgType.ROTATION_COMMAND)

            self.msg3.position = self.tilt
            self.write(self.msg3.SerializeToString(), MsgType.TILT_COMMAND)
        return


    def msg_received(self, msg, msg_type):
        if (msg_type == MsgType.TARGET):
            self.color = msg.color
            self.shape = msg.shape
            self.targetSearching = True


def main():
    module = ShapeHandling(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()
