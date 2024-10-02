from dataclasses import dataclass
<<<<<<< HEAD
from time import sleep
from typing import List, Callable
import cv2.aruco as aruco # type: ignore
from driver import Robot, Driver, State, Event, Task

class StatefulRobot(Robot):
    @dataclass
    class CamStategy:
        PI_CAMERA   = 0
        GSTREAM     = 1

    def __init__(self, states: List[State], strategy=CamStategy.PI_CAMERA, img_size=(1280, 720), fps=30, port='/dev/ttyACM0'):
        """
        **Argument(s)**
        * states - Driver states
=======
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
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f
        * strategy - CamStrategy to use
        * img_size - Image size
        * fps - Frames per second
        * port - Serial port to bind
        """
        try:
<<<<<<< HEAD
            super().__init__(port)
=======
            # Composite inheritance requires that both supers call super(T, self).__init__(),
            # unfortunately Robot does not. Luckily Python is wonky, so this is a easy hack. 
            Waitable.__init__(self)
            Robot.__init__(self, port)
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f
        except:
            pass

        # Initialize the camera
        self.cam = None
        if strategy == StatefulRobot.CamStategy.PI_CAMERA:
            try:
                import picamera2  # type: ignore
                self.cam_strategy = strategy
<<<<<<< HEAD
=======
                self.cam_wait = Waitable()
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f
                self.cam = picamera2.Picamera2()
                self.cam_config = self.cam.create_video_configuration({
                    "size": img_size, 
                    "format": "RGB888"
                    },
                    controls={
                        "FrameDurationLimits": (int(1/fps * 1000000), int(1/fps * 1000000)),
<<<<<<< HEAD
                        # "LensPosition": 0,
                        # "ScalerCrop": [img_size[0]//2, img_size[1]//2, img_size[0], img_size[1]]
                    },
                    queue=False
                )
                self.cam.configure(self.config)
=======
                    },
                    queue=False
                )
                self.cam.configure(self.cam_config)
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f
                self.cam.start(show_preview=False)
            except:
                pass
        else:
            # GStream configuration here.
            pass

        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
<<<<<<< HEAD
        self.driver = Driver(self, 1000, states[0], *states[1:])
    
    def __del__(self):
=======
        self.driver = Driver(self)
    
    def __del__(self):
        self.driver.stop()
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f
        try:
            super().__del__()
            self.cam.stop()
        except:
            pass
<<<<<<< HEAD
        self.driver.stop()
=======
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f

    def capture(self):
        if self.cam_strategy == StatefulRobot.CamStategy.PI_CAMERA:
            return self.cam.capture_array("main")
<<<<<<< HEAD
        else:
            # GStream capture here.
=======
        elif self.cam_strategy == StatefulRobot.CamStategy.PI_CAMERA_REQ:
            with self.cam.capture_request(flush=True, signal_function=lambda _: self.cam_wait.wake()) as req:
                self.cam_wait.wait()
                return req.make_array("main")
        else:
            # GStream capture here.
            # Make sure libcamera is installed: gst-inspect-1.0 libcamerasrc
            # Try without videobox and/or appsink
            # Force BGR: video/x-raw, format=BGR
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f
            pass
    
    def default(self, state: State):
        """
        Sets the default state.

        **Argument(s)**
        * state - State to set as default.
        """
        self.driver.default(state)
<<<<<<< HEAD

    def add(self, state: State, default=False):
        """
        Adds a state to the statedriver.
        
        **Argument(s)**
        * state - State to add
        * default - If true, the added stage will be set as default

        **Return**

        The known states as a tuple, where the 1st element contains the names of the states,
        and the 2nd element contains the actual states.
        """
        return self.driver.add(state, default)
=======
    
    def add(self, runable: Task|State, default=False):
        """
        Adds a task or state to the statedriver. If the driver is started, this is a no-op.
        
        **Argument(s)**
        * runable - Task or state to add
        * default - If true and runable is a state, it'll be set as default
        """
        self.driver.add(runable, default)
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f

    def switch(self, id):
        """
        Switches state. 
        
        **Argument(s)**
        * id - State id. If the active state is equal to the requested state, this is a no-op.
        """
        self.driver.switch(id)

<<<<<<< HEAD
    def register(self, id, listener: Callable[[Event], None]):
        """
        Registers a listener to an event id.

        **Argument(s)**
        * id - Event id.
        * listener - Function callback. It'll get passed an Event object.
        """
        self.driver.register(id, listener)

    def task(self, task: Task):
        """
        Registers a task. If the driver is already started, this is a no-op.

        **Argument(s)**
        * task - Task to add.
        """
        self.driver.task(task)
        
    def start(self):
        """
        Starts the driver. If the driver is already started or no states has been added, this is a no-op.
        """
        self.driver.start()


    def stop(self):
        """
        Stops the driver. If the driver is already stopped, this is a no-op.
        """
        self.driver.stop()
   
if __name__ == "__main__":
    class BackgroundEvent(Event):
        @dataclass
        class Type:
            BACKGROUND = "robot-event-background"

        def __init__(self, id, robot, **kwords: str):
            super().__init__(id, robot, **kwords)
            self.msg = kwords["msg"]         

    class BackgroundTask(Task):
        def run(self, robot):
            print("\t\tHello from background")

    class FooState(State):
        def run(self, robot):
            print("\t\tHello from foo")
            
    class BarEvent(Event):
        @dataclass
        class Type:
            BAR = "robot-event-bar"

        def __init__(self, id, robot, **kwords: str):
            super().__init__(id, robot, **kwords)
            self.msg = kwords["msg"]

    class BarState(State):
        def run(self, robot):
            self.fire(BarEvent(BarEvent.Type.BAR, robot, msg="\t\tHello from bar"))
            self.done(True)

    def handleBar(e: BarEvent):
        print(e.msg)

    def handleBarAgain(e: BarEvent):
        print("{0} again".format(e.msg))

    test = StatefulRobot([FooState("foo"), BarState("bar")])
    test.task(BackgroundTask())
    test.register(BarEvent.Type.BAR, handleBar)
    test.register(BarEvent.Type.BAR, handleBarAgain)
    test.start()
    test.start()
    sleep(0.1)
    test.switch("bar")
    sleep(2)
    test.stop()
    test.stop()
    test.add(State("baz"))
    print(len(test.driver))
    test.add(State("baz"))
    print(len(test.driver))
    test.switch("nope")
=======
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
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f
