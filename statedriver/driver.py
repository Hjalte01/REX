"""
A very simple statedriver. It implements events, tasks & states.
The execution of a cycle is sequential: tasks -> state -> event-listeners
"""
from time import sleep
import traceback
from typing import Type, Callable, List, Tuple, Dict, overload
from threading import Condition, Thread
from dataclasses import dataclass
from robot import Robot

class Event:
    @dataclass
    class Type:
        pass

    def __init__(self, id: object, **kwords):
        self.id = id
        self.robot: Robot|None = None
        self.origin: State|None = None
        self.values = kwords

    def __str__(self) -> str:
        return "Event<\"{}\">".format(self.id)

class Waitable(object):
    def __init__(self) -> None:
        super(Waitable, self).__init__()
        self.__lock__ = Condition()
        self.__wait__ = False

    def wait(self):
        with self.__lock__ :
            self.__wait__ = True
            while self.__wait__:
                self.__lock__.wait()

    def wake(self):
        with self.__lock__:
            self.__wait__ = False
            self.__lock__.notify_all()

class Task(Waitable):
    def __init__(self):
        super().__init__()
        self.__done__ = False

    def fire(self, event: Event):
        Driver.EventQueue.push(event)

    def done(self, flag=None):
        if flag is not None:
            self.__done__ = flag
        return self.__done__

    def cancel(self):
        self.done(True)
        self.wake()

    def run(self, _: Robot):
        print("[LOG] The method {0}.run is not overridden.".format(self))

class State(Task):
    def __init__(self, id: object):
        super().__init__()
        self.id = id

    def __str__(self) -> str:
        return "State<\"{0}\">".format(self.id)
    
