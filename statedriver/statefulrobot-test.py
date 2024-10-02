from dataclasses import dataclass
from time import sleep
from statefulrobot import StatefulRobot, Event, Task, State

class BackgroundEvent(Event):
        @dataclass
        class Type:
            BACKGROUND = "robot-event-background"

        def __init__(self, id, **kwords: str):
            super().__init__(id, **kwords)
            self.msg = kwords["msg"]         

class BackgroundTask(Task):
    def run(self, _):
        print("\t\tHello from background")

class FooState(State):
    def run(self, _):
        print("\t\tHello from {0}".format(self))

class BarEvent(Event):
    @dataclass
    class Type:
        BAR = "robot-event-bar"

    def __init__(self, id, **kwords: str):
        super().__init__(id, **kwords)
        self.msg = kwords["msg"]

class BarState(State):
    def run(self, _):
        print("\t\tHello from {0}".format(self))
        sleep(2)
        self.fire(BarEvent(BarEvent.Type.BAR, msg="\t\tHello from {0} & {1}"))
        self.done(True)

def handleBar(e: BarEvent):
    print(e.msg.format(e.origin, e))

if __name__ == "__main__":
    test = StatefulRobot()
    test.add(BackgroundTask())
    test.add(FooState("foo"), True)
    test.add(BarState("bar"))
    test.register(BarEvent.Type.BAR, handleBar)
    test.start()
    sleep(0.05)

    # Switch state
    test.switch("bar")
    assert(test.driver.__active_state__.id == "bar")

    # Halt main thread and wait for event
    test.wait_for(BarEvent.Type.BAR)

    # Halt driver and wait for user input
    test.wait(test.driver)
    input("Press any key")
    test.wake(test.driver)
    sleep(0.05)
    
    # Adding a state while enviromentthe driver is running is no-op
    test.add(State("baz"))
    assert(len(test.driver) == 2)
    test.stop()
    
    # Adding the same state is no-op  
    test.add(State("foo"))
    assert(len(test.driver) == 2)

    # Switching to non-existing state gives warning
    test.switch("nope")
