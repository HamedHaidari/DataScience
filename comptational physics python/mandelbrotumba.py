import numpy as np
import scipy
from numba import jit
import matplotlib.pyplot as plt
import pylab as pl
import time

@jit(nopython=True, fastmath=True, parallel=True)
def MandNumba(ext, max_steps, Nx, Ny):
    data = np.ones((Ny, Nx)) * max_steps
    for i in range(Ny):
        for j in range(Nx):
            x = ext[0] + j * (ext[1] - ext[0]) / (Nx - 1)
            y = ext[2] + i * (ext[3] - ext[2]) / (Ny - 1)
            z0 = x+y*1j
            z = 0j
            for k in range(max_steps):
                if abs(z) > 2:
                    data[i, j] = k
                    break
                z = z*z + z0
    return data
def ax_update(ax):
    ax.set_autoscale_on(False)
    xstart, ystart, xdelta, ydelta = ax.viewLim.bounds
    xend =xstart + xdelta
    yend = ystart + ydelta
    ext=np.array([xstart,xend,ystart,yend])
    # print(ext)
    data = MandNumba(ext, max_steps, Nx, Ny)

    im = ax.images[-1] # take the last image
    im.set_data(data) # update the data
    im.set_extent(ext)
    ax.figure.canvas.draw_idle()


if __name__ == '__main__':
    Nx = 1000  # Increase the resolution
    Ny = 1000  # Increase the resolution
    max_steps = 1000
    ext = np.array([-2, 1, -1, 1])

    t0 = time.time()

    data = MandNumba(ext, max_steps, Nx, Ny)

    print("Elapsed time: ", time.time()-t0)

    fig, ax = plt.subplots(1,1)
    ax.imshow(data, cmap='hot', extent=ext, aspect='equal', origin='lower')
    ax.callbacks.connect('xlim_changed', ax_update)
    ax.callbacks.connect('ylim_changed', ax_update)
    plt.show()

    # plt.imshow(1./data, cmap='hot', extent=ext)
    # plt.show()


