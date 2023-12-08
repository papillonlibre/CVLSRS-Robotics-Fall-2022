#!/usr/bin/env python3

import os
import cv2
import numpy as np
import robomodules as rm
from messages import MsgType, message_buffers, RotationCommand, TiltCommand, LaserCommand
from local_camera_reader import LocalCameraFeed
# from remote_camera_reader import RemoteCameraFeed


# Retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS", "localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)
FREQUENCY = 5

TESTING = True
ONLYCOLOR = True

class ShapeHandling(rm.ProtoModule):
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.TARGET]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)
        self.cf = LocalCameraFeed()
        self.msg2 = RotationCommand()
        self.msg2.max_speed = 2
        self.msg3 = TiltCommand()

        self.targetSearching = False
        self.tilt = 0
        self.up = True
        self.lastSeen = 0
        self.color = -1
        self.shape = -1

    def tick(self):
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
            print("Not given a valid color. Waiting for signal...")
            return
        
        if ONLYCOLOR:
            self.find_close(cf2)
        else:
            if self.shape == 0: # Square
                self.find_squares(cf2)
            elif self.shape == 1: # Circle
                self.find_circles(cf2)
            elif self.shape == 2: # Triangle
                self.find_triangles(cf2)
            elif self.shape == 3: # Octagon
                self.find_octagons(cf2)
            else: # Not a valid shape
                return
        
        if TESTING:
            color = ["Red", "Yellow", "Blue", "Green"]
            shape = ["Square", "Circle", "Triangle", "Octagon"]
            if ONLYCOLOR:
                print(f'Searching for: {color[self.color]}')
            else:
                print(f'Searching for: {color[self.color]} {shape[self.shape]}')
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


    def find_close(self, image):
        edges = cv2.Canny(image, 30, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.lastSeen += 1
        foundShape = False
        cXs = []
        cYs = []

        for contour in contours:
            if cv2.contourArea(contour) < 20:
                continue
            
            M = cv2.moments(contour)
            if (M["m00"] == 0):
                continue
            cX = int(M["m10"]/ M["m00"])
            cY = int(M["m01"]/ M["m00"])

            cXs.append(cX)
            cYs.append(cY)
            foundShape = True

        self.targetSearching = not foundShape
        if foundShape:
            self.lastSeen = 0
            cX_av = sum(cXs) / len(cXs) 
            cY_av = sum(cYs) / len(cYs) 

            if not (220 < cY_av < 260):
                self.tilt += (240 - cY_av) / 480
            
            if not (300 < cX_av < 340):
                rotation += (cY_av - 320) / 15
            else:
                rotation = 0
            
            if ((220 < cY < 260) and (300 < cX < 340)):
                msg = LaserCommand()
                msg.seconds = 1 / FREQUENCY
                self.write(msg.SerializeToString(), MsgType.LASER_COMMAND)

            self.move_check(rotation)
        return


    def find_shapes(self, image, target_count):
        edges = cv2.Canny(image, 30, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.lastSeen += 1
        foundShape = False
        cXs = []
        cYs = []

        for contour in contours:
            if cv2.contourArea(contour) < 20:
                continue
            
            M = cv2.moments(contour)
            if (M["m00"] == 0):
                continue
            cX = int(M["m10"]/ M["m00"])
            cY = int(M["m01"]/ M["m00"])
            
            approx = cv2.approxPolyDP(contour, 1.95, True)
            if len(approx) == target_count:
                cXs.append(cX)
                cYs.append(cY)
                foundShape = True

        self.targetSearching = not foundShape
        if foundShape:
            self.lastSeen = 0
            cX_av = sum(cXs) / len(cXs) 
            cY_av = sum(cYs) / len(cYs) 

            if not (220 < cY_av < 260):
                self.tilt += (240 - cY_av) / 480
            
            if not (300 < cX_av < 340):
                rotation += (cY_av - 320) / 15
            else:
                rotation = 0
            
            if ((220 < cY < 260) and (300 < cX < 340)):
                msg = LaserCommand()
                msg.seconds = 1 / FREQUENCY
                self.write(msg.SerializeToString(), MsgType.LASER_COMMAND)

            self.move_check(rotation)
        return


    def find_triangles(self, image):
        return self.find_shapes(image, 3)

    def find_squares(self, image):
        return self.find_shapes(image, 4)

    def find_octagons(self, image):
        return self.find_shapes(image, 8)

    def find_circles(self, image):
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply GaussianBlur to reduce noise and improve circle detection
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        # Use Hough Circle Transform to detect circles
        circles = cv2.HoughCircles( blurred, cv2.HOUGH_GRADIENT, dp=1,
            minDist=50, param1=50, param2=30, minRadius=70, maxRadius=90)

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
        if self.targetSearching and self.lastSeen > 1:
            if self.up:
                self.tilt += .5
            else:
                self.tilt -= .5   
            
            if self.tilt > .5 or self.tilt < -1:
                self.up = not self.up
                if self.tilt > .5:
                    self.tilt = .5
                else:
                    self.tilt = -1
                self.msg2.position = 30
                self.write(self.msg2.SerializeToString(), MsgType.ROTATION_COMMAND)

            self.msg3.position = self.tilt
            self.write(self.msg3.SerializeToString(), MsgType.TILT_COMMAND)
        return
    
    def move_check(self, rotation):
        if self.tilt > .5:
            self.tilt = .5
        elif self.tilt < -1:
            self.tilt < -1
        
        self.msg2.position = rotation
        self.write(self.msg2.SerializeToString(), MsgType.ROTATION_COMMAND)

        self.msg3.position = self.tilt
        self.write(self.msg3.SerializeToString(), MsgType.TILT_COMMAND)



    def msg_received(self, msg, msg_type):
        print("Message received!\n")
        if (msg_type == MsgType.TARGET):
            self.color = msg.color
            self.shape = msg.shape
            self.targetSearching = True
            self.lastSeen = 0


def main():
    print("STARTING THE PI\n")
    module = ShapeHandling(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()
