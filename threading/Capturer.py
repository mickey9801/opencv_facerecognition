# Capture.py
# Worker object for capturing video frame
#
# Project: Face Recognition using OpenCV and Raspberry Pi
# Ref: https://github.com/nrsyed/computer-vision/tree/master/multithread
# By: Mickey Chan @ 2019

from threading import Thread
import cv2

class Capturer:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
    
    
    def start(self):
        print("Capturer started")
        Thread(target=self.get, name="capturer", args=()).start()
        return self
    
    
    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read() # Capture a video frame
        
        self.stream.release()
        return
    
        
    def stop(self):
        print("Capturer stopped")
        self.stopped = True