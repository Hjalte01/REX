"""
A very simple statedriver. It implements events, tasks & states.
The execution of a cycle is sequential: tasks -> state -> event-listeners
"""
import sys
import os
from time import sleep
import traceback
from typing import Callable, List, Tuple
from threading import Condition, Thread
from dataclasses import dataclass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from robot import Robot

@dataclass
class EventType:
    def __init__(self, id: str):
        self.id = id

    def __str__(self):
        return self.id

class Event:
    """
    Event objects are passed to event handlers.
    """
    def __init__(self, type: EventType, **kwords):
        """
        If kwords are supplied, the values are made available as a member with the keys as accessors.
        **Argument(s)**
        * type: object - Unique identifier for the event-type. The object must be hashable
        * kwords: **dict - Additional event values.
        """
        self.type = type
        self.robot: Robot = None
        self.origin: State = None
        self.values = kwords
        for k, v in kwords.items():
            self.__setattr__(k, v)
        
    def __str__(self):
        return "{0}<\"{1}\">".format(self.__class__.__qualname__, self.type)

class Waitable(object):
    """
    A Waitable is a type that can run custom logic after a (optional) given wait.
    """
    def __init__(self):
        super(Waitable, self).__init__()
        self.__lock__ = Condition()
        self.__wait__ = True

    def __enter__(self):
        self.__lock__.acquire()
        return self.__lock__
    
    def __exit__(self, *_):
        self.__lock__.release()

    def fire(self, event: Event):
        """
        Fires the passed event. If any event handlers are listening to the events type, those handlers will be called.

        **Argument(s)**
        * event:  [Event](https://https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-event) - The event to fire	
        """
        with self:
            Driver.Events.push(event)

    def wait(self, signal: Callable[[], bool]=None):
        """
        Awaits execution untill signaled by [waitable.wake](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#waitablewake---none) or the passed signal.

        **Argument(s)**
        * signal: () -> bool - Wakes the  waitable when the signal function returns true.	
        """
        with self as lock:
            if signal:
                lock.wait_for(signal)
                return
            while self.__wait__:
                lock.wait()

    def wait_for(self, type: EventType):
        """
        Awaits execution untill an event with the passed event-type fires.

        **Argument(s)**
        * type: [EventType](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-eventtype)
        """
        with self as lock:
            Driver.Waiters.push((type, self))
            while self.__wait__:
                lock.wait()

    def wake(self):
        """
        Signal the waitable to wake and resume execution.
        """
        with self as lock:
            self.__wait__ = False
            lock.notify_all()

    def cancel(self):
        """
        Alias fo [waitable.wake](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#waitablewake---none).
        """
        self.wake()

    def reset(self):
        """
        Resets the waitable.
        """
        with self:
            self.__wait__ = True

class Task(Waitable):
    """
    A Task represents a recurring task, that is run every [Driver](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-driverwaitable) cycle regardless of state. 
    """
    def __init__(self):
        super().__init__()
        self.__done__ = False

    def done(self, flag=None):
        """
        Signals the task to end. If it's waiting, it'll be woken.

        **Argument(s)**
        * flag: bool - If true, ends the task.
        """
        with self:
            if flag is not None:
                self.__done__ = flag
            return self.__done__

    def cancel(self):
        self.done(True)
        super().wake()

    def reset(self):
        with self:
            super().reset()
            self.__done__ = False

    def run(self, _: Robot):
        """
        Virtual method that must be overriden by classes inheriting from Task. It'll get passed a Robot object.

        **Argument(s)**
        * robot - Arlo robot.
        """
        pass

class State(Task):
    """
    A state represents a unique task. Only one state is running at any given time.
    """
    def __init__(self, id: object):
        """
        **Argument(s)**
        * id: object - object | Unique identifier for the state. The object must be hashable.
        """
        super().__init__()
        self.id = id

    def __str__(self) -> str:
        return "{0}<\"{1}\">".format(self.__class__.__qualname__, self.id)
    
