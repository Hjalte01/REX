from cv2 import imwrite
from numpy import savez
from statefulrobot import StatefulRobot
from driver import State
from states.calibrate import CalibrateState, CalibrateEvent

def handleCalibrationPass(e: CalibrateEvent):
    print("Pass complete. Press any key for next pass.")

def handleCalibrationComplete(e: CalibrateEvent):
    print("Calibration complete.")
    savez("config.npz", cam_matrix=e.cam_matrix, dist_coeffs=e.dist_coeffs)

class DefaultState(State):
    def run(self, robot):
        pass

def main():
    robot = StatefulRobot()
    robot.add(DefaultState("default"), True)
    robot.add(CalibrateState(37.02, (3, 3), 1.85))
    robot.register(CalibrateEvent.Type.CALIBRATION_COMPLETE, handleCalibrationComplete)
    robot.register(CalibrateEvent.Type.PASS_COMPLETE, handleCalibrationPass)
    
    print("Robot CLI - usage:\n\tPress 'c' to calibrate.\n\tPress 'p' to capture a picture.\n\tPress 's' to stop.\n\tPress 'q' to quit.")
    while True:
        key = input().strip().lower()[0]

        if key == 'q':
            robot.stop_driver()
            robot.stop()
            break
        elif key == 's':
            robot.stop()
        elif key == 'p':
            imwrite("temp.png", robot.capture())
        elif key == 'c':
            print("\tStarted callibration (4 passes).")
            robot.start_driver()
            robot.switch("robot-state-calibrate")
            
            

if __name__ == "__main__":
    main()
