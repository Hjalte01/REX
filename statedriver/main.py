from cv2 import imwrite
from numpy import savez
from statefulrobot import StatefulRobot
from states.calibrate import CalibrateState, CalibrateEvent

def handleCalibrationPass(_: CalibrateEvent):
    input("Pass complete. Press any key for next pass.")

def handleCalibrationPass(e: CalibrateEvent):
    print("Calibration complete.")
    savez("config.npz", cam_matrix=e.cam_matrix, dist_coeffs=e.dist_coeffs)

def main():
    states = [CalibrateState(robot, 0, (3, 3), 0)]
    robot = StatefulRobot(StatefulRobot.CamStategy.PI_CAMERA, *states)
    robot.register(CalibrateEvent.Type.CALIBRATION_COMPLETE, handleCalibrationPass)

    print("Robot CLI - usage:\n\tPress 'c' to calibrate.\n\tPress 'p' to capture a picture.\n\tPress 's' to stop.\n\tPress 'q' to quit.")
    while True:
        key = input().strip().lower()[0]
        if key == 'q':
            robot.stop()
            break
        elif key == 's':
            robot.stop()
        elif key == 'p':
            imwrite("temp.png", robot.capture())
        elif key == 'c':
            print("\tStarted callibration (4 passes).")
            robot.switch(states[0].id)
            robot.start()

if __name__ == "__main__":
    main()
