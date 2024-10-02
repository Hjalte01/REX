from cv2 import imwrite
from numpy import savez
from statefulrobot import StatefulRobot, State
from states.calibrate import CalibrateState, CalibrateEvent
from time import sleep

class DefaultState(State):
    def run(self, _: StatefulRobot):
        pass

class TestState(State):
    def run(self, robot: StatefulRobot):
        robot.go_diff(40, 40, 1, 0)
        sleep(0.1)
        imwrite("tmp.png", robot.capture())
        self.done(True)

def handleCalibrationComplete(e: CalibrateEvent):
    savez("config.npz", cam_matrix=e.cam_matrix, dist_coeffs=e.dist_coeffs)

class DefaultState(State):
    def run(self, robot):
        pass

def main():
    passes = 1
    robot = StatefulRobot(StatefulRobot.CamStategy.PI_CAMERA_REQ)
    robot.add(DefaultState("default"), True)
    robot.add(CalibrateState(0, (5, 5), 0, passes))
    robot.add(TestState("test"))
    robot.register(CalibrateEvent.Type.CALIBRATION_COMPLETE, handleCalibrationComplete)

    print(
        "Robot CLI - usage:"\
        "\n\tPress 'c' to calibrate."\
        "\n\tPress 'p' to capture a picture."\
        "\n\tPress 's' to stop."\
        "\n\tPress 'q' to quit."\
    )
    
    while True:
        key = (input().lower() + "")[0]
        if key == 'q':
            robot.stop()
            sleep(1)
            break
        elif key == 's':
            robot.stop()
        elif key == 'p':
            imwrite("temp.png", robot.capture())
            # robot.capture()
        elif key == 'c':
            robot.start()
            robot.switch(CalibrateState.ID)

            print("\tStarted callibration ({0} passes).".format(passes))
            for _ in range(passes):
                robot.wait_for(CalibrateEvent.Type.PASS_COMPLETE)
                input("Pass complete. Press any key for next pass.")
            print("Calibration complete.")
            robot.driver.stop()
        elif key == 't':
            robot.start()
            robot.switch("test")
            sleep(2)
            robot.driver.stop()

            
    exit(0)

if __name__ == "__main__":
    main()
