from cv2 import imwrite
from numpy import savez
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
        if key == 'q':
            robot.stop()
            break
        elif key == 's':
            robot.stop()
        elif key == 'p':
            imwrite("temp.png", robot.capture())
        elif key == 'c':
            robot.start()
            robot.switch(CalibrateState.ID)

            print("\tStarted callibration ({0} passes).".format(passes))
            for _ in range(passes):
                robot.wait_for(CalibrateEvent.Type.PASS_COMPLETE)
                input("Pass complete. Press any key for next pass.")
            print("Calibration complete.")
            
    exit(0)

if __name__ == "__main__":
    main()
