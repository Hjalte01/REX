import numpy as np
from grid import Cell, Position, Grid

DELTA_NOISE = 450
DELTA_K = 1/np.sqrt(2*np.pi*DELTA_NOISE**2)
THETA_NOISE = 0.5
THETA_K = 1/np.sqrt(2*np.pi*THETA_NOISE**2)

class ParticleFilter(object):
    def __init__(self, grid: Grid, n=10000) -> None:
        super(ParticleFilter, self).__init__()
        self.grid = grid
        self.__n__ = n
        # The below syntax is absurd, but it's numpy standard. [:, x] == slice 0:n of the x'th index.
        # ndarrays overloads the assignment operator, so the below will set x indices in the slice, 
        # i.e. for i in range(n): arr[i][x] = y
        self.__particles__ = np.zeros((n, 3))
        self.__particles__[:, 0] = np.random.uniform(0, grid.zone_size*len(grid), size=n) 
        self.__particles__[:, 1] = np.random.uniform(0, grid.zone_size*len(grid), size=n)
        self.__particles__[:, 2] = np.random.uniform(0, 2*np.pi, size=n)

    def __len__(self):
        return self.__n__

    def expected(self, marker: Cell):
        deltas, thetas = np.zeros(len(self)), np.zeros(len(self))
        for i, (x, y, theta) in enumerate(self.__particles__):
            dx, dy = marker.cx - x, marker.cy - y
            deltas[i] = np.sqrt(dx**2 + dy**2)

            el = np.array([dx, dy])/deltas[i]
            etheta = np.array([np.cos(theta), np.sin(theta)])
            ehat = np.array([-np.sin(theta), np.cos(theta)])
            thetas[i] = np.sign(np.dot(el, ehat))*np.arccos(np.dot(el, etheta))
        return deltas, thetas
    
    def update(self, pose: Position, delta_noise=DELTA_NOISE, theta_noise=THETA_NOISE):
        if len(self.grid.markers) == 0:
            return
        
        # Move the particles and add noise.
        self.__particles__[:, 2] += np.mod(np.random.normal(pose.rad, theta_noise, len(self)), 2*np.pi)
        delta = np.random.normal(45, delta_noise, len(self))
        self.__particles__[:, 0] += delta*np.cos(self.__particles__[:, 2])
        self.__particles__[:, 1] += delta*np.sin(self.__particles__[:, 2])

        # Importance weights.
        # We use the measured distance/orientation as mean. Standard deviation is the noise.
        weights = np.ones(len(self))/len(self)
        for marker in self.grid.markers:
            deltas, thetas = self.expected(marker)
            weights *= (DELTA_K*np.exp(-(pose.delta-deltas)**2/(2*delta_noise**2)))
            weights *= (THETA_K*np.exp(-(pose.rad-thetas)**2/(2*theta_noise**2)))
        weights += 1.e-300
        weights /= np.sum(weights)

        # Resample.
        sum = np.cumsum(weights)
        sum[-1] = 1. 
        idxs = np.searchsorted(sum, np.random.random(len(self)))
        particles = self.__particles__[idxs]

        # Estimate the pose.
        x = np.average(particles[:, 0], axis=0, weights=weights)
        y = np.average(particles[:, 1], axis=0, weights=weights)
        return self.grid.transform_xy(x, y), pose
    
def main():
    grid = Grid((0, 0), 450)
    grid.create_marker(grid[8, 0].diffuse(), grid[8, 0][4, 4])
    grid.create_marker(grid[8, 8].diffuse(), grid[8, 8][4, 4])

    pf = ParticleFilter(grid)
    dx, dy = grid[8, 0].cx-grid[4, 4].cx, grid[8, 0].cy-grid[4, 4].cy
    delta = np.sqrt(dx**2+dy**2)
    theta = np.arctan2(dy, dx)
    assert(pf.grid.origo == grid[0, 0][0, 0])
    grid.update(*pf.update(Position(delta, theta)))
    assert(pf.grid.origo == grid[4, 4][0, 0])

if __name__ == '__main__':
    main()
    print(__file__, "\033[32m✓\033[0m")

        

        