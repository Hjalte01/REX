# Extended Arlo Robot Controller

from time import sleep
from threading import Thread, Condition
from robot import Robot

obstacle_threshold  = 100   # Distance in mm to obstacles before the robot acts.
deviate_tresshold   = 10    # Deviation in motor power in % before correction.
refresh_rate        = 50    # Refresh-rate in ms.

class ExtendedRobot(Robot):
    def __init__(self, port='/dev/ttyACM0'):
        super().__init__(port)

        # Props
        self.alive                  = False
        self.con                    = Condition()
        self.delta: int | None      = None
        self.tasks: list[Thread]    = []

    def __del__(self):
        super().__del__()

        with self.con:
            self.alive = False
        while len(self.tasks):
            self.tasks.pop().join(timeout=1)

    def __watch__(self):
        """
        Must be invoked by a seperate thread.
        """
        measures = [0, 0, 0, 0]

        while self.alive:
            # Update
            for i in range(4):
                measures[i] = self.read_sensor(i)
                if measures[i] < 0:
                    with self.con:
                        self.alive = False
                    return print("[ERR] Error reading sensor {0}".format(i))
                    
            # Evaluate
            flags = [False, False, False, False]
            delta = None
            for i in range(4):
                flags[i] = measures[i] <= obstacle_threshold
            if flags[0]:
                # Obstacle in front. Chose the direction with the greater freedom of movement.
                delta = measures[3] - measures[2]
            elif flags[2] and not flags[3]:
                # Obstacle to the left. 
                delta = measures[3]
            elif flags[3] and not flags[2]:
                # Obstacle to the right. 
                delta = -measures[2]

            self.con.acquire()
            self.delta = delta
            self.con.release()

            sleep(refresh_rate*0.001)
                
    def __go__(self, left_power, right_power):
        """
        Must be invoked by a seperate thread.
        """
        moving = False

        while self.alive:
            self.con.acquire()
            delta = self.delta
            self.con.release()

            if moving:
                if delta != None:
                    if delta < 0:
                        # Turn the robot left.
                        self.go_diff(left_power, right_power, 0, 1)
                        print("[LOG] Turning left") # Delete me
                    else:
                        # Turn the robot right.
                        self.go_diff(left_power, right_power, 1, 0)
                        print("[LOG] Turning right") # Delete me
                    moving = False
                else:
                    pass
                    # Deviation corrections. From the library documentation, go_diff does not use encodes.
                    # As such this properly does not work.
                    # left = int(self.send_command("e0\n"))%144
                    # right = int(self.send_command("e1\n"))%144
                    # if left < right and 1 - left/right > deviate_tresshold:
                    #     left_power *= 1.1
                    #     self.go_diff(left_power, right_power, 1, 1)
                    # elif right > left and 1 - right/left > deviate_tresshold:
                    #     right_power *= 1.1
                    #     self.go_diff(left_power, right_power, 1, 1)
            else:
                if delta == None:
                    self.go_diff(left_power, right_power, 1, 1)
                    moving = True
                    print("[LOG] Going") # Delete me

            sleep(refresh_rate*0.001)

    def go(self, left_power = 40, right_power = 40):
        """
        Starts the robot with the given motor powers and the heading it's facing.
        """
        self.alive = True
        self.delta = None
        self.tasks.append(Thread(target=self.__go__, args=(left_power, right_power)))
        self.tasks.append(Thread(target=self.__watch__))
        for task in self.tasks:
            # Making the threads daemons might be better for testing purposes,
            # such that they die with the main thread on SIG-TERM or similar.
            # task.daemon = True
            task.start()

    def stop_driver(self):
        """
        Stops the robot and terminates running threads.
        """
        super().stop_driver()

        with self.con:
            self.alive = False
        while len(self.tasks):
            self.tasks.pop().join(timeout=1)
