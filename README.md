# Face Recognition using OpenCV and Raspberry Pi

Face recognition sample with opencv-python.

## Prepare Required Files

* opencv-python
   
   OpenCV with Python 3 interface

   ```bash
   sudo apt update
   sudo apt install python3-opencv
   ```
* DB Browser for SQLite
   
   This software is used for browsing user data stored in SQLite database file.
   
   ```bash
   sudo apt update
   sudo apt install sqlitebrowser
   ```

* Classifiers file: haarcascade_frontalface_default.xml
   
   This is a pre-trained cascade classifier file for face detection provided by OpenCV. You may download the file in [OpenCV's GitHub](https://github.com/opencv/opencv/tree/master/data/haarcascades) and store it in the project root (same directory of `setup.py`).

## Usage

Before using any program, please run the `setup.py` script to prepare an empty SQLite database for storing user inforamtion.

```bash
cd opencv_facerecognition
python3 setup.py
```

First we have to collect face images using `recordface_***.py` script.

```bash
python3 recordface_webcam.py # for using webcam
python3 recordface_picam.py # for using PiCam v2
```

Collected face images will be stored in `dataset` directory grouped by **User ID**. User's name and User ID will stored in SQLite database. You may add more fields in the database to store more information about the target person you have gathered by other methods.

You may collected as many face images of different person as you wanted and train them at once.

To train a face recognition model, run the `trainer.py` script.

``` bash
python3 trainer.py
```

The trained recognition model will be stored in `recognizer` directory, and we can run `detector_***.py` script to begin face recognition.

```bash
python3 detector_webcam.py # for using webcam
python3 detector_picam.py # for using PiCam v2
```

When the program detected a face, it will retrieve user information from SQLite database, and show target person's name in video window.

## Multi-threading Detection

Because face recognition using IP cam (via RTSP) consume a lot of computer power, we can only recognize face 5 times per second with Raspberry Pi 4 (4GB) when using single threading manner. We may release more computer power of Raspberry Pi by writing the code in multi-threading manner.

Codes in `threading` directory is multi-threading version of detector script, which is for webcam or IP cam.

```bash
cd threading
python3 detect_main.py
```

NB: The `Show` module in `Show.py` is used only for evaluate simple video capture in multi-threading manner.
