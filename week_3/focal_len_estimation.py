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

# Capture 1 frame from the camera
image = cam.capture_array("main")
print("Image shape: ", image.shape)

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)


# Detect the markers
corners, ids, rejected = aruco.ArucoDetector().detectMarkers(image, aruco_dict)

# If markers are detected, draw them on the image
if ids is not None:
    image_with_markers = aruco.drawDetectedMarkers(image.copy(), corners, ids)

# Display the resulting image
cv2.imshow('Detected Markers', image_with_markers)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save the image to a file
cv2.imwrite("image.jpg", image)


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

# Compute the width of the marker in pixels
x = corners[0][0][1][0] - corners[0][0][0][0]

# Measure the width of the marker in millimeters
X = 100  # Width of the marker in millimeters

# Measure the distance from the camera to the marker in millimeters
Z = 500  # Distance from the camera to the marker in mill

# Compute the focal length of the camera
f = (x * Z) / X

print("Focal length of the camera: ", f)


