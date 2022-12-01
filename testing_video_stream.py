from camera_reader import CameraFeed
import cv2

def testing_video():
    cf = CameraFeed(f'tcp://192.168.0.102:9000')
    frame = cf.read()
    
                
    cv2.imshow('Video Capture',frame)
    cv2.waitKey(0)

    # while True:
    #     frame = cf.read()
                
    #     cv2.imshow('Video Capture',frame)
    #     if cv2.waitKey(1) & 0xFF ==ord('q'):
    #         break
    # cv2.destroyAllWindows()

testing_video()
