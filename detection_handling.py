#!/usr/bin/env python3

# NAME: detection_handling.py
# PURPOSE: robomodule that detects desired colors and shape from camera feed
# AUTHOR: Vanessa Bellotti

import os
import robomodules as rm
from messages import MsgType, message_buffers
import cv2
from camera_reader import CameraFeed
import numpy as np
from emitter import Emitter
from messages import MsgType, message_buffers, RotationCommand

# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 2

START_POS = -1

e = Emitter()
cf = CameraFeed(0)


class ShapeHandling(rm.ProtoModule):
    # sets up the module (subscriptions, connection to server, etc)
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.TARGET]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)               
            

    # runs every 1 / FREQUENCY seconds
    def tick(self):
        pass
    
    def find_green(self,image):
      # convert to hsv colorspace
      hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
      # lower bound and upper bound for Green color
      lower_bound = np.array([50, 20, 20])   
      upper_bound = np.array([100, 255, 255])
      # find the colors within the boundaries
      mask = cv2.inRange(hsv, lower_bound, upper_bound)

      #define kernel size  
      kernel = np.ones((7,7),np.uint8)
      # Remove unnecessary noise from mask
      mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
      mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

      # Segment only the detected region
      segmented_img = cv2.bitwise_and(image, image, mask=mask)
      # Find contours from the mask
      contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


      output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3)
      return output
      # # Showing the output
      # cv2.imshow("Output", output)

    def find_yellow(self,image):
      # convert to hsv colorspace
      # lower bound and upper bound for Yellow color
      hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
      lower_bound = np.array([20, 80, 80])   
      upper_bound = np.array([30, 255, 255])
      # find the colors within the boundaries
      mask = cv2.inRange(hsv, lower_bound, upper_bound)

      #define kernel size  
      kernel = np.ones((7,7),np.uint8)
      # Remove unnecessary noise from mask
      mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
      mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

      # Segment only the detected region
      segmented_img = cv2.bitwise_and(image, image, mask=mask)
      # Find contours from the mask
      contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


      output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3)
      return output
      # # Showing the output
      # cv2.imshow("Output", output)
    def find_red(self,image):
      # convert to hsv colorspace
      # lower bound and upper bound for Red color
      hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
      lower_bound = np.array([161, 155, 84])   
      upper_bound = np.array([179, 255, 255])
      # find the colors within the boundaries
      mask = cv2.inRange(hsv, lower_bound, upper_bound)

      #define kernel size  
      kernel = np.ones((7,7),np.uint8)
      # Remove unnecessary noise from mask
      mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
      mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

      # Segment only the detected region
      segmented_img = cv2.bitwise_and(image, image, mask=mask)
      # Find contours from the mask
      contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


      output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3)
      return output
      # # Showing the output
      # cv2.imshow("Output", output)
    def find_blue(self,image):
      # convert to hsv colorspace
      # lower bound and upper bound for Blue color
      hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
      lower_bound = np.array([94,80,2])   
      upper_bound = np.array([126, 255, 255])
      # find the colors within the boundaries
      mask = cv2.inRange(hsv, lower_bound, upper_bound)

      #define kernel size  
      kernel = np.ones((7,7),np.uint8)
      # Remove unnecessary noise from mask
      mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
      mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

      # Segment only the detected region
      segmented_img = cv2.bitwise_and(image, image, mask=mask)
      # Find contours from the mask
      contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


      output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3)
      return output
      # # Showing the output
      cv2.imshow("Output", output)
      
    
    def find_triangles(self, image, START_POS):
      print("finding triangles")
      # finding contours (edges of shapes) in image
      edges = cv2.Canny(image, 30, 200)
      contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      #  deciding which contours are triangular and drawing them on the image
      output_image = image.copy()
      triangle_count = 0
      for contour in contours:
        approx = cv2.approxPolyDP(contour, 1.95, True)

        if len(approx) == 3:
          print("triangle found")
          triangle_count += 1
          e.send_pulse()
          #cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)
        if (triangle_count == 0):
          print("no triangles")
          msg = RotationCommand()
          START_POS += .1
          msg.position = START_POS
          msg.max_speed = 1
          self.write(msg.SerializeToString(), MsgType.ROTATION_COMMAND)

      return output_image, triangle_count
    def find_squares(self, image, START_POS):
      print("FIND SQUARES WAS CALLED")
      # finding contours (edges of shapes) in image
      edges = cv2.Canny(image, 30, 200)
      contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      #  deciding which contours are triangular and drawing them on the image
      output_image = image.copy()
      square_count = 0
      for contour in contours:
        approx = cv2.approxPolyDP(contour, 1.95, True)

        if len(approx) == 4:
          square_count += 1
          print("square found")
          e.send_pulse()
          #cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)
        if (square_count == 0):
          print("no squares")
          msg = RotationCommand()
          START_POS += .1
          msg.position = START_POS
          msg.max_speed = 1
          self.write(msg.SerializeToString(), MsgType.ROTATION_COMMAND)
          print ("square not found")
        # print("DEBUGGING SQUARE_COUNT", square_count)

      return output_image, square_count
  
    def find_octagons(self, image, START_POS):
      print("finding octagons")
      # finding contours (edges of shapes) in image
      edges = cv2.Canny(image, 30, 200)
      contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      #  deciding which contours are triangular and drawing them on the image
      output_image = image.copy()
      octagons_count = 0
      for contour in contours:
        approx = cv2.approxPolyDP(contour, 1.95, True)

        if len(approx) == 8:
          print("found octagon")
          octagons_count += 1
          e.send_pulse()
          #cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)
        if (octagons_count == 0):
          print("no octagon found")
          msg = RotationCommand()
          START_POS += .1
          msg.position = START_POS
          msg.max_speed = 1
          self.write(msg.SerializeToString(), MsgType.ROTATION_COMMAND)

      return output_image, octagons_count
  
    def find_circles(self, image, START_POS):
      # finding contours (edges of shapes) in image
      print("looking for circles")
      edges = cv2.Canny(image, 30, 200)
      contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      #  deciding which contours are triangular and drawing them on the image
      output_image = image.copy()
      circle_count = 0
      for contour in contours:
        approx = cv2.approxPolyDP(contour, 1.95, True)

        if len(approx) > 8: #might want to increase to fix the threshold
          print("circle found")
          circle_count += 1
          # cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)
          e.send_pulse(0)
        
        if (circle_count == 0):
          print("no circle found")
          msg = RotationCommand()
          START_POS += .1
          msg.position = START_POS
          msg.max_speed = 1
          self.write(msg.SerializeToString(), MsgType.ROTATION_COMMAND)

      return output_image, circle_count

# runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        msg2 = RotationCommand()
        msg2.position = START_POS
        msg2.max_speed = 1
        self.write(msg2.SerializeToString(), MsgType.ROTATION_COMMAND)

        
        if (msg_type == MsgType.TARGET):
          # print ("target message was found")
          # control logic for detecting colors
          if (msg.color== 0):
            cf2 = self.find_red(cf.read())
          elif (msg.color == 1):
            cf2 = self.find_yellow(cf.read())
          elif (msg.color == 2):
            cf2 = self.find_blue(cf.read())
          elif(msg.color == 3):
            # print ("green was found")
            cf2 = self.find_green(cf.read())
          
          # color detection on the new masked camera feed frame read
          if (msg.shape == 0):
            print("looking for squares")
            self.find_squares(cf2, START_POS)
          elif (msg.shape == 1):
            self.find_circles(cf2, START_POS)
          elif (msg.shape == 2):
            self.find_triangles(cf2, START_POS)
          elif (msg.shape == 3):
            self.find_octagons(cf2, START_POS)


def main():
    module = ShapeHandling(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()

