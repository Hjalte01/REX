import cv2 # Import the OpenCV library
from cv2 import aruco
import time
from pprint import *

try:
    import picamera2
    print("Camera.py: Using picamera2 module")
except ImportError:
    print("Camera.py: picamera2 module not available")
    exit(-1)

print("OpenCV version = " + cv2.__version__)

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

print("Image shape: ", image.shape)

# # Save the image to a file
# cv2.imwrite("aruco_marker.jpg", image)


img_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250) # As per the assignment

# Detect the markers in the images
corners, ids, _ = aruco.detectMarkers(image, img_dict)

print("Corners detected: ", len(corners))


def compute_focal_len_of_image(X, Z, corners):
    """
    The focal length of the camera can be estimated using the formula:
    f = (x * Z) / X
    Parameters:
    - X: Width of the marker in millimeters
    - Z: Distance from the camera to the marker in millimeters
    - corners: Corners of the detected marker in the image plane
    """
    print(corners)
    print(corners[0])
    print(corners[0][0])
    x = corners[0][1] - corners[0][0]  # x difference between the two top corners
    print(x)
    return (x * Z) / X

# Measure the width of the marker in millimeters
X = 150

# Measure the distance from the camera to the marker in millimeters
Z = 400



# Compute the focal length of the camera
focal_length = compute_focal_len_of_image(X, Z, corners[0]) # Corners [0] is the first marker detected

# Save the focal lengths to a file and the corners
with open("focal_lengths.txt", "a") as f:
    f.write("Focal lengths: " + str(focal_length) + "\n")
    f.write("Corners: " + str(corners) + "\n")
    f.close()







