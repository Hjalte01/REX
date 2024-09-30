from time import sleep
import cv2, cv2.aruco as aruco  # type: ignore
import numpy as np
from typing import Tuple
from dataclasses import dataclass
from statedriver.statefulrobot import State, Event, StatefulRobot

class CalibrateEvent(Event):
    @dataclass
    class Type:
        PASS_COMPLETE           = "robot-event-pass-complete"
        CALIBRATION_COMPLETE    = "robot-event-calibration-complete"

    def __init__(self, id, robot: StatefulRobot, state: State, **kwords: str):
        super().__init__(id, robot, **kwords)
        self.state = state
        self.cam_matrix     = kwords["arg0"]
        self.dist_coeffs    = kwords["arg1"]

class CalibrateState(State):
    def __init__(self, x: float, grid: Tuple[int, int], gap: float, passes = 4):
        super().__init__("robot-state-calibrate")
        self.__done__           = False
        self.__x__              = x*0.001
        self.__grid__           = grid
        self.__gap__            = gap*0.001
        self.__passes__         = passes
        self.__mode__           = 0x0
        self.__all_corners__    = np.empty((0, 1, 4, 2), np.float32)
        self.__all_ids__        = np.empty((0, 1), np.int32)
        self.__all_counts__     = np.empty((0, 1), np.int32)
    
    def run(self, robot: StatefulRobot):
        robot.stop()
        frame = robot.capture()
        sleep(4)
        corners, ids, _ = aruco.detectMarkers(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), robot.aruco_dict)
        cv2.imwrite("temp.png", frame)

        if ids is None:
            self.__mode__ &= 0xE # Turn off detect bit
        else:
            self.__mode__ |= 0x1 # Turn on detect bit
            self.__all_corners__ = np.append(self.__all_corners__, corners, axis=0)
            self.__all_ids__ = np.append(self.__all_ids__, ids, axis=0)
            self.__all_counts__ = np.append(self.__all_counts__, [len(ids)])

        if self.__mode__ == 0x1:
            self.__mode__ |= 0x2
        elif self.__mode__ == 0x2:
            self.__mode__ = 0x4
        elif self.__mode__ == 0x5:
            self.__mode__ |= 0x2
        
        if self.__mode__ == 0x2 | 0x4:
            self.__passes__ -= 1
            self.__mode__ = 0x0
            self.fire(CalibrateEvent(CalibrateEvent.Type.PASS_COMPLETE, robot, self, arg0="", arg1=""))
            robot.stop()
            print("stopping")
        elif self.__mode__ < 0x4:
            print("left", self.__mode__, "" if ids is None else ", ids {0}".format(len(ids)))
            robot.go_diff(40, 40, 0, 1)
        else:
            print("right", self.__mode__,  "" if ids is None else ", ids {0}".format(len(ids)))
            robot.go_diff(40, 40, 1, 0)

        if not self.done(self.__passes__ <= 0):
            return
        
        _, cam_matrix, dist_coeffs, _, _ = aruco.calibrateCameraAruco(
            self.__all_corners__,
            self.__all_ids__,
            self.__all_counts__,
            aruco.GridBoard.create(
                self.__grid__[0], self.__grid__[1], self.__x__, self.__gap__, robot.aruco_dict),
            frame.shape[:-1],
            None,
            None
        )
        self.fire(CalibrateEvent(
            CalibrateEvent.Type.CALIBRATION_COMPLETE, robot, self, arg0=cam_matrix, arg1=dist_coeffs)
        )
