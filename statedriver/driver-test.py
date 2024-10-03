from time import sleep
from driver import EventType, Event, Task, State, Driver
from robot import Robot

class BackgroundTask(Task):
    def run(self, _):
        print("\t\tHello from background")

class FooState(State):
    def run(self, _):
        print("\t\tHello from {0}".format(self))

class BarEvent(Event):
    EVENT_BAR = EventType("bar")
    msg: str

class BarState(State):
    def run(self, _):
        print("\t\tHello from {0}".format(self))
        sleep(2)
        self.fire(BarEvent(BarEvent.EVENT_BAR, msg="\t\tHello from {0} fired from {1}"))
        self.done(True)

class ErrState(State):
    def run(self, _: Robot):
        x = []
        x[1]

def handleBar(e: BarEvent):
    print(e.msg.format(e, e.origin))

if __name__ == "__main__":
    d = Driver(None, 1000)
    d.add(BackgroundTask())
    d.add(FooState("foo"), True)
    d.add(BarState("bar"))
    d.add(ErrState("err"))
    d.register(BarEvent.EVENT_BAR, handleBar)
    d.start()
    sleep(0.5)

    # Switch state
    d.switch("bar")
    assert(d.__active_state__.id == "bar")

    # Halt main thread and wait for event
    Task().wait_for(BarEvent.EVENT_BAR)

    # Halt driver
    d.wait()
    sleep(2)
    d.wake()
    sleep(0.5)

    # Done states switch to default state
    assert(d.__active_state__.id == "foo")
    assert(len(d.Events.__queue__) == 0)
    assert(len(d.Waiters.__queue__) == 0)

    # Exceptions switch to default state
    d.switch("err")
    sleep(0.5)
    assert(d.__active_state__.id == "foo")
    
    # Adding a state while the driver is running is no-op
    d.add(State("baz"))
    assert(len(d) == 3)
    
    # Adding the same state is no-op  
    d.stop()
    d.add(State("foo"))
    assert(len(d) == 3)

    # Adding the same task is no-op  
    t = Task()
    d.add(t)
    d.add(t)
    assert(len(d.__tasks__) == 2)

    # Switching to non-existing state gives warning
    d.switch("nope")
