# Detector.py
# Worker object for doing face recognition
#
# Project: Face Recognition using OpenCV and Raspberry Pi
# Ref: https://github.com/nrsyed/computer-vision/tree/master/multithread
# By: Mickey Chan @ 2019

from threading import Thread
import cv2
import sqlite3
import RPi.GPIO as GPIO
import time

class Detector:
    def __init__(self, dBase, cascade, trainingData=None, frame=None, lockPin=0):
        self.frame = frame
        self.lockPin = lockPin
        self.lastUnlockedAt = 0
        self.unlockDuration = 5 # n second
        self.dBase = dBase
        self.faceCascade = cv2.CascadeClassifier(cascade)
        self.trainingData = trainingData
        self.stopped = False
    
    
    def start(self):
        print("Detector started")
        Thread(target=self.detect, name="detector", args=()).start()
        return self
    
    
    def detect(self):
        self.conn = sqlite3.connect(self.dBase)
        self.db = self.conn.cursor()
        self.recognizer = cv2.face.createLBPHFaceRecognizer() # or LBPHFaceRecognizer_create()
        self.recognizer.load(self.trainingData) # read() for LBPHFaceRecognizer_create()
        while not self.stopped:
            if time.time() - self.lastUnlockedAt > self.unlockDuration:
                GPIO.output(self.lockPin, 0)
            
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY) # Convert captured frame to grayscale
            faces = self.faceCascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 5) # Detect face(s) inside the frame
            for (x, y, w, h) in faces:
                # Try to recognize the face using recognizer
                roiGray = gray[y:y+h, x:x+w]
                id_, conf = self.recognizer.predict(roiGray)
                
                # If recognized face has enough confident (<= 70),
                # retrieve the user name from database,
                # draw a rectangle around the face,
                # print the name of the user and
                # unlock the door for 5 secords
                if conf <= 70:
                    self.db.execute("SELECT `name` FROM `users` WHERE `id` = (?);", (id_,))
                    result = self.db.fetchall()
                    name = result[0][0]
                    print("[Unlock] " + str(id_) + ":" + name + " (" + str(conf) + ")")
                    cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(self.frame, name, (x+2,y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150,255,0), 2)
                    
                    # You may do anything below for detected user, e.g. unlock the door
                    if self.lockPin > 0:
                        GPIO.output(self.lockPin, 1)
                        self.lastUnlockedAt = time.time()
                else:
                    print("[No Match] " + str(id_) + " (" + str(conf) + ")")
                    cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    if self.lockPin > 0: GPIO.output(self.lockPin, 0)
            
            cv2.imshow("Face Recognizer", self.frame)
            # Press ESC or 'q' to quit the program
            key = cv2.waitKey(1) & 0xff
            if key == 27 or key == ord('q'):
                self.stop()
        
        self.conn.close()
        cv2.destroyAllWindows()
        return
    
    
    def stop(self):
        print("Detector stopped")
        self.stopped = True