class Driver(Waitable):
    """
    A driver handles execution of runables(Task or State objects). 
    Runables are executed sequentially in parallel with the main thread and in a threadsafe context. 
    The order of execution is **tasks -> state -> event handlers -> waitables**. 
    Exceptions from tasks, states and event handlers are caught, except for exceptions in the default state, 
    which will kill the thread gracefully. 
    """
    class Events:
        __queue__: List[Event] = []
        
        def push(e: Event):
            Driver.Events.__queue__.append(e)

    class Waiters:
        __queue__: List[Tuple[EventType, Waitable]] = []
        
        def push(val: Tuple[EventType, Waitable]):
            Driver.Waiters.__queue__.append(val)

    def __init__(self, robot: Robot, cycle=100, default_state: object = None, *states: List[State]):
        """
        **Argument(s)**
        * robot: Robot - Arlo robot
        * cycle: int - Driver cycle in ms
        * default_state: [State](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-statetask) - Default state.
        * states - List<[State](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-statetask)>: Driver states.
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
        self.__wait__                   = False
        self.__signal__                 = None

        if default_state:
            self.__default__ = default_state
        else:
            self.__default__ = None

        for arg in states:
            self.add(arg)

    def __str__(self):
        return "Driver[{0}]".format(", ".join([x.__str__() for x in self.__states__.values()]))

    def __len__(self):
        return len(self.__states__)
    
    def __is_alive__(self):
        with self:
            return self.__alive__
        
    def __caller__(self, f, *args):
        with self:
            try:
                    f(*args)
            except Exception:
                print("[ERR] An exception was thrown while running state {0}.".format(self.__active_state__))
                traceback.print_exc()
                if self.__active_state__.id == self.__default__:
                    self.__alive__ = False
                else:
                    self.switch(self.__default__)

    def __runner__(self):  
        while self.__is_alive__():
            super().wait(self.__signal__ if self.__signal__ else None)
            # Run tasks
            for t in self.__tasks__:
                if t.done(): 
                    continue
                self.__caller__(t.run, self.__robot__)

            # Run the active state
            if self.__active_state__.done():
                self.switch(self.__default__)
            self.__caller__(self.__active_state__.run, self.__robot__)

            # Flush the event queue
            with self:
                while len(Driver.Events.__queue__):
                    e = Driver.Events.__queue__.pop()
                    if not e.type.id in self.__events__.keys():
                        continue
                    e.robot = self.__robot__
                    e.origin = self.__active_state__
                    for f in self.__events__[e.type.id]:
                        self.__caller__(f, e)

                    for val in Driver.Waiters.__queue__:
                        t, w = val
                        if t.id != e.type.id:
                            continue
                        Driver.Waiters.__queue__.remove(val)
                        Waitable.wake(w)

            sleep(self.__cycle__)
                
    def states(self):
        """
        Returns the known states as a tuple, where the 1st element contains the names of the states, and the 2nd element contains the actual states.
        """
        return (tuple(self.__states__.keys()), tuple(self.__states__.values()))
                
    def default(self, id: object):
        """
        Sets the passed state as the default state. If the driver is started, this is a no-op.

        **Argument(s)**
        * state: [State](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-statetask) - State to set as default.
        """
        if self.__thread__:
            return
        self.__default__ = id

    def add(self, runable: Task, default=False):
        """
        Adds a runable to the statedriver. If the driver is started, this is a no-op.
        
        **Argument(s)**
        * runable: [Task](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-statetask#class-statetask) - Task or state to add.
        * default: bool - If true and runable is a state, it'll be set as default.
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
        Switches to the state with the given identifier.
        
        **Argument(s)**
        * id: object - Unique identifier for the state. The object must be hashable.
        """
        if self.__active_state__ and self.__active_state__.id == id:
            return
        if not id in self.__states__.keys():
            return print("[LOG] The state \"{0}\" has not been added to driver {1}.".format(id, self))
        with self as lock:
            lock.notify_all()
            self.__active_state__.cancel()
            self.__active_state__ = self.__states__[id]
            self.__active_state__.reset()
        print("[LOG] Switched to state {0}.".format(self.__active_state__))

    def register(self, type: EventType, handler: Callable[[Event], None]):
        """
        Registers a handler to the given event-type identifier.

        **Argument(s)**
        * type: [EventType](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-eventtype) - Event-type to register to.
        * handler: ([Event](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-event)) -> None - Event handler.
        """
        with self.__lock__:
            if handler in self.__events__.setdefault(type.id, []):
                return
            self.__events__[type.id].append(handler)

    def unregister(self, type: EventType, handler: Callable[[Event], None]):
        """
        Unregister a handler to an event-type.

        **Argument(s)**
        * type: [EventType](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-eventtype) - Event-type to unregister from.
        * handler: ([Event](https://github.com/Hjalte01/REX/blob/main/statedriver/README.md#class-event)) -> None - Event handler.
        """
        with self.__lock__:
            if not (type in self.__events__.keys()):
                return
            self.__events__[type.id] = list(filter(lambda f: f is not handler, self.__events__[type.id]))

    def start(self):
        """
        Starts the driver. If the driver is already started, this is a no-op.
        """
        if self.__thread__:
            return
        if not self.__default__:
            return print("[LOG] No default state for driver {0}. Skipping start.".format(self))
        print("[LOG] Starting driver {0}.".format(self))
        self.__active_state__ = self.__states__[self.__default__]
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
            self.__active_state__.cancel()
            self.__alive__ = False
            self.wake()
            self.__thread__.join(3*self.__cycle__)
            self.__thread__ = None

    def wait(self, signal=None):
        with self:
            self.__signal__ = signal
            self.__wait__ = True

    def wait_for(self, _: EventType):
        """
        Driver is responsible for executing events, which it can't if it is waiting for an event, so this is a no-op.
        """
        return
