import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rrt import rrt_path
from grid import Grid

def main():
    grid = Grid((2, 2), 450)
    grid.create_marker(grid[4, 1].diffuse(), grid[4, 1][3, 3])
    grid.create_marker(grid[1, 4].diffuse(), grid[1, 4][3, 3])
    grid.create_marker(grid[7, 4].diffuse(), grid[7, 4][3, 3])
    grid.create_marker(grid[4, 7].diffuse(), grid[4, 7][3, 3])
    grid.create_marker(grid[4, 4].diffuse(), grid[4, 4][0, 0])
    grid.create_marker(grid[2, 6].diffuse(), grid[2, 6][3, 3])

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
    ax.add_patch(Rectangle((grid[2, 2].cx-25, grid[2, 2].cy-25), 50, 50, facecolor="green", edgecolor="green"))
    ax.add_patch(Rectangle((grid[4, 7][7, 7].cx-25, grid[4, 7][7, 7].cy-25), 50, 50, facecolor="red", edgecolor="red"))

    plt.ion()
    rrtpath = rrt_path(grid, grid[2, 2][0, 0], grid[4, 7][7, 7], 450, 100, ax)
    cell = grid.transform_position(rrtpath.pop())
    while len(rrtpath):
        link = grid.transform_position(rrtpath.pop())
        ax.plot([cell.cx, link.cx], [cell.cy, link.cy], 'g-', alpha=1)
        cell = link
        plt.draw()
        plt.pause(0.15)
    plt.ioff()
    plt.show()

if __name__ == '__main__':
    fig, ax = plt.subplots()
    ax.set_title('RTT')
    ax.set_xlim(0, 9**2*50)
    ax.set_ylim(0, 9**2*50)
    main()
