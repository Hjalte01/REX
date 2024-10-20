import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from rrt import rrt_path
from grid import Grid, Position
from localization import ParticleFilter

def main():
    grid = Grid((2, 2), 450)
    grid.create_marker(grid[4, 1].diffuse(), grid[4, 1][3, 3])
    grid.create_marker(grid[1, 4].diffuse(), grid[1, 4][3, 3])
    grid.create_marker(grid[7, 4].diffuse(), grid[7, 4][3, 3])
    grid.create_marker(grid[4, 7].diffuse(), grid[4, 7][3, 3])
    grid.create_marker(grid[4, 4].diffuse(), grid[4, 4][0, 0])
    grid.create_marker(grid[2, 6].diffuse(), grid[2, 6][3, 3])
    pf = ParticleFilter(grid)

    for zone_row in grid.zones:
        for zone in zone_row:
            ax.add_patch(Rectangle((zone.cx-225, zone.cy-225), 450, 450, facecolor="white", edgecolor='black'))
            for cell_row in zone.cells:
                for c in cell_row:
                    if zone.free:
                        continue
                    color = "none" if c.free else "black"
                    rect = Rectangle((c.cx-25, c.cy-25), 50, 50, facecolor=color, edgecolor="black")
                    ax.add_patch(rect)
    origo = ax.add_patch(Rectangle((grid[2, 2].cx-25, grid[2, 2].cy-25), 50, 50, facecolor="green", edgecolor="green"))
    ax.add_patch(Rectangle((grid[4, 7][7, 7].cx-25, grid[4, 7][7, 7].cy-25), 50, 50, facecolor="red", edgecolor="red"))

    plt.ion()
    rrtpath = rrt_path(grid, grid[2, 2][0, 0], grid[4, 7][7, 7], 450, 100)
    c = grid.transform_position(rrtpath.pop())
    for i in range(len(rrtpath)-1, -1, -1):
        link = grid.transform_position(rrtpath[i])
        ax.plot([c.cx, link.cx], [c.cy, link.cy], 'g-', alpha=0.2)
        c = link
        plt.draw()
        plt.pause(0.1)

    while len(rrtpath):
        c = grid.transform_position(rrtpath.pop())
        m = grid.markers[0]
        # dx, dy = m.cx - c.cx, m.cy - c.cy
        dx, dy = c.cx - m.cx, c.cy - m.cy
        delta = np.sqrt(dx**2+dy**2)
        theta = np.cos(np.arctan2(dy, dx))
        grid.update(*pf.update(Position(delta, theta)))
        origo.remove()
        origo = ax.add_patch(Rectangle((grid.origo.cx-25, grid.origo.cy-25), 50, 50, facecolor="green", edgecolor="green"))

        plt.draw()
        plt.pause(1)
    plt.ioff()
    plt.show()

if __name__ == '__main__':
    fig, ax = plt.subplots()
    ax.set_title('RTT')
    ax.set_xlim(0, 9**2*50)
    ax.set_ylim(0, 9**2*50)
    main()
