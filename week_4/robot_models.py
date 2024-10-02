import numpy as np

# class RobotModel:
#     def __init__(self, ctrl_range) -> None:
#         self.ctrl_range = ctrl_range  # The range of control inputs available for the robot
    
#     def forward_dyn(self, x, u, T):
#         path = [x]
#         u_sum = np.sum(u, axis=0)
#         # dist = np.linalg.norm(u_sum - x)
#         theta = np.arctan2(u_sum[0]-x[0], u_sum[1]-x[1]) * 180 / np.pi
#         for i in range(T):
#             if (i == 0):
#                 path[-1][2] = theta
#                 x_new = path[-1] + u_sum/T
#                 continue
#             x_new = path[-1] + u_sum/T  # u is velocity command here
#             path[-1][2] = 0
#             path.append(x_new)

#         # rotate the robot theta degrees
#         # move dist
        
#         return path[1:]

#     def inverse_dyn(self, x, x_goal, T):
#         dir = (x_goal - x) / np.linalg.norm(x_goal - x)
#         u = np.array([dir * self.ctrl_range[1] for _ in range(T)])
#         return self.forward_dyn(x, u, T)

class RobotModel:
    def __init__(self, ctrl_range) -> None:
        self.ctrl_range = ctrl_range  # The range of control inputs available for the robot
    
    def forward_dyn(self, x, u, T):
        path = [x]
        u_sum = np.sum(u, axis=0)
        
        theta = np.arctan2(u_sum[1], u_sum[0])  # Calculate the heading angle
        print(f"Calculated theta: {theta * 180 / np.pi:.2f} degrees")

        for i in range(T):
            # Update theta based on u
            theta = np.arctan2(u[i][1], u[i][0])

            # Update the position x, y based on the control input (v, omega)
            x_new = path[-1].copy()
            x_new[0] += u[i][0] * np.cos(theta) 
            x_new[1] += u[i][0] * np.sin(theta) 
            x_new[2] = theta

            path.append(x_new)

        print(f"Generated path: {path}")
        return path[1:]

    def inverse_dyn(self, x, x_goal, T):
        """
        Inverse dynamics to compute control inputs to drive from x to x_goal.
        """
        # x = np.array(x)
        # x_goal = np.array(x_goal)
        dir = (x_goal - x) / np.linalg.norm(x_goal - x)
        u = np.array([dir * self.ctrl_range[1] for _ in range(T)])

        print(f"Control inputs (u): {u}")
        return self.forward_dyn(x, u, T)


# Point mass model (from the original code)
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
