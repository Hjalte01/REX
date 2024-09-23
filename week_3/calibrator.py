# This file is used to find the landmarks (Aruco Marker) in the image plane and drive the robot to the landmark 
# by computing the distance and angle between the robot and the landmark.

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

# Open a camera device for capturing
imageSize = (1280, 720)
FPS = 30
cam = picamera2.Picamera2()
frame_duration_limit = int(1/FPS * 1000000) # Microseconds
# Change configuration to set resolution, framerate
picam2_config = cam.create_video_configuration({"size": imageSize, "format": 'RGB888'},
                                                            controls={"FrameDurationLimits": (frame_duration_limit, frame_duration_limit)},
                                                            queue=False)
cam.configure(picam2_config) # Not really necessary
cam.start(show_preview=False)

time.sleep(1)  # wait for camera to setup

    
# Capture an image from the camera
image = cam.capture_array("main")
image_width = image.shape[1]
image_height = image.shape[0]

# Get the camera matrix and distortion coefficients
cam_matrix = np.zeros((3, 3))
coeff_vector = np.zeros(5)

focal_length = 1694.0
principal_point = (image_width / 2, image_height / 2)

cam_matrix[0, 0] = focal_length  # f_x
cam_matrix[1, 1] = focal_length  # f_y
cam_matrix[0, 2] = principal_point[0]  # c_x
cam_matrix[1, 2] = principal_point[1]  # c_y
cam_matrix[2, 2] = 1.0

marker_length = 0.15 # meters

# get the dictionary for the aruco markers
marker_x = float(sys.argv[1])
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
aruco_board = aruco.GridBoard.create(4, 4, marker_x*0.001, float(sys.argv[2])*0.001, aruco_dict)

all_corners = []
all_ids = []
all_counts = []



def get_landmark(cam, img_dict, cam_matrix, coeff_vector, marker_length, left):
    """Get the landmark from the camera and return the distance and angle between the robot and the landmark"""
    # Capture an image from the camera
    image = cam.capture_array("main")

    # Detect the markers in the images
    corners, ids, _ = aruco.detectMarkers(image, img_dict)

    print("corners: ", corners)

    if ids == None:
        print("no ids detected")
        return not(left)
    else:
        all_corners = np.append(all_corners, corners)
        ids = np.append(all_ids, ids)
        all_corners = np.append(all_counts, len(ids))
    

def main():
    # initialize the robot
    arlo = robot.Robot()

    # sleep for 2 seconds
    sleep(2)

    # set the speed of the robot
    left_motor_diff = 0.875
    leftSpeed = 40*left_motor_diff
    rightSpeed = 40

    running = True
    left = True
    while(running):
        # 
        if left:
            print(arlo.go_diff(leftSpeed, rightSpeed, 1, 0))
        else:
            print(arlo.go_diff(leftSpeed, rightSpeed, 0, 1))
        
        sleep(1)
        left = get_landmark(cam, aruco_dict, cam_matrix, coeff_vector, marker_length, left)
        print(arlo.stop())
        sleep(1)

    print(arlo.stop())
    sleep(1)

    cam.stop()
