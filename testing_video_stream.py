from camera_reader import CameraFeed
import cv2
import sys
from detection_handling import find_blue, find_squares

def testing_video():
    cf = CameraFeed(f'tcp://192.168.0.102:9000')
    # frame = cf.read()
    
                
    # cv2.imshow('Video Capture',frame)
    # cv2.waitKey(0)

    while True:
        frame = cf.read()
        frame = find_blue(frame)
        cv2.imshow("testing", frame)
        cv2.waitKey(0)
        sys.exit() # to exit from all the processes
 
    cv2.destroyAllWindows() # destroy all windows

testing_video()
