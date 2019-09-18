# Ref: https://www.pytorials.com/face-recognition-using-opencv-part-2/

# Import required modules
import cv2
import os
import time
import sqlite3

# Connect SQLite3 database
conn = sqlite3.connect("database.db")
db = conn.cursor()

# Prepare a directory for storing captured face data
dirName = "./dataset"
if not os.path.exists(dirName):
    os.makedirs(dirName)
    print("DataSet Directory Created")

name = input("What's his/her Name?")

imgCapture = 30
saveFace = False
frameColor = (0,0,255)
userDir = "User_"
beginTime = 0

# Connect to video source
#vSource = "rtsp://192.168.1.100:8554/live.sdp" # RTSP URL of IP Cam
vSource = 0 # first USB webcam
vStream = cv2.VideoCapture(vSource)

# Setup Classifier for detect face
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

count = 1
frameRate = 5
prevTime = 0
while vStream.isOpened():
    timeElapsed = time.time() - prevTime
    ok, frame = vStream.read()
    if not ok: break
    cv2.putText(frame, "Press 'f' to start face capture", (10, 480-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    
    if timeElapsed > 1./frameRate:
        prevTime = time.time()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.1, minNeighbors = 2)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), frameColor, 2)
            if saveFace:
                roiGray = gray[y:y+h, x:x+w]
                fileName = userDir + "/" + f'{count:02}' + ".jpg"
                cv2.imwrite(fileName, roiGray)
                cv2.imshow("face", roiGray)
                count += 1
        
    cv2.imshow('frame', frame)
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
    
    # Quit face detection when captured 30 images
    if count > imgCapture:
        break

# Clean up
vStream.release()

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