# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2011-11-15
#
# ------------------------------------------------------------------------

import math
import turtle

import random
import time

from typing import (Dict, List, Tuple, Set)

turtle.tracer(0, delay=0)
turtle.register_shape("dot", ((-3,-3), (-3,3), (3,3), (3,-3)))
turtle.register_shape("tri", ((-3, -2), (0, 3), (3, -2), (0, 0)))
turtle.speed(10)
turtle.setworldcoordinates(0, 0, 350, 350)
turtle.title("Poor robbie is lost")
UPDATE_EVERY = 0
DRAW_EVERY = 2

class Maze(object):
    def __init__(self, maze_matrix, anc_list=None, block_width=5):
        self.block_witdh = block_width
        self.update_cnt = 0
        self.blocks = []
        self.beacons = []
    
        if not anc_list:
            self.maze = maze_matrix
            self.width   = len(maze_matrix[0])
            self.height  = len(maze_matrix)
            turtle.setworldcoordinates(0, 0, self.width, self.height)
            for y, line in enumerate(self.maze):
                for x, block in enumerate(line):
                    if block:
                        nb_y = self.height - y - self.block_witdh
                        # (x, nb_y) is the lower-left corner of the block
                        self.blocks.append((x, nb_y))
                        if block == 2: # one at each corner
                            self.beacons.extend(((x, nb_y), (x+1, nb_y), (x, nb_y+1), (x+1, nb_y+1)))
                        if block == 3: # one at center only
                            self.beacons.append((x + self.block_witdh/2, nb_y + self.block_witdh/2))
            self.anchor_x_list, self.anchor_y_list = [b[0] for b in self.beacons], [b[1] for b in self.beacons]
        else:
            self.maze = None
            self.anchor_x_list = [anc[1] for anc in anc_list]
            self.anchor_y_list = [anc[2] for anc in anc_list]
            self.width = max(self.anchor_x_list) - min(self.anchor_x_list)
            self.height = max(self.anchor_y_list) - min(self.anchor_y_list)
            for anc in anc_list:
                self.beacons.append((anc[1], anc[2]))
                self.blocks.append((anc[1]-self.block_witdh/2, anc[2]-self.block_witdh/2))
        self.one_px = float(turtle.window_width()) / float(self.width) / 0.002

    def draw(self, lost_beacons):
        # draw the blocks of the maze
        turtle.color("#000000")
        for x, y in self.blocks:
            turtle.up()
            turtle.setposition(x, y)
            turtle.down()
            turtle.setheading(90)
            turtle.begin_fill()
            for _ in range(0, 4):
                turtle.fd(self.block_witdh)
                turtle.right(90)
            turtle.end_fill()
            turtle.up()

        # draw the beacons/anchors
        for i in range(len(self.beacons)):
            x, y = self.beacons[i]
            turtle.setposition(x, y)
            if i in lost_beacons:
                turtle.dot(8, 'white')
            else:
                turtle.dot(8, 'red')
        turtle.stamp()

    def weight_to_color(self, weight):
        return "#%02x00%02x" % (int(weight * 255), int((1 - weight) * 255))

    def is_in(self, x, y):
        if x < min(self.anchor_x_list) or y < min(self.anchor_y_list) or x > max(self.anchor_x_list) or y > max(self.anchor_y_list):
            return False
        return True

    def is_free(self, x, y):
        if not self.is_in(x, y):
            return False

        yy = self.height - int(y) - 1
        xx = int(x)
        if self.maze:
            return self.maze[yy][xx] == 0
        return True

        # 0 - empty square
        # 1 - occupied square
        # 2 - occupied square with a beacon at each corner, detectable by the robot
        # 3 - occupied square with a beacon at the sensor, detectable by the robot

    def show_mean(self, x, y, confident=False):
        if confident:
            turtle.color("#00AA00")
        else:
            turtle.color("#cccccc")
        turtle.setposition(x, y)
        turtle.shape("circle")
        turtle.stamp()

    def show_particles(self, particles):
        self.update_cnt += 1
        if UPDATE_EVERY > 0 and self.update_cnt % UPDATE_EVERY != 1:
            return

        turtle.clearstamps()
        turtle.shape('tri')

        draw_cnt = 0
        px = {}
        for p in particles:
            draw_cnt += 1
            if DRAW_EVERY == 0 or draw_cnt % DRAW_EVERY == 1:
                # Keep track of which positions already have something
                # drawn to speed up display rendering
                scaled_x = int(p.x * self.one_px)
                scaled_y = int(p.y * self.one_px)
                scaled_xy = scaled_x * 10000 + scaled_y
                if not scaled_xy in px:
                    px[scaled_xy] = 1
                    turtle.setposition(*p.xy)
                    turtle.setheading(90 - p.h)
                    turtle.color(self.weight_to_color(p.w))
                    turtle.stamp()

    def show_robot(self, robot):
        turtle.color("green")
        turtle.shape('turtle')
        turtle.setposition(*robot.xy)
        turtle.setheading(90 - robot.h)
        turtle.stamp()
        turtle.update()

    def random_place(self):
        x = random.uniform(0, self.width)
        y = random.uniform(0, self.height)
        return x, y

    def random_free_place(self):
        while True:
            x, y = self.random_place()
            if self.is_free(x, y):
                return x, y

    def euclidean_dist(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def distance_to_nearest_beacon(self, x, y) -> float:
        d = float('inf')
        for c_x, c_y in self.beacons:
            distance = self.euclidean_dist(c_x, c_y, x, y)
            if distance < d:
                d = distance
                d_x, d_y = c_x, c_y
        return d
    
    def distances_to_all_beacons(self, x, y) -> Tuple:
        dist = []
        for c_x, c_y in self.beacons:
            dist.append(self.euclidean_dist(c_x, c_y, x, y))
        return dist
