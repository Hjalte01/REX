from dataclasses import dataclass
from time import sleep
from typing import List, Callable
import cv2.aruco as aruco # type: ignore
from driver import Robot, Driver, State, Event, Task

class StatefulRobot(Robot):
    @dataclass
    class CamStategy:
        PI_CAMERA   = 0
        GSTREAM     = 1

    def __init__(self, strategy=CamStategy.PI_CAMERA, img_size=(1280, 720), fps=30, port='/dev/ttyACM0'):
        """
        **Argument(s)**
        * states - Driver states
        * strategy - CamStrategy to use
        * img_size - Image size
        * fps - Frames per second
        * port - Serial port to bind
        """
        try:
            super().__init__(port)
        except:
            pass

        # Initialize the camera
        self.cam = None
        if strategy == StatefulRobot.CamStategy.PI_CAMERA:
            try:
                import picamera2  # type: ignore
                self.cam_strategy = strategy
                self.cam = picamera2.Picamera2()
                self.cam_config = self.cam.create_video_configuration({
                    "size": img_size, 
                    "format": "RGB888"
                    },
                    controls={
                        "FrameDurationLimits": (int(1/fps * 1000000), int(1/fps * 1000000)),
                        # "ScalerCrop": [0, 0, img_size[0]*10, img_size[1]*10],
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
        self.driver = Driver(self, 100)
    
    def __del__(self):
        try:
            super().__del__()
            self.cam.stop()
        except:
            pass
        self.driver.stop()

    def capture(self):
        if self.cam_strategy == StatefulRobot.CamStategy.PI_CAMERA:
            return self.cam.capture_request().make_array("main")
        else:
            # GStream capture here.
            pass
    
    def default(self, state: State):
        """
        Sets the default state.

        **Argument(s)**
        * state - State to set as default.
        """
        self.driver.default(state)

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

    def switch(self, id):
        """
        Switches state. 
        
        **Argument(s)**
        * id - State id. If the active state is equal to the requested state, this is a no-op.
        """
        self.driver.switch(id)

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
        
    def start_driver(self):
        """
        Starts the driver. If the driver is already started or no states has been added, this is a no-op.
        """
        self.driver.start()

    def stop_driver(self):
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
    test.stop_driver()
    test.stop_driver()
    test.add(State("baz"))
    print(len(test.driver))
    test.add(State("baz"))
    print(len(test.driver))
    test.switch("nope")
