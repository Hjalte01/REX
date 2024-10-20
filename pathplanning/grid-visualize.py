import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from grid import Grid

def main():
    dd = np.sqrt((9/2*450)**2 + (9/2*450)**2)
    grid = Grid((0, 0), 450)

    grid.create_marker(grid[1, 1].diffuse(), grid[1, 1][0, 0])
    grid.create_marker(grid[1, 1].diffuse(), grid[1, 1][0, 8])
    grid.create_marker(grid[1, 1].diffuse(), grid[1, 1][8, 0])
    grid.create_marker(grid[1, 1].diffuse(), grid[1, 1][8, 8])
    grid.create_marker(grid[1, 1].diffuse(), grid[1, 1][3, 3])
    grid.create_marker(grid[7, 7].diffuse(), grid[7, 7][0, 0])
    grid.create_marker(grid[7, 7].diffuse(), grid[7, 7][0, 8])
    grid.create_marker(grid[7, 7].diffuse(), grid[7, 7][8, 0])
    grid.create_marker(grid[7, 7].diffuse(), grid[7, 7][8, 8])
    grid.create_marker(grid[7, 7].diffuse(), grid[7, 7][5, 5])

    for zone_row in grid.zones:
        for zone in zone_row:
            ax.add_patch(Rectangle((zone.cx-225, zone.cy-225), 450, 450, facecolor="white", edgecolor='black'))
            for cell_row in zone.cells:
                for cell in cell_row:
                    if zone.free:
                        continue
                    color = "none" if cell.free else "black"
                    rect = Rectangle((cell.cx-25, cell.cy-25), 50, 50, facecolor=color, edgecolor="black")
                    ax.add_patch(rect)
    plt.show()

if __name__ == "__main__":
    _, ax = plt.subplots()
    ax.set_title("Grid")
    ax.set_xlim(0, 9**2*50)
    ax.set_ylim(0, 9**2*50)
    main()
