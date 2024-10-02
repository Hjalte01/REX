
from grid import Grid, Cell

import numpy as np
import math
import matplotlib.pyplot as plt



class RRT(object):

    def __init__(self, grid, robot_size = 0.45):

        self.grid = grid
        self.final_route = []
        self.robot_size = robot_size
        self.init_cell = Cell(robot_size/2,robot_size/2, True)
        self.new_cell = self.init
        self.final_cell = Cell(robot_size-2, robot_size-2)
        self.rnd_cell = self.random_cell()



    def collide(self, cell):
        # check if a cell collides with grid

        return self.grid[cell.x][cell.y].occupied
        
    def random_cell(self):
        # get a random cell

        x = np.random(0, self.grid.grid_x)
        y = np.random(0, self.grid.grid_x)
        return Cell(x, y)
    
    def collision_rnd_cell(self):
        for obstacle in self.grid.obstacles:
            length = np.linalg.norm(obstacle.x-self.rnd_cell.x, obstacle.y-self.rnd_cell.y)
            if length < self.robot_size:
                return False
        return True


    def rnd_sort_distance(self, cell):
        # sort the list of cells in the following function with distance to rnd_cell

        return np.linalg.norm(cell.x - self.rnd_cell.x, cell.y - self.rnd_cell.y)
    def collision_best_options(self):
        # get a list of the best options to try for the new cell in path
        result = []
        for i in range(-1,1):
            for j in range(-1,1):
                x_index = self.new_cell.x + i
                y_index = self.new_cell.y + j
                if x_index < 0 or x_index > self.grid.grid_x: continue
                if y_index < 0 or x_index > self.grid.grid_y: continue
                result.append(Cell(x_index, y_index))
        return result.sort(key=self.rnd_sort_distance)                

    def nearest_cells(self):
        # Returns the nearest cell to the given cell
        min_cell = 2 * self.grid.grid_x ** 2
        min_index = 0
        for index, cell in enumerate(self.final_route):
            length = np.linalg.norm(self.rnd_cell.x - cell.x, self.rnd_cell.y - cell.y)
            if length < min_cell:
                min_cell = length
                min_index = index
        return min_index, self.final_route[min_index]                

    def new_point_generate(self):
        
        cell_opt = self.collision_best_options()
        for cell in cell_opt:
            if self.collide(cell): continue
            self.new_cell.occupied = False
            self.new_cell = cell
            self.new_cell.occupied = True
            break


    def draw_graph(self):
        plt.clf()

        if self.rnd_cell is not None:
            plt.plot(self.rnd_cell.x, self.rnd_cell.y, "^k")
        
        self.map.draw_map()





