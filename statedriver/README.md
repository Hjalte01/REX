## Statedriver - First draft
A first try to implement a statedriver for the robot. The statedriver is a structure and should consist of the following:
- start
- stop
- add
- switch
- register

The add method should register states for the statedriver. States are structures and should consist of the following methods:
- run
- done
- fire
- queue

done should be called in the statedriver loop, followed by a call to run if done is false, else it'll revert the statedriver to its default state.
queue should return a states event queue and should be flushed by the statedriver. Standard events should carry data (Py-object) and custom ones should carry members.
