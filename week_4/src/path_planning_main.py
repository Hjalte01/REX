
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
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import robot
import grid
import rrt

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
    

def walk_and_rotate(robot, distance, angle):
    # Walk and rotate the robot
    robot.rotate(angle)
    robot.move(distance)


# Main loop for the path planning
def main():
    # Create the grid
    grid_size = 20
    cell_size = 1
    robot_size = 0.45
    grid_obj = grid.Grid(cell_size, grid_size)

    # Create the RRT object
    rrt_algorithm = rrt.RRT(grid_obj, robot_size)

    # Add obstacles to the grid by using the get_landmark function
    distances, angles = get_landmark(cam, img_dict, cam_matrix, coeff_vector, marker_length)
    if distances is not None:
        for i in range(len(distances)):
            pos = grid.Pos(distances[i], angles[i])
            grid_obj.add_obstacle(rrt_algorithm.init_cell, pos)
    

    rrt_algorithm.RRT()
    final_route = rrt_algorithm.final_route
    print(final_route)
    for index, pos in enumerate(final_route):
        if (index >= len(final_route-2)): break
        distance = np.linalg.norm([pos.x - final_route[index+1].x, pos.y - final_route[index+1].y])
        angle = np.arctan2(pos[1] - final_route[index+1].y, pos[0] - final_route[index+1].x)
        # walk_and_rotate(robot, distance, angle)
        print("Robot moved to: ", pos[0], pos[1])
        print("distance: ", distance, "angle: ", angle)


main()
