from cv2 import aruco
from time import sleep
import numpy as np
import sys
import picamera2

img_size = (1280, 720)
fps = 30
cam = picamera2.Picamera2()
frame_dur_limit = int(1/fps*1000000)
picam_config = cam.create_video_configuration({
    "size": img_size,
    "format": "RGB888"
    },
    controls= {
        "FrameDurationLimits": (
            frame_dur_limit, 
            frame_dur_limit
        )
    },
    queue=False
)

cam.configure(picam_config)
cam.start(show_preview=False)
sleep(1)

img = cam.capture_array("main")
cv2.imwrite("img.png", img)

img_dict  = a
