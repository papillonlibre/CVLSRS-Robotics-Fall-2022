#!/usr/bin/env python3

# NAME: shape_handling.py
# PURPOSE: empty robomodule (for use as a template)
# AUTHOR: Vanessa Bellotti

import os
import robomodules as rm
from messages import MsgType, message_buffers
import cv2
from camera_reader import CameraFeed

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

    
    def find_triangles(image):
      # finding contours (edges of shapes) in image
      edges = cv2.Canny(image, 30, 200)
      contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

      #  deciding which contours are triangular and drawing them on the image
      output_image = image.copy()
      triangle_count = 0
      for contour in contours:
        approx = cv2.approxPolyDP(contour, 1.95, True)

        if len(approx) == 3:
          triangle_count += 1
          cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

      return output_image, triangle_count
    def find_squares(image):
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
          cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

      return output_image, square_count
  
    def find_octagons(image):
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
          cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

      return output_image, octagons_count
  
    def find_circles(image):
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
          cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)

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
              self.find_squares(cf2.read())
          elif (msg.Shape == 1):
              self.find_circles(cf2.read())
          elif (msg.Shape == 2):
              self.find_triangles(cf2.read())
          elif (msg.Shape == 3):
              self.find_octagons(cf2.read())
               
        

def main():
    module = ShapeHandling(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()

