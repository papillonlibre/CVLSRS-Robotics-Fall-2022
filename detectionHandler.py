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

# Behavior Parameters
TESTING = False
ONLYCOLOR = True

# Speed/Adjustement Parameters ===============================================
FREQUENCY = 5       # Tick rate (I like to think ticks per second)
XADJUST = 15        # Adjustment denominator when found shape/color
YADJUST = 480*2     # Higher adjustment means its moves less per pixel away
ROTATE = 30         # Rotate per tick
TILTMIN = -1        # Min tilt of the camera
TILTMAX = .5        # Max tilt of the 

# ROTATE = 15         # Rotate per tick

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
            cf2 = self.find_color(self.cf.read(), np.array([170, 100, 100]), np.array([180, 255, 255]))
            # cf2 = self.find_color(self.cf.read(), np.array([0, 100, 100]), np.array([15, 255, 255]))
        elif self.color == 1: # Yellow
            cf2 = self.find_color(self.cf.read(), np.array([20, 100, 100]), np.array([30, 255, 255]))
        elif self.color == 2: # Blue
            cf2 = self.find_color(self.cf.read(), np.array([100, 200, 100]), np.array([110, 255, 255]))
        elif self.color == 3: # Green
            cf2 = self.find_color(self.cf.read(), np.array([70, 100, 100]), np.array([85, 175, 255]))
        else: # Not a valid color
            print("Not given a valid color. Waiting for signal...")
            return
        
        if ONLYCOLOR:
            # pass
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
        
        self.move()
        if TESTING:
            color = ["Red", "Yellow", "Blue", "Green"]
            shape = ["Square", "Circle", "Triangle", "Octagon"]
            if ONLYCOLOR:
                print(f'Searching for: {color[self.color]}')
            else:
                print(f'Searching for: {color[self.color]} {shape[self.shape]}')
        return


    def find_color(self, image, lower_bound, upper_bound):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # print(hsv[240][320])
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
        return self.check_contour(contours, -1)

    def find_shapes(self, image, target_count):
        edges = cv2.Canny(image, 30, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.lastSeen += 1
        return self.check_contour(contours, target_count)
    
    
    def check_contour(self, contours, target_count):
        cXs = []
        cYs = []

        for contour in contours:
            if cv2.contourArea(contour) < 1000:
                continue
            
            M = cv2.moments(contour)
            if (M["m00"] == 0):
                continue
            cX = int(M["m10"]/ M["m00"])
            cY = int(M["m01"]/ M["m00"])

            if (target_count != -1):
                approx = cv2.approxPolyDP(contour, 1.95, True)
                if len(approx) == target_count:
                    cXs.append(cX)
                    cYs.append(cY)
            else:
                cXs.append(cX)
                cYs.append(cY)

            self.targetSearching = len(cXs) == 0
            if not self.targetSearching:
                self.found_move(cXs, cYs)
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

        self.lastSeen += 1
        output_image = image.copy()
        if circles is not None:
            circles = np.uint16(np.around(circles))
            # Convert circles to contours
            contours = [np.array([[[i[0], i[1]]]], dtype=np.int32) for circle in circles]
            self.check_contour(contours, -1)
        return 
    

    def move(self):
        if self.targetSearching and self.lastSeen > 3:
            print("Moved | ")
            if self.up:
                self.tilt += .5
            else:
                self.tilt -= .5   
            
            if (self.tilt > TILTMAX and self.up) or (self.tilt < TILTMIN and not self.up):
                self.up = not self.up
                if self.tilt > TILTMAX:
                    self.tilt = TILTMAX
                else:
                    self.tilt = TILTMIN
                self.msg2.position = ROTATE
                self.write(self.msg2.SerializeToString(), MsgType.ROTATION_COMMAND)

            self.msg3.position = self.tilt
            self.write(self.msg3.SerializeToString(), MsgType.TILT_COMMAND)
        return
    
    def found_move(self, cXs, cYs):
        self.lastSeen = 0
        cX_av = sum(cXs) / len(cXs) 
        cY_av = sum(cYs) / len(cYs)
        # print(f"{cX_av}, {cY_av} ", end = "")
        # print(f"{cXs}, {cYs} | ", end = "")
        # print(f"; {len(cXs)} ; ", end = "")

        if not (260 < cY_av < 300):
            self.tilt += (cY_av - 280) / YADJUST
        
        if not (300 < cX_av < 340):
            rotation = (cX_av - 320) / XADJUST
        else:
            rotation = 0
        
        if ((260 < cY_av < 300) and (300 < cX_av < 340)):
            print("LASER!")
            msg = LaserCommand()
            msg.seconds = 1 / FREQUENCY
            self.write(msg.SerializeToString(), MsgType.LASER_COMMAND)

        if self.tilt > 1:
            self.tilt = 1
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
