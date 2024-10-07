# This file is used to find the landmarks (Aruco Marker) in the image plane and drive the robot to the landmark 
# by computing the distance and angle between the robot and the landmark.

# 32.19 29.77

import cv2 # Import the OpenCV library
from cv2 import aruco
import time
import sys
import numpy as np
from pprint import *

import os, sys
from time import sleep

# get for the robot module from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import robot

try:
    import picamera2
    print("Camera.py: Using picamera2 module")
except ImportError:
    print("Camera.py: picamera2 module not available")
    exit(-1)

# print("OpenCV version = " + cv2.__version__)

def cam_pipeline(capture_width=1024, capture_height=720, framerate=30):
    """Utility function for setting parameters for the gstreamer camera pipeline"""
    return (
        "libcamerasrc !"
        "videobox autocrop=true !"
        "video/x-raw, width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "videoconvert ! "
        "appsink"
        % (
            capture_width,
            capture_height,
            framerate,
        )
    )

# Connection closed by 192.168.0.199 port 22Open a camera device for capturing
imageSize = (1024, 720)
FPS = 30
cam = cv2.VideoCapture(cam_pipeline(), apiPreference=cv2.CAP_GSTREAMER)
frame_duration_limit = int(1/FPS * 1000000) # Microseconds
# Change configuration to set resolution, framerate
picam2_config = cam.create_video_configuration({"size": imageSize, "format": 'RGB888'},
                                                            controls={"FrameDurationLimits": (frame_duration_limit, frame_duration_limit)},
                                                            queue=False)
cam.configure(picam2_config) # Not really necessary
cam.start(show_preview=False)

time.sleep(1)  # wait for camera to setup

    
# Capture an image from the camera


# get the dictionary for the aruco markers
marker_x = float(sys.argv[1])
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
aruco_board = aruco.GridBoard.create(3, 3, marker_x*0.001, float(sys.argv[2])*0.001, aruco_dict)

all_corners = []
all_ids = []
all_counts = []

constant_1_degree = 1.5 / 90


left = True
def get_landmark(cam, img_dict):
    """Get the landmark from the camera and return the distance and angle between the robot and the landmark"""
    # Capture an image from the camera
    # image = cam.capture_array("main")
    retval, image = cam.read()

    cv2.imshow("image", image)

    # Detect the markers in the images
    corners, ids, _ = aruco.detectMarkers(image, img_dict)

    if ids is None:
        left = False
        print("no ids detected")
    else:
        global all_corners
        global all_ids
        global all_counts
        all_corners = np.append(all_corners, corners)
        all_ids = np.append(all_ids, ids)
        all_counts = np.append(all_counts, len(ids))
    
def main():
    # initialize the robot
    arlo = robot.Robot()

    # sleep for 2 seconds
    sleep(2)

    # set the speed of the robot
    left_motor_diff = 0.875
    leftSpeed = 40*left_motor_diff
    rightSpeed = 40
    # one rotation
    n = 100/3 
    while(n > 0):
        n -= 1
        if left:
            print(arlo.go_diff(leftSpeed, rightSpeed, 1, 0))
        else:
            print(arlo.go_diff(leftSpeed, rightSpeed, 0, 1))
        
        get_landmark(cam, aruco_dict)
        sleep(0.01)

    print(arlo.stop_driver())
    sleep(1)

    cam.stop()


main()

print(len(all_ids))

# frame = cam.capture_array("main")
# cv2.imwrite("image.png", frame)
