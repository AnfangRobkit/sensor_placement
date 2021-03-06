from sensor_class.fence import CFence
from sensor_class.human import CHuman
from sensor_class.robot import CRobot
from sensor_class.lidar import CLidar
from sensor_class.mat import CMate
from sensor_class.utils import *
from sensor_factory.coverage_detector import CCoverageDetector

import matplotlib.pyplot as plt
import numpy as np
import os

dangerous_zone_radius = 2
cwd = os.getcwd()

# define different sensor parameters
mate = CMate('Mate1', x=3, y=4, width=4, length=6)
fence = CFence('Fence1', x=-3, y=3, length=4)
lidar = CLidar(x=3, y=-2)
human = CHuman('Worker1', start_vel=2, start_pos_x=7, start_pos_y=5, heading=1.1 * np.pi)
robot = CRobot(robot_range=dangerous_zone_radius, name='Robot1', start_vel=0.1, start_pos=0)

counter = 0
lidar_scanner = 0
current_time = 0
dt = 0.10  # time step
simulation_time = 100  # time limit
fig, axes = plt.subplots(1, 1)  # use subplot for more stable and flexible visualization of the dynamic image
lidar_time_gap = 1 / lidar.rate
plt.ion()

save_flag = False

while current_time < simulation_time:
    # remember to clean the current image to display the image dynamically
    axes.cla()
    # set the axis limits
    axes.set_xlim([-10, 10])
    axes.set_ylim([-10, 10])
    rx, ry = lidar.object_detection(human)
    lidar_scanner += 1
    lidar.signal_output(rx, ry)
    if len(rx) > 1:
        lidar.plot_scan(axes, rx, ry)
    if human:
        human.update(dt, omega=0)
        human.plot(axes)  # update the human positions
    robot.update()  # update the robot pose
    current_time += dt
    fence.fence_contact(human)  # run fence detection function
    mx, my = mate.detect_human(human)  # run mate detection function
    mate.plot(axes)
    fence.plot(axes)
    lidar.plot(axes)
    mate.plot_scan(axes, mx, my)
    robot.plot(axes)
    draw_warn_zone(axes, robot)
    plt.pause(0.01)
    plt.show()
    if save_flag:
        plt.savefig(f'{cwd}/sensor_class/out/scenario/fig{counter}.png')
        counter += 1
