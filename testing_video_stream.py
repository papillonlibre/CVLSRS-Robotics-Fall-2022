from camera_reader import CameraFeed
import cv2
import sys
import os
from detection_handling import ShapeHandling
def testing_video():
    #cf = CameraFeed(f'tcp://192.168.0.102:9000')
    cf = CameraFeed(0)
    # frame = cf.read() # for testing
    ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
    PORT = os.environ.get("LOCAL_PORT", 11295)
    module = ShapeHandling(ADDRESS, PORT)
    
    # cv2.imshow('Video Capture',frame)
    # cv2.waitKey(0)

    while True:
        frame = cf.read()
        # cv2.imshow("testing", frame)
        frame2 = ShapeHandling.find_squares(frame)
        cv2.imshow("testing", frame2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # sys.exit() # to exit from all the processes
 
    cv2.destroyAllWindows() # destroy all windows

testing_video()