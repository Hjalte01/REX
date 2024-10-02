from cv2 import imwrite
from numpy import savez
<<<<<<< HEAD
from statefulrobot import StatefulRobot
from states.calibrate import CalibrateState, CalibrateEvent

def handleCalibrationPass(_: CalibrateEvent):
    input("Pass complete. Press any key for next pass.")

def handleCalibrationComplete(e: CalibrateEvent):
    print("Calibration complete.")
    savez("config.npz", cam_matrix=e.cam_matrix, dist_coeffs=e.dist_coeffs)

def main():
    states = [CalibrateState(robot, 0, (3, 3), 0)]
    robot = StatefulRobot(StatefulRobot.CamStategy.PI_CAMERA, *states)
    robot.register(CalibrateEvent.Type.CALIBRATION_COMPLETE, handleCalibrationComplete)
    robot.register(CalibrateEvent.Type.PASS_COMPLETE, handleCalibrationPass)

    print("Robot CLI - usage:\n\tPress 'c' to calibrate.\n\tPress 'p' to capture a picture.\n\tPress 's' to stop.\n\tPress 'q' to quit.")
    while True:
        key = input().strip().lower()[0]
=======
from robot import Robot
from statefulrobot import StatefulRobot, State
from states.calibrate import CalibrateState, CalibrateEvent

class DefaultState(State):
    def run(self, _: Robot):
        pass

def handleCalibrationComplete(e: CalibrateEvent):
    savez("config.npz", cam_matrix=e.cam_matrix, dist_coeffs=e.dist_coeffs)

def main():
    passes = 1
    robot = StatefulRobot(StatefulRobot.CamStategy.PI_CAMERA)
    robot.add(DefaultState("default"), True)
    robot.add(CalibrateState(0, (5, 5), 0, passes))
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
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f
        if key == 'q':
            robot.stop()
            break
        elif key == 's':
            robot.stop()
        elif key == 'p':
            imwrite("temp.png", robot.capture())
        elif key == 'c':
<<<<<<< HEAD
            print("\tStarted callibration (4 passes).")
            robot.switch(states[0].id)
            robot.start()
=======
            robot.start()
            robot.switch(CalibrateState.ID)

            print("\tStarted callibration ({0} passes).".format(passes))
            for _ in range(passes):
                robot.wait_for(CalibrateEvent.Type.PASS_COMPLETE)
                input("Pass complete. Press any key for next pass.")
            print("Calibration complete.")
            
    exit(0)
>>>>>>> d191327ecf6b86a5884c222afb8c67fbe4ba831f

if __name__ == "__main__":
    main()
