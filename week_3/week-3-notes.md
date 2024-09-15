# Notes week 3
So I've been reading the documentation for OpenCV. It seems that the course recommends/requires v4.6.0, but we have v4.10.0 (That's my mistake). So we can either keep using the new version, and disregard slides/examples and rely on the latest documentation, or we can downgrade.

## Downgrade
When I added OpenCV, I just added it to Pythons root. This means that whatever was there before is overwritten. This means that we need to:
 - Uninstall OpenCV.
 - Uninstall its dependencies (numpy)
 - Clear the cache so we get the required packages for v4.6.0 and not v4.10.0

 Now OpenCV isn't shipped with external libraries (aruco) by default. That is instead located in another package. With that in mind:

 ```
 pip uninstall opencv-python numpy
 pip cache purge
 pip install opencv-contrib-python==4.6.0.66
 ```

Now we have access to the API documented in the slides.

## Usage
This is taken directly from the [docs](https://docs.opencv.org/4.6.0/d9/d6a/group__aruco.html) and might work?:
```python
import numpy as np
from cv2 import aruco

# Begin with detecting a mark
img_path = "foo/bar"
img_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250) # As per the assignment
corners, ids, _ = aruco.detectMarkers(img_path, img_dict)

# Calibrate the camera
image_size = (20, 10)
cam_matrix = np.zeros((3, 3))   # From the docs, this should be 3x3
dist_coeffs = np.zeros((5, 1))  # From the docs, this should be 4x1, 5x1, 8x1, or 12x1
board = aruco.Board(corners, img_dict, ids)
_, cam_matrix, dist_coeffs, rvecs, tvecs = aruco.calibrateCameraAruco(
    corners, 
    ids, 
    1, # Maybe? From the docs 'number of markers in each frame so that corners and ids can be split'
    board,
    cam_matrix,
    dist_coeffs
)

# Get an estimation
focal_length = -1 # Needs to be calculated, as per the assignment
rvecs, tvecs = aruco.estimatePoseSingleMarkers(corners, focal_length, cam_matrix, dist_coeffs)
```
