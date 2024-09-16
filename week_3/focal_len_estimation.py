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

pprint(cam.camera_configuration()) # Print the camera configuration in use

time.sleep(1)  # wait for camera to setup



#### Capture frames from the camera and detect the marker with Aruco ###

def capture_frames(cam, num_frames=10):
    images = []
    for i in range(num_frames):
        image = cam.capture_array("main")
        images.append(image)
    return images

# Capture 10 frame from the camera
images = capture_frames(cam, num_frames=10)

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)


# Detect the markers
corners, ids = aruco.ArucoDetector(aruco_dict).detectMarkers(images)
print(corners, ids)


# Compute the focal length of the camera
"""
The focal length of the camera can be estimated using the formula:
f = (x * Z) / X
where:
- f is the focal length of the camera
- x is the width of the marker in pixels (in the image plane)
- Z is the distance from the camera to the marker in millimeters

Known values:
- x: can be computed from the corners of the detected marker (corners)
- X: can be measured using a ruler
- Z: can be measured using a ruler
"""

def compute_focal_len_of_image(X, Z):
    # Compute the width of the marker in pixels
    x = corners[0][0][1][0] - corners[0][0][0][0]
    return (x * Z) / X

# Measure the width of the marker in millimeters
X = 150  # Width of the marker in millimeters

# Measure the distance from the camera to the marker in millimeters
Z = 870  # Distance from the camera to the marker in mill


# Save the focal length of the camera for each image, corners


focal_lengths = []

for i in range(len(images)):
    f = compute_focal_len_of_image(X, Z)
    focal_lengths.append(f)


# Save the focal lengths to a file and the corners
with open("focal_lengths.txt", "w") as f:
    f.write("Focal lengths: " + str(focal_lengths) + "\n")
    f.write("Corners: " + str(corners) + "\n")
    f.close()







