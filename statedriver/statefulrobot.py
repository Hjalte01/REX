from dataclasses import dataclass
from typing import Callable
import cv2.aruco as aruco # type: ignore
from driver import Robot, Waitable, Driver, State, Event, Task

class StatefulRobot(Robot, Waitable):
    @dataclass
    class CamStategy:
        PI_CAMERA           = 0
        PI_CAMERA_REQ       = 1
        GSTREAM             = 2

    def __init__(self, strategy=CamStategy.PI_CAMERA, img_size=(1280, 720), fps=30, port='/dev/ttyACM0'):
        """
        **Argument(s)**
        * strategy - CamStrategy to use
        * img_size - Image size
        * fps - Frames per second
        * port - Serial port to bind
        """
        try:
            # Composite inheritance requires that both supers call super(T, self).__init__(),
            # unfortunately Robot does not. Luckily Python is wonky, so this is a easy hack. 
            Waitable.__init__(self)
            Robot.__init__(self, port)
        except:
            pass

        # Initialize the camera
        self.cam = None
        if strategy == StatefulRobot.CamStategy.PI_CAMERA:
            try:
                import picamera2  # type: ignore
                self.cam_strategy = strategy
                self.cam_wait = Waitable()
                self.cam = picamera2.Picamera2()
                self.cam_config = self.cam.create_video_configuration({
                    "size": img_size, 
                    "format": "RGB888"
                    },
                    controls={
                        "FrameDurationLimits": (int(1/fps * 1000000), int(1/fps * 1000000)),
                    },
                    queue=False
                )
                self.cam.configure(self.cam_config)
                self.cam.start(show_preview=False)
            except:
                pass
        else:
            # GStream configuration here.
            pass

        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        self.driver = Driver(self)
    
    def __del__(self):
        self.driver.stop()
        try:
            super().__del__()
            self.cam.stop()
        except:
            pass

    def capture(self):
        if self.cam_strategy == StatefulRobot.CamStategy.PI_CAMERA:
            return self.cam.capture_array("main")
        elif self.cam_strategy == StatefulRobot.CamStategy.PI_CAMERA_REQ:
            with self.cam.capture_request(flush=True, signal_function=lambda _: self.cam_wait.wake()) as req:
                self.cam_wait.wait()
                return req.make_array("main")
        else:
            # GStream capture here.
            # Make sure libcamera is installed: gst-inspect-1.0 libcamerasrc
            # Try without videobox and/or appsink
            # Force BGR: video/x-raw, format=BGR
            pass
    
    def default(self, state: State):
        """
        Sets the default state.

        **Argument(s)**
        * state - State to set as default.
        """
        self.driver.default(state)
    
    def add(self, runable: Task|State, default=False):
        """
        Adds a task or state to the statedriver. If the driver is started, this is a no-op.
        
        **Argument(s)**
        * runable - Task or state to add
        * default - If true and runable is a state, it'll be set as default
        """
        self.driver.add(runable, default)

    def switch(self, id):
        """
        Switches state. 
        
        **Argument(s)**
        * id - State id. If the active state is equal to the requested state, this is a no-op.
        """
        self.driver.switch(id)

    def register(self, id, handler: Callable[[Event], None]):
        """
        Register a handler to an event id.

        **Argument(s)**
        * id - Event id.
        * handler - Event handler. It'll get passed an Event object.
        """
        self.driver.register(id, handler)

    def unregister(self, id, handler: Callable[[Event], None]):
        """
        Register a handler to an event id.

        **Argument(s)**
        * id - Event id.
        * handler - Event handler.
        """
        self.driver.register(id, handler)

    def wait(self, waitable: Waitable):
        """
        Awaits execution of a waitable untill it's awaken.

        **Argument(s)**
        * waitable - A robot or driver
        """
        if isinstance(waitable, Robot):
            super().wait()
        else:
            self.driver.wait()

    def wait_for(self, event: Event):
        """
        Awaits execution untill the event is fired.
        """
        def f(_):
            self.wake(self)
        self.driver.register(event, f)
        self.wait(self)
        self.driver.unregister(event, f)

    def wake(self, waitable: Waitable):
        """
        Wakes a waitable.

        **Argument(s)**
        * waitable - A robot or driver
        """
        if isinstance(waitable, Robot):
            super().wake()
        else:
            self.driver.wake()

    def start(self):
        """
        Starts the robot.
        """
        self.driver.start()

    def stop(self):
        """
        Stops the robot.
        """
        try:
            super().stop()
        except:
            pass   
