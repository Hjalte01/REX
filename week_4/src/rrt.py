
from grid import Grid, Cell

import numpy as np
import math
import matplotlib.pyplot as plt



class RRT(object):

    def __init__(self, grid = Grid(0.45), robot_size = 0.45):

        self.grid = grid
        self.final_route = []
        self.robot_size = robot_size
        self.step_size = robot_size
        self.init_cell = Cell(robot_size/2,robot_size/2, True)
        self.new_cell = self.init_cell
        self.final_cell = Cell(robot_size-2, robot_size-2)
        self.rnd_cell = self.random_cell()



    def collision_check_point(self, cell):
        # check if a cell collides with grid
        return self.grid[cell.x][cell.y].occupied
        

    def random_cell(self):
        # get a random cell
        x = np.random.randint(0, self.grid.grid_size)
        y = np.random.randint(0, self.grid.grid_size)
        self.rnd_cell = Cell(x, y)
    

    # def collision_rnd_cell(self):
    #     # check for colision from rnd_cell and a 
    #     for obstacle in self.grid.obstacles:
    #         length = np.linalg.norm(obstacle.x-self.rnd_cell.x, obstacle.y-self.rnd_cell.y)
    #         if length < self.robot_size:
    #             return False
    #     return True


    def distance_to_rnd(self, cell):
        # sort the list of cells in the following function with distance to rnd_cell
        return np.linalg.norm(cell.x - self.rnd_cell.x, cell.y - self.rnd_cell.y)
    
    def collision_check_line(self):
        # get a list of the best options to try for the new cell in path
        closest_cell = 0
        min = 2 * self.grid.grid_size ** 2
        for i in range(-1,2):
            for j in range(-1,2):
                if (i == 0 and j == 0): continue
                x_index = self.new_cell.x + i
                y_index = self.new_cell.y + j
                if x_index < 0 or x_index > self.grid.grid_size: continue
                if y_index < 0 or x_index > self.grid.grid_size: continue
                dist = self.distance_to_rnd(Cell(x_index, y_index))
                if (dist < min):
                    closest_cell = Cell(x_index, y_index)
                    min = dist
        collision_bool = self.collision_check_point(closest_cell)
        return collision_bool, closest_cell
    


    def nearest_cell(self):
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
        
        cell_opt = self.collision_check_line()
        for cell in cell_opt:
            if self.collision_check_point(cell): continue
            self.new_cell.occupied = False
            self.new_cell = cell
            self.new_cell.occupied = True
            break

    def connect_to_goal(self):
        np.linalg.norm(self.new_cell.x-self.final_cell.x, self.new_cell.y-self.final_cell.y)


    def draw_graph(self):
        plt.clf()

        if self.rnd_cell is not None:
            plt.plot(self.rnd_cell.x, self.rnd_cell.y, "^k")
        
        self.map.draw_map()

    def RRT(self, start_pos, end_pos):
        #generate and plot circles
        iterations = 5000
    

        for i in range(iterations):
            #check if the new vertex can connect with the final point
            #if yes, jump out of the loop
            if self.connect_to_goal() == True:
                break

            #check for the start and end points
            while (rrt.collision_check_point(self.rnd_cell) == False):
                rrt.random_cell()


           
            collision_bool, closest_cell = rrt.collision_check_line()

            # Check if the cloest cell is occipied
            if collision_bool == True:
                continue



            # Generate new vertex according to delta_q
            q_new = rrt.new_point_generate(q_near, q_rand, index_near)






#--------------------------------------------------------
# run RRT example:
#--------------------------------------------------------
# set 
grid_size = 20
robot_size = 0.45

grid = Grid(robot_size, grid_size)
rrt = RRT(grid, robot_size)
start_pos = Cell(int(grid_size/2), int(grid_size/2), True)
end_pos = Cell(int(grid_size-2), int(grid_size-2), True)
rrt.RRT(start_pos, end_pos)




