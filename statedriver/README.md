# Documentation
* driver
    * [class EventType](#class-eventtype)
    * [class Event](#class-event)
    * [class Waitable](#class-waitable)
    * [class Task(Waitable)](#class-taskwaitable)
    * [class State(Task)](#class-statetask)
    * [class Driver(Waitable)](#class-driverwaitable)
* statefulrobot
    * [class StatefulRobot(Robot, Driver)](#class-statefulrobotrobot-waitable)

## class EventType
### EventType(id) -> EventType
Constructor.
| Arg | Type | Description | Default |
| - | - | - | -: | 
| id | object | Unique identifier for the event-type. The object must be hashable |

## class Event
Event objects are passed to event handlers.
### Event(type, **kwords) -> Event
Constructor. If kwords are supplied, the values are made available as a member with the keys as accessors, i.e.:
```
event = Event(EventType("foo"), foo="foo", bar="bar")
print(event.foo, event.bar)
```

| Arg | Type | Description | Default |
| - | - | - | -: | 
| type | [EventType](#class-eventtype) | Type of the event |
| kwords | **dict | Optional key-value pairs | None

## class Waitable
A Waitable is a type that can run custom logic after a (optional) given wait.
### Waitable() -> Waitable
Constructor.

### waitable.fire(event) -> None
Fires the passed event. If any event handlers are listening to the events event-type, those handlers will be called.
| Arg | Type | Description | Default |
| - | - | - | -: | 
| event | [Event](#class-event) | The event to fire |

### waitable.wait(signal) -> None
Awaits execution untill signaled by [waitable.wake](#waitablewake---none) or the passed signal.
| Arg | Type | Description | Default |
| - | - | - | -: | 
| signal | () -> bool | Wakes the  waitable when the signal function returns true.	 | None

### waitable.wait_for(type) -> None
Awaits execution untill event with the passed event-type fires.
| Arg | Type | Description | Default |
| - | - | - | -: | 
| type | [EventType](#class-eventtype) | Type of the event |

### waitable.wake() -> None
Signals the waitable to wake and resume execution.

### waitable.cancel() -> None
Alias for [waitable.wake](#waitablewake---none).

### waitable.reset() -> None
Resets the waitable.

## class Task(Waitable)
A Task represents a recurring task, that is run every [Driver](#class-driverwaitable) cycle regardless of state. 

### Task() -> Task
Constructor.

### task.done(flag) -> bool
Signals the task to end. If it's waiting, it'll be woken.
| Arg | Type | Description | Default |
| - | - | - | -: | 
| flag | bool | If true, ends the task | False

### task.run(robot) -> None
Virtual method that must be overriden by classes inheriting from Task. It'll get passed a Robot object.

| Arg | Type | Description | Default |
| - | - | - | -: | 
| robot | Robot | Arlo robot | 

### [task.fire(event) -> None](#waitablefireevent---none)
### [task.wait(signal) -> None](#waitablewaitsignal---none)
### [task.wait_for(type) -> None](#waitablewait_fortype---none)
### [task.wake() -> None](#waitablewake---none)
### [task.cancel() -> None](#waitablecancel---none)
### [task.reset() -> None](#waitablereset---none)


## class State(Task)
A state represents a unique task. Only one state is running at any given time.
### State(id) -> State
Constructor.

| Arg | Type | Description | Default |
| - | - | - | -: | 
| id | object | Unique identifier for the state. The object must be hashable. |

### [state.done(flag) -> bool](#taskdoneflag---bool)
### [state.run(robot) -> None](#taskrunrobot---none)
### [state.fire(event) -> None](#waitablefireevent---none)
### [state.wait(signal) -> None](#waitablewaitsignal---none)
### [state.wait_for(type) -> None](#waitablewait_fortype---none)
### [state.wake() -> None](#waitablewake---none)
### [state.cancel() -> None](#waitablecancel---none)
### [state.reset() -> None](#waitablereset---none)

## class Driver(Waitable)
A driver handles execution of runables(Task or State objects). Runables are executed sequentially in parallel with the main thread and in a threadsafe context. The order of execution is **tasks -> state -> event handlers -> wake waitables**. Exceptions from tasks, states and event handlers are caught, except for exceptions in the default state, which will kill the thread gracefully. 

### Driver(robot, tick, default_state, states) -> Driver
Constructor.

| Arg | Type | Description | Default |
| - | - | - | -: | 
| robot | Robot | Arlo robot. | 
| tick | int | Driver cycle tick in ms. | 100
| default_state | [State](#class-statetask) | Default driver state. | None
| states | List<[State](#class-statetask)> | Driver states. | None

### driver.states() -> Tuple<Tuple<str\>, Tuple<[State](#class-statetask)>>
Returns the known states as a tuple, where the 1st element contains the names of the states, and the 2nd element contains the actual states.

### driver.default(state) -> None
Sets the passed state as the default state. If the driver is started, this is a no-op.

| Arg | Type | Description | Default |
| - | - | - | -: | 
| state | [State](#class-statetask) | State to set as default | None

### driver.add(runable, default) -> None
Adds a runable to the statedriver. If the driver is started, this is a no-op.

| Arg | Type | Description | Default |
| - | - | - | -: | 
| runable | Task \| State | Task or state to add | 
| default | bool | If true and runable is a state, it'll be set as default state | False

### driver.switch(id) -> None
Switches to the state with the given identifier.

| Arg | Type | Description | Default |
| - | - | - | -: | 
| id | object | Unique identifier for the state. The object must be hashable |

### driver.register(type, handler) -> None
Registers a handler to the given event-type identifier.

| Arg | Type | Description | Default |
| - | - | - | -: | 
| id | [EventType](#class-eventtype) | Event-type to register to. |
| handler | ([Event](#class-event)) -> None | The event handler.

### driver.unregister(type, handler) -> None
Unregisters a handler to the given event-type identifier.

| Arg | Type | Description | Default |
| - | - | - | -: | 
| id | [EventType](#class-eventtype) | Event-type to unregister from. |
| handler | ([Event](#class-event)) -> None | The event handler.

### driver.start() -> None
Starts the driver. If the driver is already started, this is a no-op.

### driver.stop() -> None
Stops the driver. If the driver is already started, this is a no-op.

### [driver.fire(event) -> None](#waitablefireevent---none)
### [driver.wait(signal) -> None](#waitablewaitsignal---none)
### [driver.wait_for(type) -> None](#waitablewait_fortype---none)
Driver is responsible for executing events, which it can't if it is waiting for an event, so this is a no-op.
### [driver.wake() -> None](#waitablewake---none)
### [driver.cancel() -> None](#waitablecancel---none)
### [driver.reset() -> None](#waitablereset---none)

## class StatefulRobot(Robot, Waitable)
Container class for various robot important objects.

### StatefulRobot(img_size, fps, port) -> StatefulRobot
Constructor.

| Arg | Type | Description | Default |
| - | - | - | -: | 
| img_size | Tuple[int, int] | Image size (width x height) | (1280, 720)
| fps | int | Frames per second. | 30
| port | str | Serial port to bind | "/dev/ttyACM0"

### statefulrobot.start() -> None
Starts the robot.

### statefulrobot.stop() -> None
Stops the robot. 

### [statefulrobot.default(state) -> None](#driverdefaultstate---none)
### [statefulrobot.add(state, default) -> None](#driveraddrunable-default---none)
### [statefulrobot.switch(id) -> None](#driverswitchid---none)
### [statefulrobot.register(type, handler) -> None](#driverregistertype-handler---none)
### [statefulrobot.unregister(type, handler) -> None](#driverunregistertype-handler---none)
### [statefulrobot.fire(event) -> None](#waitablefireevent---none)
### [statefulrobot.wait(signal) -> None](#waitablewaitsignal---none)
### [statefulrobot.wait_for(type) -> None](#waitablewait_fortype---none)
### [statefulrobot.wake() -> None](#waitablewake---none)
### [statefulrobot.cancel() -> None](#waitablecancel---none)
### [statefulrobot.reset() -> None](#waitablereset---none)
