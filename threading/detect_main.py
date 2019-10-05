# detect_main.py
# Finding the person in front of the camera is anyone who stored in database
# Using USB webcam or IP Cam (multi-threading)
#
# Project: Face Recognition using OpenCV and Raspberry Pi
# Ref: https://github.com/nrsyed/computer-vision/tree/master/multithread
# By: Mickey Chan @ 2019

import os
import RPi.GPIO as GPIO
from Capturer import Capturer # Worker object for capturing video frame
from Detector import Detector # Worker object for doing face recognition
#from Show import Show # Worker object for just showing capture frame on desktop

# Connect to video source
#vSource = "rtsp://192.168.1.100:8554/live.sdp" # RTSP URL of IP Cam
vSource = 0 # first USB webcam

cname = "../haarcascade_frontalface_default.xml"
dname = "../database.db" # Database file
fname = "../recognizer/trainingData.yml" # Training data file

relayPin = 26

def main():
    if not os.path.isfile(fname):
        print("Please train the data first")
        exit(0)
    videoGetter = Capturer(vSource).start()
    faceDetector = Detector(dname, cname, fname, videoGetter.frame, relayPin).start()
    #videoShower = Show(videoGetter.frame).start()
    
    # Setup GPIO for door lock
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relayPin, GPIO.OUT)
    GPIO.output(relayPin, 0)
    
    while True:
        # Stop the thread when its other worker stopped
        if videoGetter.stopped or faceDetector.stopped: #videoShower.stopped:
            if not videoGetter.stopped: videoGetter.stop()
            if not faceDetector.stopped: faceDetector.stop()
            #if not videoShower.stopped: videoShower.stop()
            break
        
        frame = videoGetter.frame # Capture a video frame
        faceDetector.frame = frame # Submit the video frame to detector for process
        #videoShower.frame = frame
    
    GPIO.cleanup()
    print("END")


if __name__ == "__main__":
    main()
    exit(0)