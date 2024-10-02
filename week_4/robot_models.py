import numpy as np

class RobotModel:
    def __init__(self, ctrl_range) -> None:
        self.ctrl_range = ctrl_range  # The range of control inputs available for the robot
    
    def forward_dyn(self, x, u, T):
        path = [x]
        u_sum = np.sum(u, axis=0)
        # dist = np.linalg.norm(u_sum - x)
        x_diff = u_sum - x
        theta = np.arctan2(u_sum[0]-x[0], u_sum[1]-x[1]) * 180 / np.pi
        for i in range(T):
            if (i == 0):
                path[-1][2] = theta
                x_new = path[-1] + u_sum/T
                path.append(x_new)
                continue
            x_new = path[-1] + u_sum/T  # u is velocity command here
            path[-1][2] = 0
            path.append(x_new)

        # rotate the robot theta degrees
        # move dist
        
        return path[1:]

    def inverse_dyn(self, x, x_goal, T):
        x_goal[2] = 0
        x[2] = 0
        dir = (x_goal - x) / np.linalg.norm(x_goal - x)
        u = np.array([dir * self.ctrl_range[1] for _ in range(T)])
        return self.forward_dyn(x, u, T)









class PointMassModel(RobotModel):
    def forward_dyn(self, x, u, T):
        path = [x]
        for i in range(T):
            x_new = path[-1] + u[i]  # u is velocity command here
            path.append(x_new)
        
        return path[1:]

    def inverse_dyn(self, x, x_goal, T):
        dir = (x_goal - x) / np.linalg.norm(x_goal - x)
        u = np.array([dir * self.ctrl_range[1] for _ in range(T)])
        return self.forward_dyn(x, u, T)
