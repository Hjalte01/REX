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

    def __init__(self, id, **kwords: str):
        super().__init__(id, **kwords)
        if len(kwords):
            self.cam_matrix     = kwords["arg0"]
            self.dist_coeffs    = kwords["arg1"]

class CalibrateState(State):
    ID = "robot-state-calibration"

    def __init__(self, x: int, grid: Tuple[int, int], gap: int, passes = 4):
        super().__init__(CalibrateState.ID)
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
        corners, ids, _ = aruco.detectMarkers(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), robot.aruco_dict)

        if ids is None:
            self.__mode__ &= 0xE # Turn off detect bit
        else:
            self.__mode__ |= 0x1 # Turn on detect bit
            self.__all_corners__ = np.append(self.__all_corners__, corners)
            self.__all_ids__ = np.append(self.__all_ids__, ids)
            self.__all_counts__ = np.append(self.__all_counts__, [len(ids)])

        if self.__mode__ == 0x1:
            self.__mode__ |= 0x2 # turn on left bit
        elif self.__mode__ == 0x2:
            self.__mode__ |= 0x4 # turn on right bit

        if self.__mode__ == 0x6:
            self.__passes__ -= 1
            self.__mode__ = 0x0
            self.fire(CalibrateEvent(CalibrateEvent.Type.PASS_COMPLETE))
            robot.stop()
        elif self.__mode__  == 0x4:
            robot.go_diff(40, 40, 0, 1) # pan right
        else:
            robot.go_diff(40, 40, 1, 0) # pan left

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
            CalibrateEvent.Type.CALIBRATION_COMPLETE, arg0=cam_matrix, arg1=dist_coeffs)
        )
