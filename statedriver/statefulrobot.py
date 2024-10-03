from dataclasses import dataclass
from typing import Callable
from driver import Robot, Waitable, Driver, State, Event, Task
from camera import Camera

class StatefulRobot(Robot, Waitable):
    """
    Container class for various robot important objects.
    """
    @dataclass
    class CamStategy:
        PI_CAMERA           = 0
        PI_CAMERA_REQ       = 1
        GSTREAM             = 2

    def __init__(self, port='/dev/ttyACM0'):
        """
        **Argument(s)**
        * port - Serial port to bind.
        """
        try:
            # Composite inheritance requires that both supers call super(T, self).__init__(),
            # unfortunately Robot does not. Luckily Python is wonky, so this is a easy hack. 
            Waitable.__init__(self)
            Robot.__init__(self, port)
        except:
            pass

        self.driver = Driver(self, 1000)
        self.cam = Camera((1280, 720), 30)
    
    def __del__(self):
        self.driver.stop()
        try:
            super().__del__()
            self.cam.stop()
        except:
            pass

    def capture(self):
        """
        convenience method for [camera.capture](https://localhost:1234).
        """
        return self.cam.capture()
    
    def default(self, state: State):
        """
        convenience method for [driver.default](https://localhost:1234).
        """
        self.driver.default(state)

    def add(self, runable: Task, default=False):
        """
        convenience method for [driver.add](https://localhost:1234).
        """
        self.driver.add(runable, default)

    def switch(self, id):
        """
        convenience method for [driver.switch](https://localhost:1234).
        """
        self.driver.switch(id)

    def register(self, id, handler: Callable[[Event], None]):
        """
        convenience method for [driver.register](https://localhost:1234).
        """
        self.driver.register(id, handler)

    def unregister(self, id, handler: Callable[[Event], None]):
        """
        convenience method for [driver.unregister](https://localhost:1234).
        """
        self.driver.register(id, handler)

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
