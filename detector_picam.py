# detector_webcam.py
# Finding the person in front of the camera is anyone who stored in database
# Using Pi Camera v2 module (single threading)
#
# Project: Face Recognition using OpenCV and Raspberry Pi
# Ref: https://www.pytorials.com/face-recognition-using-opencv-part-3/
# By: Mickey Chan @ 2019

# Import required modules
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import os
import sqlite3
import RPi.GPIO as GPIO
import time

# Connect SQLite3 database
conn = sqlite3.connect('database.db')
db = conn.cursor()

# Assign the training data file
fname = "recognizer/trainingData.yml"
if not os.path.isfile(fname):
    print("Please train the data first")
    exit(0)

# Setup GPIO for door lock
relayPin = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(relayPin, GPIO.OUT)
GPIO.output(relayPin, 0)

lastUnlockedAt = 0
unlockDuration = 5 # n second

# Font used for display
font = cv2.FONT_HERSHEY_SIMPLEX

# Connect to video source
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))

# Setup Classifier for detecting face
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
# Setup LBPH recognizer for face recognition
recognizer = cv2.face.createLBPHFaceRecognizer() # or LBPHFaceRecognizer_create()
# Load training data
recognizer.load(fname) # change to read() for LBPHFaceRecognizer_create()

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # Lock the door again when timeout
    if time.time() - lastUnlockedAt > unlockDuration:
        GPIO.output(relayPin, 0)
    
    frame = frame.array
    # Detect face
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convert captured frame to grayscale
    faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 5) # Detect face(s) inside the frame
    for (x, y, w, h) in faces:
        # Try to recognize the face using recognizer
        roiGray = gray[y:y+h, x:x+w]
        id_, conf = recognizer.predict(roiGray)
        print(id_, conf)
            
        # If recognized face has enough confident (<= 70),
        # retrieve the user name from database,
        # draw a rectangle around the face,
        # print the name of the user and
        # unlock the door for 5 secords
        if conf <= 70:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # retrieve user name from database
            db.execute("SELECT `name` FROM `users` WHERE `id` = (?);", (id_,))
            result = db.fetchall()
            name = result[0][0]
            
            # You may do anything below for detected user, e.g. unlock the door
            GPIO.output(relayPin, 1) # Unlock
            lastUnlockedAt = time.time()
            print("[Unlock] " + name + " (" + str(conf) + ")")
            cv2.putText(frame, name, (x+2,y+h-5), font, 1, (150,255,0), 2)
        else:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            GPIO.output(relayPin, 0) # Lock the door if not enough confident
            #print("[Lock] " + name + " " + str(conf))
            #cv2.putText(frame, 'No Match', (x+2,y+h-5), font, 1, (0,0,255), 2)
        
    cv2.imshow("Face Recognizer", frame)
    rawCapture.truncate(0) # Clear frame buffer for next frame
    
    # Press ESC or 'q' to quit the program
    key = cv2.waitKey(1) & 0xff
    if key == 27 or key == ord('q'):
        break

# Clean up
camera.close()
conn.close()
cv2.destroyAllWindows()
GPIO.cleanup()
print("END")
