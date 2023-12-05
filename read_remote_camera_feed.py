# NAME: read_remote_camera_feed.py
# PURPOSE: reading and displaying (using OpenCV) a video feed being streamed
#          over TCP
# AUTHOR: Emma Bethel

import os
import cv2


'''
command to stream camera feed from pi on port 9000:

/usr/bin/gst-launch-1.0 v4l2src ! video/x-h264,width=640,height=480,framerate=30/1 ! h264parse config-interval=1 ! matroskamux streamable=true ! tcpserversink host=::0 port=9000 sync=false sync-method=2
'''


# get IP address and port of video stream from environment variables
ADDRESS = os.environ.get("VIDEO_STREAM_ADDRESS","192.168.0.89")
PORT = os.environ.get("VIDEO_STREAM_PORT", "9000")

# connect to video stream
stream = cv2.VideoCapture(f"tcp://{ADDRESS}:{PORT}")

try:
    while True:
        # get and store the most recent frame from the image
        _, frame = stream.read()

        # display video feed
        cv2.imshow("Video Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
	print("Program stopped")