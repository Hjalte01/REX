
import numpy as np
class Cell(object):
    
    def __init__(self, x, y, flag = False):
        super(Cell, self).__init__()
        self.x = int(x)
        self.y = int(y)
        self.occupied = flag
        self.parent = None
        
    
    
class Pos(object):

    def __init__(self, real_length, real_angel):
        self.real_length = real_length
        self.real_angel = real_angel


class Grid(object):

    def __init__(self, cell_size, grid_size = 20):
        super(Grid, self).__init__()
        self.cell_size = cell_size
        self.grid_size = grid_size
        self.grid = self.__generate__()
        self.obstacles = []

    
    def add_obstacle(self, robot_cell, obstacle_pos):
        kate_1 = obstacle_pos.real_length * np.cos(obstacle_pos.real_angel)
        kate_2 = obstacle_pos.real_length * np.sin(obstacle_pos.real_angel)

        x = kate_1 // self.cell_size
        y = kate_2 // self.cell_size

        self.grid[robot_cell.x+x][robot_cell.y+y].occupied = True
        self.obstacles.append(self.grid[robot_cell.x+x][robot_cell.y+y])

    def update_grid(self):

        for obstacle in self.obstacles:
            self.grid[obstacle.x][obstacle.y].occupied = True

    def __generate__(self):
        # Generates the grid
        result = np.full((self.grid_size, self.grid_size), Cell(0, 0))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                result[i][j] = Cell(i, j)
        return result
