
import numpy as np
class Cell(object):
    
    def __init__(self, x, y, flag = False):
        super(Cell, self).__init__()
        self.x = x
        self.y = y
        self.occupied = flag
        self.parent = None
        
    
    
class Pos(object):

    def __init__(self, real_length, real_angel):
        self.real_length = real_length
        self.real_angel = real_angel


class Grid(object):

    def __init__(self, cell_x, grid_x = 20):
        super(Grid, self).__init__()
        self.cell_x = cell_x
        self.grid_x = grid_x
        self.grid = self.__generate__()
        self.obstacles = []

    
    def add_obstacle(self, robot_cell, obstacle_pos):
        kate_1 = obstacle_pos.real_length * np.cos(obstacle_pos.real_angel)
        kate_2 = obstacle_pos.real_length * np.sin(obstacle_pos.real_angel)

        x = kate_1 // self.cell_x
        y = kate_2 // self.cell_x


        self.obstacles.append(Cell(robot_cell.x+x, robot_cell.y+y, True))


    def __generate__(self):
        # Generates the grid
        result = []
        for i in range(self.cell_x):
            for j in range(self.cell_x):
                cell = Cell(i, j)
                result.append(cell)
        return result
