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
from messages import MsgType, message_buffers, RotationCommand, TiltCommand

# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 2

START_POS = -1

e = Emitter()
cf = CameraFeed(0)
msg3 = TiltCommand()


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
      lower_bound = np.array([41, 130, 0])   
      upper_bound = np.array([67, 255, 255])
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
      cv2.imshow("Output", output)
      #cv2.waitKey(0)
      return output
      # # Showing the output

    def find_yellow(self,image):
      # convert to hsv colorspace
      # lower bound and upper bound for Yellow color
      hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
      lower_bound = np.array([86, 132, 0])   
      upper_bound = np.array([98, 255, 255])
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
      # cv2.imshow("Output", output)
      # cv2.waitKey(0)
      return output
      # # Showing the output
    def find_red(self,image):
      # convert to hsv colorspace
      # lower bound and upper bound for Red color
      hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
      lower_bound = np.array([110, 155, 0])   
      upper_bound = np.array([128, 255, 255])
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
      # Showing the output for testing
      # cv2.imshow("Output", output)
      # cv2.waitKey(0)
    def find_blue(self,image):
      # convert to hsv colorspace
      # lower bound and upper bound for Blue color
      hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
      lower_bound = np.array([0,153,2])   
      upper_bound = np.array([23, 255, 255])
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


      output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3) # outlines target in shape
      return output
      # Showing the output for testing
      # cv2.imshow("Output", output)
      # cv2.waitKey(0)
      
    
    def find_triangles(self, image, START_POS, msg3):
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
          cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3) # outlines target in shape
        if (triangle_count == 0 and msg3.position == 1): # when target not detected && tilt not finished
          print("no triangles")
          msg = RotationCommand()
          START_POS += .1
          msg.position = START_POS
          msg.max_speed = 1
          self.write(msg.SerializeToString(), MsgType.ROTATION_COMMAND)
          msg3.position = -1 # reset tilt value
          self.write(msg3.SerializeToString(), MsgType.TILT_COMMAND)
      # Showing the output for testing
      # cv2.imshow("Output", output)
      # cv2.waitKey(0)
      return output_image, triangle_count
    def find_squares(self, image, START_POS, msg3):
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
          cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3) # outlines target in shape
        if (square_count == 0 and msg3.position == 1): # when target not detected && tilt not finished
          print("no squares")
          msg = RotationCommand()
          START_POS += .1
          msg.position = START_POS
          msg.max_speed = 1
          self.write(msg.SerializeToString(), MsgType.ROTATION_COMMAND)
          msg3.position = -1 # reset tilt value
          self.write(msg3.SerializeToString(), MsgType.TILT_COMMAND)
          print ("square not found")
        # print("DEBUGGING SQUARE_COUNT", square_count)
      # Showing the output for testing
      # cv2.imshow("Output", output)
      # cv2.waitKey(0)
      return output_image, square_count
  
    def find_octagons(self, image, START_POS, msg3):
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
          cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3) # outlines target in shape
        if (octagons_count == 0 and msg3.position == 1): # when target not detected && tilt not finished
          print("no octagon found")
          msg = RotationCommand()
          START_POS += .1
          msg.position = START_POS
          msg.max_speed = 1
          self.write(msg.SerializeToString(), MsgType.ROTATION_COMMAND)
          msg3.position = -1 # reset tilt value
          self.write(msg3.SerializeToString(), MsgType.TILT_COMMAND)
      # Showing the output for testing
      # cv2.imshow("Output", output)
      # cv2.waitKey(0)
      return output_image, octagons_count
  
    def find_circles(self, image, START_POS, msg3):
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
          cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3) # outlines target in shape
          e.send_pulse(0)
        
        if (circle_count == 0 and msg3.position == 1): # when target not detected && tilt not finished
          print("no circle found")
          msg_motor = RotationCommand()
          START_POS += .1
          msg_motor.position = START_POS
          msg_motor.max_speed = 1
          self.write(msg_motor.SerializeToString(), MsgType.ROTATION_COMMAND)
          msg3.position = -1 # reset tilt value
          self.write(msg3.SerializeToString(), MsgType.TILT_COMMAND)
      # cv2.imshow("Output", output_image)
      # cv2.waitKey(0)
      return output_image, circle_count

# runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        msg2 = RotationCommand()
        msg2.position = START_POS
        msg2.max_speed = 1
        self.write(msg2.SerializeToString(), MsgType.ROTATION_COMMAND)

        msg3.position = START_POS
        self.write(msg3.SerializeToString(), MsgType.ROTATION_COMMAND)

        
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
          

          while (msg3.position != 1): # need to tilt to achieve full view
            # color detection on the new masked camera feed frame read
            if (msg.shape == 0):
              print("looking for squares")
              output,count = self.find_squares(cf2, START_POS, msg3)
            elif (msg.shape == 1):
              output,count =self.find_circles(cf2, START_POS, msg3)
            elif (msg.shape == 2):
              output,count =self.find_triangles(cf2, START_POS, msg3)
            elif (msg.shape == 3):
              output,count = self.find_octagons(cf2, START_POS, msg3)
            while True:
              cv2.imshow("testing", output)
              if cv2.waitKey(1) & 0xFF == ord('q'):
                  break
              # sys.exit() # to exit from all the processes
            msg3.position += .1
            self.write(msg3.SerializeToString(), MsgType.ROTATION_COMMAND)
 
          cv2.destroyAllWindows() # destroy all windows


def main():
    module = ShapeHandling(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()

