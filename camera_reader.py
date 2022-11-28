#!/usr/bin/env python3

# NAME: remote_camera_reader.py
# PURPOSE: wrapper class for reading the most recent frame from a camera stream
# AUTHOR: this dude on stackoverflow tbh https://stackoverflow.com/a/54755738

import cv2, threading, queue


class CameraFeed:

    # PURPOSE: constructor
    # PARAMETERS: source - source of the video stream. can be either be the URI 
    #                      of a remote stream (e.g. tcp://192.168.0.102:9000), 
    #                      or the integer index of a local camera (likely 0, 
    #                      unless you have multiple cameras hooked up to your 
    #                      computer)
    # RETURNS: N/A
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # PURPOSE: continously reads from camera feed such that unused frames will 
    #          be discarded
    # PARAMETERS: N/A
    # RETURNS: N/A
    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()   # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)

    # PURPOSE: retrieves and parses the most recent frame in the camera stream
    # PARAMETERS: N/A
    # RETURNS: the frame, as a 3D numpy array (such that each pixel is a trio 
    #          of RGB values)
    def read(self):
        return self.q.get()
