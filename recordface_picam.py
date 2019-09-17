# Ref: https://www.pytorials.com/face-recognition-using-opencv-part-2/

# Import required modules
import cv2
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
import sqlite3
import time

# Connect SQLite3 database
conn = sqlite3.connect("database.db")
db = conn.cursor()

# Prepare a directory for storing captured face data
dirName = "./dataset"
if not os.path.exists(dirName):
    os.makedirs(dirName)
    print("DataSet Directory Created")

name = input("What's his/her Name?")

saveFace = False
frameColor = (0,0,255)
userDir = "User_"
beginTime = 0

# Connect to video source
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))

# Setup Classifier for detect face
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

count = 1
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = frame.array;
    cv2.putText(frame, "Press 'f' to start face capture", (10, 480-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors = 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), frameColor, 2)
        if saveFace:
            roiGray = gray[y:y+h, x:x+w]
            fileName = userDir + "/" + f'{count:02}' + ".jpg"
            cv2.imwrite(fileName, roiGray)
            #print(fileName)
            cv2.imshow("face", roiGray)
            count += 1
        
    cv2.imshow('frame', frame)
    rawCapture.truncate(0)
    
    # Press 'f' to begin detect,
    # Press ESC or 'q' to quit
    key = cv2.waitKey(1) & 0xff
    if key == 27 or key == ord('q'):
        break
    elif key == ord('f') and not saveFace:
        saveFace = True
        frameColor = (0, 255, 0)
        beginTime = time.time()
        # Build directory for storing captured faces
        userDir = os.path.join(dirName, userDir + time.strftime("%Y%m%d%H%M%S"))
        if not os.path.exists(userDir):
            os.makedirs(userDir)
        #print("Maked directory: " + userDir)
    
    # Quit face detection when captured 30 images
    if count > 30:
        break

# Clean up
camera.close()

# Insert a new record
db.execute("INSERT INTO `users` (`name`) VALUES(?)", (name,))
uid = db.lastrowid
print("User ID:" + str(uid))
# Rename temperary directory with UID
newUserDir = os.path.join(dirName, str(uid))
os.rename(userDir, newUserDir);
#print("Renamed user dataset directory name to " + newUserDir)
conn.commit()
conn.close()

cv2.destroyAllWindows()
print("DONE")
elapsedTime = round(time.time() - beginTime, 4)
print("Elapsed time: " + str(elapsedTime) + "s")