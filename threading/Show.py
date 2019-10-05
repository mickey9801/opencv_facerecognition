# Show.py
# Worker object for just showing capture frame on desktop
#
# Project: Face Recognition using OpenCV and Raspberry Pi
# Ref: https://github.com/nrsyed/computer-vision/tree/master/multithread
# By: Mickey Chan @ 2019

from threading import Thread
import cv2

class Show:
    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False
    
    
    def start(self):
        print("Shower started")
        Thread(target=self.show, name="show", args=()).start()
        return self
    
    
    def show(self):
        while not self.stopped:
            cv2.imshow("Face Recognizer", self.frame) # Show the video frame
            # Press ESC or 'q' to quit the program
            key = cv2.waitKey(1) & 0xff
            if key == 27 or key == ord('q'):
                self.stop()
        
        cv2.destroyAllWindows()
        return
    
    
    def stop(self):
        print("Shower stopped")
        self.stopped = True