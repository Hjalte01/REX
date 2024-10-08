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
img_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250) # As per the assignment


def get_landmark(cam, img_dict, cam_matrix, coeff_vector, marker_length):
    """Get the landmark from the camera and return the distance and angle between the robot and the landmark"""
    # Capture an image from the camera
    image = cam.capture_array("main")

    # Detect the markers in the images
    corners, ids, _ = aruco.detectMarkers(image, img_dict)

    print("corners: ", corners)
    print(ids)

    # check if the markers are detected
    if corners != ():
        # Estimate the pose of the markers
        rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, marker_length, cam_matrix, coeff_vector)

        print("rvecs: ", rvecs)
        print("tvecs: ", tvecs)

        # Calculate the distance and angle between the robot and the landmark

        distance = np.linalg.norm(tvecs[0])
        angle = np.arctan2(tvecs[0][0][0], tvecs[0][0][2])

        print("Distance: ", distance)
        print("Angle: ", angle)

        return distance, angle
    else:
        print("No markers detected")
        return None, None



def search_for_landmark(cam, img_dict, cam_matrix, coeff_vector, marker_length, arlo, leftSpeed, rightSpeed):
    """
    Turn around until the landmark is found and return the distance and angle between the robot and the landmark
    """
    turn_speed_constant = 0.95
    while True:
        distance, angle = get_landmark(cam, img_dict, cam_matrix, coeff_vector, marker_length)
        if distance != None:
            return distance, angle
        else:
            # Turn around
            print(arlo.go_diff(leftSpeed*turn_speed_constant, rightSpeed*turn_speed_constant, 0, 1))
            sleep(0.1)
            print(arlo.stop())
    

# Correct the angle of the robot while driving towards the landmark
def correct_angle(angle, arlo, leftSpeed, rightSpeed):
    """
    Correct the angle of the robot by stopping and turning towards the landmark.
    """
    if angle != None:
        while abs(angle) > 0.05:
            print(arlo.stop())
            # Get angle between the robot and the landmark
            distance, angle = get_landmark(cam, img_dict, cam_matrix, coeff_vector, marker_length)
            if angle == None:
                break
            # Turn left correction
            if angle > 0.05:
                print(arlo.go_diff(leftSpeed, rightSpeed, 1, 0))
                sleep(0.01)
            # Right turn correction
            elif angle < -0.05:
                print(arlo.go_diff(leftSpeed, rightSpeed, 0, 1))
                sleep(0.01)
 


def drive_towards_landmark(distance, angle, arlo, leftSpeed, rightSpeed):
    """
    Drive the robot towards the landmark and keep updating the distance and angle between the robot and the landmark
    """
    # Turn correction
    correct_angle(angle, arlo, leftSpeed, rightSpeed)

    # Drive towards the landmark
    while distance > 0.4:
        print(arlo.go_diff(leftSpeed, rightSpeed, 1, 1))

        # Update the distance and angle between the robot and the landmark
        distance, angle = get_landmark(cam, img_dict, cam_matrix, coeff_vector, marker_length)

        if distance == None:
            break

        # Correct the angle of the robot while driving towards the landmark
        correct_angle(angle, arlo, leftSpeed, rightSpeed)

    
    print(arlo.stop())
    print("Landmark reached")

    return distance, angle


def main():
    # initialize the robot
    arlo = robot.Robot()

    # sleep for 2 seconds
    sleep(2)

    # set the speed of the robot
    left_motor_diff = 0.920
    leftSpeed = 40*left_motor_diff
    rightSpeed = 40

    # search for the landmark, if landmark is lost during the search, the robot will turn around until the landmark is found again
    distance, angle = search_for_landmark(cam, img_dict, cam_matrix, coeff_vector, marker_length, arlo, leftSpeed, rightSpeed)

    # Drive towards the landmark
    drive_towards_landmark(distance, angle, arlo, leftSpeed, rightSpeed)

    cam.stop()


main()