class Driver(Waitable):
    class EventQueue:
        __queue__: List[Event] = []
        
        def push(e: Event):
            Driver.EventQueue.__queue__.append(e)

    def __init__(self, robot: Robot, cycle=100, default_state: object = None, *args: List[State]):
        """
        **Argument(s)**
        * robot - Arlo robot
        * cycle - Driver cycle in ms
        * default_state - Driver default state
        * states - Driver states 
        """
        super().__init__()
        self.__robot__                  = robot
        self.__cycle__                   = cycle*0.001
        self.__states__                 = dict()
        self.__active_state__: State    = None
        self.__thread__: Thread         = None
        self.__events__                 = dict()
        self.__tasks__                  = list()
        self.__alive__                  = False

        if default_state:
            self.__default__ = default_state
        else:
            self.__default__ = None

        for arg in args:
            self.add(arg)

    def __str__(self):
        return "Driver[{0}]".format(", ".join([x.__str__() for x in self.__states__.values()]))

    def __len__(self):
        return len(self.__states__)
    
    def __is_alive__(self):
        with self.__lock__:
            return self.__alive__
    
    def __runner__(self):
        while self.__is_alive__():
            # Run tasks
            for t in self.__tasks__:
                if t.done(): 
                    continue
                try:
                    t.run(self.__robot__)
                except Exception as err:
                    print("[ERR] An exception was thrown while running state \"{0}\".\n{1}".format(self.__active_state__.id, traceback.print_exc()))

            # Run the active state
            if self.__active_state__.done():
                self.switch(self.__default__)

            try:
                self.__active_state__.run(self.__robot__)
            except Exception as err:
                print("[ERR] An exception was thrown while running state \"{0}\".\n{1}".format(self.__active_state__.id, err))
                self.switch(self.__default__)

            # Flush the event queue
            while len(Driver.EventQueue.__queue__):
                e = Driver.EventQueue.__queue__.pop()
                with self.__lock__:
                    events = self.__events__.copy()
                if not e.id in events.keys():
                    continue
                for f in events[e.id]:
                    try:
                        e.robot = self.__robot__
                        e.origin = self.__active_state__
                        f(e)
                    except Exception as err:
                        print("[ERR] An exception was thrown while running state \"{0}\".\n{1}".format(self.__active_state__.id, err))

            sleep(self.__cycle__)
                
    def states(self) -> Tuple[Tuple[str], Tuple[State]]:
        """
        **Returns** 
        
        The known states as a tuple, where the 1st element contains the names of the states,
        and the 2nd element contains the actual states.
        """
        return (tuple(self[State].keys()), tuple(self[State].values()))
                
    def default(self, id: object):
        """
        Sets the default state id. If the driver is started, this is a no-op.

        **Argument(s)**
        * state - State to set as default.
        """
        if self.__thread__:
            return
        self.__default__ = id

    def add(self, runable: Task, default=False):
        """
        Adds a task or state to the statedriver. If the driver is started, this is a no-op.
        
        **Argument(s)**
        * runable - Task or state to add
        * default - If true and runable is a state, it'll be set as default
        """
        if self.__thread__:
            return
        if isinstance(runable, State):
            if runable.id in self.__states__.keys():
                return
            if default:
                self.__default__ = runable.id
            self.__states__[runable.id] = runable
        else:
            if runable in self.__tasks__:
                return
            self.__tasks__.append(runable)

    def switch(self, id: object):
        """
        Switches state. 
        
        **Argument(s)**
        * id - State id. If the active state is equal to the requested state, this is a no-op.
        """
        if self.__active_state__ and self.__active_state__.id == id:
            return
        if not (id in self.__states__.keys()):
            return print("[LOG] The state \"{0}\" has not been added to driver {1}.".format(id, self))
        with self.__lock__:
            self.__active_state__.cancel()
            self.__active_state__ = self.__states__[id]
            self.__active_state__.done(False)
        print("[LOG] Switched to state {0}.".format(self.__active_state__))

    def register(self, id: object, handler: Callable[[Event], None]):
        """
        Register a handler to an event id.

        **Argument(s)**
        * id - Event id.
        * handler - Event handler. It'll get passed an Event object.
        """
        with self.__lock__:
            if handler in self.__events__.setdefault(id, []):
                return
            self.__events__[id].append(handler)

    def unregister(self, id: object, handler: Callable[[Event], None]):
        """
        Unregister a handler to an event id.

        **Argument(s)**
        * id - Event id.
        * handler - Event handler.
        """
        with self.__lock__:
            if not (id in self.__events__.keys()):
                return
            self.__events__[id] = list(filter(lambda f: f is not handler, self.__events__[id]))

    def start(self):
        """
        Starts the driver. If the driver is already started, this is a no-op.
        """
        if self.__thread__:
            return
        if not self.__default__:
            return print("[LOG] No default state for driver {0}. Skipping start.".format(self))
        self.__active_state__ = self.__states__[self.__default__]
        self.__alive__ = True
        self.__thread__ = Thread(target=self.__runner__, daemon=True)
        self.__thread__.start()
        print("[LOG] Started driver {0}.".format(self))

    def stop(self):
        """
        Stops the driver. If the driver is already stopped, this is a no-op.
        """
        if self.__thread__ is None:
            return
        with self.__lock__:
            self.__active_state__.cancel()
            self.__active_state__.wake()
            self.__alive__ = False
            self.wake()
        self.__thread__.join(3*self.__cycle__)
        self.__thread__ = None
        print("[LOG] Stopped driver {0}.".format(self))

    def wait(self):
        """
        Awaits execution of the driver untill it's awaken. If the driver is stopped, this is a no-op.
        """
        if self.__thread__ is None:
            return

        class WaitTask(Task):
            def __init__(self, driver):
                super().__init__()
                self.driver = driver

            def run(self, _: Robot):
                self.wait()
                with self.__lock__:
                    self.driver.__tasks__ = list(filter(lambda x: x is not self, self.driver.__tasks__))

        with self.__lock__:
            self.__tasks__ = [WaitTask(self)] + self.__tasks__

    def wake(self):
        """
        Wakes the driver. If the driver is stopped, this is a no-op.
        """
        if self.__thread__ is None:
            return
        self.__tasks__[0].wake()
    