# Exercise 3.3: Plot the landmark coordinates


import cv2 # Import the OpenCV library
from cv2 import aruco
import time
import sys
import numpy as np
from pprint import *
import matplotlib.pyplot as plt

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

    # save image
    cv2.imwrite("image.png", image)

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

        # Calculate the distance and angle between the robot and the landmarks

        distances = [np.linalg.norm(tvec) for tvec in tvecs]
        angles = [np.arctan2(tvec[0][0], tvec[0][2]) for tvec in tvecs]

        print("Distance: ", distances)
        print("Angle: ", angles)

        return distances, angles
    else:
        print("No markers detected")
        return None, None
    

# Plot the landmark coordinates
def get_coordinates(distance, angle):
    """Get the landmark's coordinates (x,y). Robot is at the origin (0, 0)
    and the landmark is at the distance and angle from the robot.

    args:
    distance: float: The distance between the robot and the landmark.
    angle: float: The angle between the robot and the landmark

    returns:
    x: np.array: The x-coordinate of the landmark (scalar if single landmark)
    y: np.array: The y-coordinate of the landmark (scalar if single landmark)
    """
    x = distance * np.sin(angle)
    y = distance * np.cos(angle)

    return x, y

# Create a map of the environment
def create_map(x_size, y_size):
    """Create a empy map of the environment"""
    # Create empty np array for the map
    map = np.zeros((x_size, y_size))

    return map

def update_map(map, x, y):
    """Update the map with the landmark coordinates
    args:
    map: np.array: The map of the environment
    x: np.array: The x-coordinate of the landmark (scalar if single landmark)
    y: np.array: The y-coordinate of the landmark (scalar if single landmark)
    """
    # Update the map with the landmark coordinates
    for xi, yi in zip(x, y):
        xi = int(np.floor(xi*100))
        yi = int(np.floor(yi*100))
        map[xi, yi] = 1
    return map



def saftety_margin(map, x, y, r):
    """Update the map with the landmark coordinates
    args:
    map: np.array: The map of the environment
    x: np.array: The x-coordinate of the landmark (scalar if single landmark)
    y: np.array: The y-coordinate of the landmark (scalar if single landmark)
    r: float: The radius of the robot
    """
    # Update the map with the landmark coordinates
    for xi, yi in zip(x, y):
        for i in range(-r, r+1):
            for j in range(-r, r+1):
                xi = int(np.floor(xi*100+i))
                yi = int(np.floor(yi*100+j))
                map[xi, yi] = 1
    return map


# Get all the landmarks in the image and plot them

def main():
    distance, angle = get_landmark(cam, img_dict, cam_matrix, coeff_vector, marker_length)

    # get the coordinates of the landmark
    x, y = get_coordinates(distance, angle)
    r_robot = 2.30 # radius of the robot in m
    r_box = 2.30 # radius of the robot in m
    pos = [0, 0]

    print("Landmark coordinates: ", x, y)
    
    # Create and update map
    map = create_map(500, 500)
    map = update_map(map, x, y)
    map = saftety_margin(map, [pos[0]], [pos[1]], r_robot)
    map = saftety_margin(map, x, y, r_box)

    # Plot the landmark coordinates
    robot_coordinates = np.array([0,0])
    plt.scatter(robot_coordinates[0], robot_coordinates[1], color='red')
    plt.scatter(x, y)
    plt.grid()
    plt.xlabel("x-coordinate")
    plt.ylabel("y-coordinate")
    plt.title("Landmark coordinates")
    plt.savefig("landmark_coordinates.png")
    
    cam.stop()


# Run the main function
if __name__ == "__main__":
    main()

