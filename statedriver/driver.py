"""
A very simple statedriver. It implements events, tasks & states.
The execution of a cycle is sequential: tasks -> state -> event-listeners
"""
from time import sleep
from typing import Callable, List, Tuple
from threading import Thread, Lock
from dataclasses import dataclass
from robot import Robot

class Event:
    @dataclass
    class Type:
        pass

    def __init__(self, id: object, robot: Robot, **kwords):
        self.id = id
        self.robot = robot
        self.values = kwords

class Task:
    def __init__(self):
        self.__done__ = False

    def fire(self, event: Event):
        Driver.EventQueue.push(event)

    def done(self, flag=False):
        if flag:
            self.__done__ = flag
        return self.__done__
    
    def cancel(self):
        self.__done__ = True

    def run(self, robot: Robot):
        print("[LOG] The method {0}.run is not overridden.".format(self.__str__()))

class State(Task):
    def __init__(self, id: object):
        super().__init__()
        self.id = id

    def __str__(self) -> str:
        return "State<\"{0}\">".format(self.id)
    
class Driver():
    class EventQueue:
        __queue__: List[Event] = []
        
        def push(e: Event):
            Driver.EventQueue.__queue__.append(e)

    def __init__(self, robot: Robot, tick=100, default_state: State = None, *args: List[State]):
        """
        **Argument(s)**
        * robot - Arlo robot
        * tick - Driver cycle tick in ms
        * default_state - Driver default state
        * states - Driver states 
        """
        self.__robot__                  = robot
        self.__tick__                   = tick*0.001
        self.__states__                 = dict()
        self.__active_state__: State    = None
        self.__thread__: Thread         = None
        self.__listeners__              = dict()
        self.__tasks__                  = list()
        self.__lock__                   = Lock()
        self.__alive__                  = False

        if default_state:
            self.default(default_state)

        for arg in args:
            self.add(arg)

    def __str__(self):
        return "Driver[{0}]".format(", ".join([x.__str__() for x in self.__states__.values()]))
    
    def __getitem__(self, key: object) -> State:
        return self.__states__[key]
    def __setitem__(self, key: object, val: State):
        self.__states__[key] = val

    def __len__(self):
        return len(self.__states__)
    
    def __runner__(self):
        while True:
            with self.__lock__:
                if not self.__alive__:
                    return
            # Run tasks
            for task in self.__tasks__:
                try:
                    if not task.done():
                        task.run(self.__robot__)
                except Exception as err:
                    print("[ERR] An exception was thrown while running state \"{0}\".\n{1}".format(self.__active_state__.id, err))

            # Run the active state
            if self.__active_state__.done():
                self.switch("default")

            try:
                self.__active_state__.run(self.__robot__)
            except Exception as err:
                print("[ERR] An exception was thrown while running state \"{0}\".\n{1}".format(self.__active_state__.id, err))
                self.switch("default")

            # Flush the event queue
            while len(Driver.EventQueue.__queue__):
                event = Driver.EventQueue.__queue__.pop()
                if not event.id in self.__listeners__:
                    continue
                for f in self.__listeners__[event.id]:
                    try:
                        f(event)
                    except Exception as err:
                        print("[ERR] An exception was thrown while running state \"{0}\".\n{1}".format(self.__active_state__.id, err))

            sleep(self.__tick__)
                
    def states(self) -> Tuple[Tuple[str], Tuple[State]]:
        """
        **Returns** 
        
        The known states as a tuple, where the 1st element contains the names of the states,
        and the 2nd element contains the actual states.
        """
        return (tuple(self.__states__.keys()), tuple(self.__states__.values()))
                
    def default(self, state: State):
        """
        Sets the default state. If the driver is started, this is a no-op.

        **Argument(s)**
        * state - State to set as default.
        """
        if self.__thread__:
            return
        self["default"] = state

    def add(self, state: State, default=False):
        """
        Adds a state to the statedriver. If the driver is started, this is a no-op.
        
        **Argument(s)**
        * state - State to add
        * default - If true, the added stage will be set as default
        """
        if self.__thread__ or state.id in self.__states__:
            return 
        if default:
            self.default(state)
        self[state.id] = state

    def switch(self, id: object):
        """
        Switches state. 
        
        **Argument(s)**
        * id - State id. If the active state is equal to the requested state, this is a no-op.
        """
        if self.__active_state__.id == id:
            return
        if not (id in self.__states__.keys()):
            return print("[LOG] The state \"{0}\" has not been added to driver {1}.".format(id, self))
        self.__active_state__ = self[id]
        print("[LOG] Switched to state {0}.".format(self.__active_state__.__str__()))

    def task(self, task: Task):
        """
        Registers a task. If the driver is already started, this is a no-op.

        **Argument(s)**
        * task - Task to add.
        """
        if self.__thread__:
            return
        self.__tasks__.append(task)

    def register(self, id: object, listener: Callable[[Event], None]):
        """
        Registers a listener to an event id. If the driver is already started, this is a no-op.

        **Argument(s)**
        * id - Event id.
        * listener - Function callback. It'll get passed an Event object.
        """
        if self.__thread__:
            return
        self.__listeners__.setdefault(id, []).append(listener)

    def start(self):
        """
        Starts the driver. If the driver is already started, this is a no-op.
        """
        if self.__thread__:
            return
        if not ("default" in self.__states__.keys()):
            return print("[LOG] No default state for driver {0}. Skipping start.".format(self))
        print("[LOG] Starting driver {0}.".format(self))
        self.__active_state__ = self["default"]
        self.__alive__ = True
        self.__thread__ = Thread(target=self.__runner__, daemon=True)
        self.__thread__.start()

    def stop(self):
        """
        Stops the driver. If the driver is already stopped, this is a no-op.
        """
        if self.__thread__ is None:
            return
        print("[LOG] Stopping driver {0}.".format(self))
        with self.__lock__:
            self.__alive__ = False
        self.__thread__.join(3*self.__tick__)
        self.__thread__ = None
