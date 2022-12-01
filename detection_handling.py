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

# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 2


class ShapeHandling(rm.ProtoModule):
    # sets up the module (subscriptions, connection to server, etc)
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.TARGET]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)               
            

    # runs every 1 / FREQUENCY seconds
    def tick(self):
        pass
    
    def find_green(image):
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

    def find_yellow(image):
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
    def find_red(image):
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
    def find_blue(image):
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
      # cv2.imshow("Output", output)
      
    
    def find_triangles(image):
      # finding contours (edges of shapes) in image
      e = Emitter()
      edges = cv2.Canny(image, 30, 200)
      contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      #  deciding which contours are triangular and drawing them on the image
      output_image = image.copy()
      triangle_count = 0
      for contour in contours:
        approx = cv2.approxPolyDP(contour, 1.95, True)

        if len(approx) == 3:
          triangle_count += 1
          e.send_pulse()
          #cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

      return output_image, triangle_count
    def find_squares(image):
      # finding contours (edges of shapes) in image
      e = Emitter()
      edges = cv2.Canny(image, 30, 200)
      contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      #  deciding which contours are triangular and drawing them on the image
      output_image = image.copy()
      square_count = 0
      for contour in contours:
        approx = cv2.approxPolyDP(contour, 1.95, True)

        if len(approx) == 4:
          square_count += 1
          e.send_pulse()
          #cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

      return output_image, square_count
  
    def find_octagons(image):
      e = Emitter()
      # finding contours (edges of shapes) in image
      edges = cv2.Canny(image, 30, 200)
      contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      #  deciding which contours are triangular and drawing them on the image
      output_image = image.copy()
      octagons_count = 0
      for contour in contours:
        approx = cv2.approxPolyDP(contour, 1.95, True)

        if len(approx) == 8:
          triangle_count += 1
          e.send_pulse()
          #cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

      return output_image, octagons_count
  
    def find_circles(image):
      e = Emitter()
      # finding contours (edges of shapes) in image
      edges = cv2.Canny(image, 30, 200)
      contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      #  deciding which contours are triangular and drawing them on the image
      output_image = image.copy()
      circle_count = 0
      for contour in contours:
        approx = cv2.approxPolyDP(contour, 1.95, True)

        if len(approx) > 8: #might want to increase to fix the threshold
          circle_count += 1
          # cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)
          e.send_pulse(0)

      return output_image, circle_count

# runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        cf = CameraFeed(0)
        
        if (msg_type == MsgType):
          # control logic for detecting colors
          if (msg.Color== 0):
            cf2 = self.find_red(cf.read())
          elif (msg.Color == 1):
            cf2 = self.find_yellow(cf.read())
          elif (msg.Color == 2):
            cf2 = self.find_blue(cf.read())
          elif(msg.Color == 3):
            cf2 = self.find_green(cf.read())
          
          # color detection on the new masked camera feed frame read
          if (msg.Shape == 0):
              self.find_squares(cf2)
          elif (msg.Shape == 1):
              self.find_circles(cf2)
          elif (msg.Shape == 2):
              self.find_triangles(cf2)
          elif (msg.Shape == 3):
              self.find_octagons(cf2)
               
        

def main():
    module = ShapeHandling(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()

