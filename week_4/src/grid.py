
import numpy as np
class Cell(object):
    
    def __init__(self, x, y, flag = False):
        super(Cell, self).__init__()
        self.x = int(x)
        self.y = int(y)
        self.occupied = flag
        self.parent = None

class Zone(Cell):

    def __init__(self, x, y, flag = False):
        super(Cell, self).__init__(x, y, flag)
        self.cells = [[Cell(0, 0)]]
        
    def difuse(self, new_len):
        n = len(self.cells)
        # sanity check to avoid multiple difusions on the same cell
        if n >= new_len: return

        # difuse the cells in the zone
        for i in range(n, new_len):
            if i >= n:
                self.cells.append([Cell(i, 0)])
            for j in range(n):
                self.cells[i].append(Cell(i, j))
        
    
class Pos(object):

    def __init__(self, real_length, real_angel):
        self.real_length = real_length
        self.real_angel = real_angel


class Grid(object):

    def __init__(self, zone_size, grid_size = 8):
        super(Grid, self).__init__()
        self.zone_size = zone_size
        self.grid_size = grid_size
        self.grid = []
        self.obstacles = []
        self.obstacle_radius = 200
        self.__generate__()

    
    def add_obstacle(self, robot_cell, obstacle_pos):
        kate_1 = (obstacle_pos.real_length+self.obstacle_radius) * np.cos(obstacle_pos.real_angel)
        kate_2 = (obstacle_pos.real_length+self.obstacle_radius) * np.sin(obstacle_pos.real_angel)
        
        x = int(kate_1 // self.zone_size)
        y = int(kate_2 // self.zone_size)

        for i in range(max(0, x-2), min(self.grid_size, x+2)):
            for j in range(max(0, y-2), min(self.grid_size, y+2)):
                self.grid[i][j].occupied = True
                self.obstacles.append(self.grid[i][j])




        print("x: ", x, "y: ", y)
        print("r-x: ", robot_cell.x, "r-y: ", robot_cell.y)

        # x_min = np.floor(x-self.obstacle_radius)
        # x_max = np.ceil(x+self.obstacle_radius)
        # y_min = np.floor(y-self.obstacle_radius)
        # y_max = np.ceil(y+self.obstacle_radius)
        # print(x_min, x_max, y_min, y_max)
        # for i in range(int(x_min), int(x_max)+1):
        #     for j in range(int(y_min), int(y_max)+1):
        #         print("obj -> x: ", robot_cell.x+i, "y: ", robot_cell.x+j)
        #         if robot_cell.x+i < 0 or robot_cell.x+i >= self.grid_size: continue
        #         if robot_cell.y+j < 0 or robot_cell.y+j >= self.grid_size: continue
        #         self.grid[robot_cell.x+i][robot_cell.y+j].occupied = True
        #         self.obstacles.append(self.grid[robot_cell.x+i][robot_cell.y+j])




    def update_grid(self):

        for obstacle in self.obstacles:
            self.grid[obstacle.x][obstacle.y].occupied = True

    def __generate__(self):
        # Generates the grid
        for i in range(self.grid_size):
            self.grid.append([])
            for j in range(self.grid_size):
                self.grid[i].append(Zone(i, j))

