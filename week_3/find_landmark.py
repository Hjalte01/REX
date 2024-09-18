# This file is used to find the landmarks (Aruco Marker) in the image plane and drive the robot to the landmark 
# by computing the distance and angle between the robot and the landmark.

import cv2 # Import the OpenCV library
from cv2 import aruco
import time
import sys
import numpy as np
from pprint import *

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

print("Image shape: ", image.shape)


img_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250) # As per the assignment

# Detect the markers in the images
corners, ids, _ = aruco.detectMarkers(image, img_dict)

print("corners: ", corners)

if corners == None:
    print("no corners detected")
    sys.exit()

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

# Estimate the pose of the markers
rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, marker_length, cam_matrix, coeff_vector)

print("rvecs: ", rvecs)
print("tvecs: ", tvecs)
