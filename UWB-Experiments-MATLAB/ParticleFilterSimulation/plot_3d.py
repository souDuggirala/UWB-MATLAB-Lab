import multiprocessing as mp
import time

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import numpy as np

# Fixing random state for reproducibility
np.random.seed(19680801)
DRAW_EVERY = 10
class ProcessPlotter(object):
    def __init__(self, world):
        self.world = world
    
    def terminate(self):
        plt.close('all')

    def call_back(self):
        while self.pipe.poll():
            command = self.pipe.recv()
            if command is None:
                self.terminate()
                return False
            else:
                self.ax.clear()
                self.ax.set_xlabel('X axis')
                self.ax.set_ylabel('Y axis')
                self.ax.set_zlabel('Z axis')
                [selected_anc, robbie, particles, (m_x, m_y, m_z, confidence_indicator)] = command
                # draw the beacons/anchors
                x, y, z, attr = [], [] ,[], []
                for i in range(len(self.world.beacons)):
                    x, y, z = self.world.beacons[i][1],self.world.beacons[i][2],self.world.beacons[i][3]
                    if self.world.beacons[i][0] in selected_anc:
                        self.ax.plot(x, y, z, 'go')
                    else:
                        self.ax.plot(x, y, z, 'ro')
                draw_cnt = 0
                for p in particles:
                    draw_cnt += 1
                    if DRAW_EVERY == 0 or draw_cnt % DRAW_EVERY == 1:
                        # Keep track of which positions already have something
                        # drawn to speed up display rendering
                        self.ax.plot(p.x, p.y, p.z, 'bo')
                self.fig.canvas.draw()
        return True

    def __call__(self, pipe):
        print('starting plotter...')

        self.pipe = pipe
        self.fig = plt.figure(figsize=plt.figaspect(0.5))
        self.ax = p3.Axes3D(self.fig)

        timer = self.fig.canvas.new_timer(interval=1000)
        timer.add_callback(self.call_back)
        timer.start()

        print('...done')
        plt.show()

class NBPlot(object):
    def __init__(self, world):
        self.plot_pipe, plotter_pipe = mp.Pipe()
        self.plotter = ProcessPlotter(world)
        self.plot_process = mp.Process(
            target=self.plotter, args=(plotter_pipe,), daemon=True)
        self.plot_process.start()

    def plot(self, data, finished=False):
        send = self.plot_pipe.send
        if finished:
            send(None)
        else:
            send(data)


def main():
    pl = NBPlot()
    while True:
        pl.plot()
        time.sleep(0.05)


if __name__ == '__main__':
    if plt.get_backend() == "MacOSX":
        mp.set_start_method("forkserver")
    main()