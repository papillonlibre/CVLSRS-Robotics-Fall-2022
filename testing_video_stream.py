#!/usr/bin python3

# NAME: testing_video_stream.py
# PURPOSE: reading the most recent frame from a remote camera 
#          stream on your local computer

import os, cv2, threading, queue

ADDRESS = os.environ.get("STREAM_ADDRESS","192.168.0.89")
PORT = os.environ.get("STREAM_PORT", 9000)


class RemoteCameraFeed:

    # PARAMETERS: source - URI of the remote stream
    #                      (e.g. tcp://192.168.0.89:9000)
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # PURPOSE: continously reads from camera feed; discards unused frames
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
    # RETURNS: the frame, as a 3D numpy array (such that each pixel is a trio 
    #          of RGB values)
    def read(self):
        return self.q.get()


if __name__ == '__main__':
    feed = RemoteCameraFeed(f'tcp://{ADDRESS}:{PORT}')
    while True:
        frame = feed.read()

        cv2.imshow('Camera Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break