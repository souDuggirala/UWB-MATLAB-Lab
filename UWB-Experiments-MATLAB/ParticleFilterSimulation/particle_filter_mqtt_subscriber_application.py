
# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2011-11-15
#  Modified by Zezhou Wang for UWB applications on 2021
# ------------------------------------------------------------------------

from typing import (Dict, List, Tuple, Set)

import paho.mqtt.client as mqtt
import json
from draw import *
from plot_3d import ProcessPlotter, NBPlot
import random
import math
import numpy as np
from scipy.stats import multivariate_normal
import bisect

import time

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import multiprocessing as mp
import time


AXIAL_NOISE=5
SPEED_NOISE=0.5
AXIAL_NOISE_LARGE=0.1
HEADING_NOISE, HEADING_RANGE = 5, [0, 360]
PITCH_NOISE, PITCH_RANGE = 5, [-90, 90]

# ------------------------------------------------------------------------
# Some utility functions

def add_noise(level, range_lim, *coords):
    if len(coords)==1:
        raw = coords[0] + random.uniform(-level, level)
    else:
        raw = [x + random.uniform(-level, level) for x in coords]
    if not range_lim:
        return raw
    elif isinstance(raw, List):
        for x in raw:
            if x < range_lim[0]:
                x = range_lim[0]
            if x > range_lim[1]:
                x = range_lim[1]
    else:
        if raw < range_lim[0]:
            raw = range_lim[0]
        if raw > range_lim[1]:
            raw = range_lim[1]
    return raw

# This is just a gaussian kernel I pulled out of my hat, to transform
# values near to robbie's measurement => 1, further away => 0
sigma = 15
sigma2 = sigma ** 2
def w_gauss(a, b):
    error = a - b
    g = math.e ** -(error ** 2 / (2 * sigma2))
    return g

# This is the 0-mean multivariate gaussian pdf value serves as the weight
# values near to robbie's measurement => 1, further away => 0
# the pdf value is not normalized
def w_gauss_multi(a: List, b: List) -> float:
    a_valid = [i for i in range(len(a)) if a[i] != float('inf')]
    b_valid = [i for i in range(len(b)) if b[i] != float('inf')]
    intersection_idx = [i for i in a_valid if i in b_valid]
    a = np.asarray([a[i] for i in intersection_idx])
    b = np.asarray([b[i] for i in intersection_idx])
    
    dim = len(a)
    if dim > 0:
        error = (a - b)
        center = (a - a)
        error = error.reshape(1,dim)
        mean = np.zeros(dim, float)
        cov = np.zeros((dim,dim), float)
        np.fill_diagonal(cov, sigma2)
        center_pdf = multivariate_normal.pdf(x=center, mean=mean, cov=cov)
        g = multivariate_normal.pdf(x=error, mean=mean, cov=cov) / center_pdf
        return g

# ------------------------------------------------------------------------
def compute_mean_point(world, particles, dist_threshold=25):
    """
    Compute the mean for all particles that have a reasonably good weight.
    This is not part of the particle filter algorithm but rather an
    addition to show the "best belief" for current position.
    """

    m_x, m_y, m_z, m_count = 0, 0, 0, 0
    for p in particles:
        m_count += p.w
        m_x += p.x * p.w
        m_y += p.y * p.w
        m_z += p.z * p.w

    if m_count == 0:
        return -1, -1, -1, False

    m_x /= m_count
    m_y /= m_count
    m_z /= m_count

    # Now compute how good that mean is -- check how many particles
    # actually are in the immediate vicinity
    m_count = 0
    for p in particles:
        if world.euclidean_dist(p.x, p.y, p.z, m_x, m_y, m_z) < dist_threshold:
            m_count += 1

    return m_x, m_y, m_z, m_count > PARTICLE_COUNT * 0.95

# ------------------------------------------------------------------------
class WeightedDistribution(object):
    def __init__(self, state):
        accum = 0.0
        self.state = [p for p in state if p.w > 0]
        self.distribution = []
        for x in self.state:
            accum += x.w
            self.distribution.append(accum)

    def pick(self):
        try:
            uni = random.uniform(0, 1)
            idx = bisect.bisect_left(self.distribution, uni)
            a = self.state[idx]
            return a
        except IndexError:
            # Happens when all particles are improbable w=0
            return None

# ------------------------------------------------------------------------
class Particle(object):
    def __init__(self, x, y, z=0, xy_heading=None, pitch=None, w=1, noisy=False):
        if xy_heading is None:
            xy_heading = random.uniform(HEADING_RANGE[0], HEADING_RANGE[1])
        if pitch is None:
            pitch = random.uniform(PITCH_RANGE[0], PITCH_RANGE[1])
        if noisy:
            x, y, z = add_noise(AXIAL_NOISE, [], x, y, z)
            xy_heading = add_noise(HEADING_NOISE, HEADING_RANGE, xy_heading)
            pitch = add_noise(PITCH_NOISE, PITCH_RANGE, pitch)

        self.x = x
        self.y = y
        self.z = z
        self.xy_heading = xy_heading
        self.pitch = pitch
        self.w = w

    def __repr__(self):
        return "(%f, %f, %f, w=%f)" % (self.x, self.y, self.z, self.w)

    @property
    def xy(self):
        return self.x, self.y

    @property
    def xyz(self):
        return self.x, self.y, self.z

    @classmethod
    def create_random_particles(cls, particle_count, maze):
        return [cls(*maze.random_free_place()) for _ in range(0, particle_count)]

    def advance_by(self, speed, delta_t=1, checker=None, noisy=False):
        xy_heading = self.xy_heading
        pitch = self.pitch
        if noisy:
            speed = add_noise(SPEED_NOISE, [], speed)
            xy_heading = add_noise(HEADING_NOISE, HEADING_RANGE, xy_heading)
            pitch = add_noise(PITCH_NOISE, PITCH_RANGE, pitch)
        r, pitch_r = math.radians(xy_heading), math.radians(pitch)
        speed_xy = math.cos(pitch_r)
        dx = math.sin(r) * speed_xy * delta_t
        dy = math.cos(r) * speed_xy * delta_t
        dz = math.sin(pitch_r) * speed * delta_t
        if checker is None or checker(self, dx, dy, dz):
            self.move_by(dx, dy, dz)
            return True
        return False

    def move_by(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

# ------------------------------------------------------------------------
class Robot(Particle):
    speed = 0

    def __init__(self, maze):
        super(Robot, self).__init__(*maze.random_free_place(), xy_heading=90)
        self.chose_random_direction()
        self.step_count = 0

    def chose_random_direction(self):
        xy_heading = random.uniform(0, 360)
        self.xy_heading = xy_heading

    def move(self, maze, speed, delta_t):
        """
        Move the robot. Note that the movement is stochastic too.
        """
        self.step_count += 1
        self.advance_by(speed, delta_t=1, noisy=True, checker=None)


# The callback for when the client receives a CONNACK response from the server.
def mqtt_on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("Tag/9A1C/Uplink/Location")

# The callback for when a PUBLISH message is received from the server.
def mqtt_on_message(client, userdata, msg):
    global mqtt_data, spd_window_size, last_uwb_pos, new_uwb_pos_semaphore
    prev_mqtt_data = mqtt_data
    mqtt_data = json.loads(msg.payload.decode("utf-8"))
    if 'est_pos' in mqtt_data.keys():
        prev_uwb_pos = last_uwb_pos
        new_uwb_pos_semaphore = True
        last_uwb_pos = [mqtt_data['est_pos'],  time.time()]
        curr_x, curr_y = last_uwb_pos[0]['x'], last_uwb_pos[0]['y']
        if prev_uwb_pos:
            prev_x, prev_y = prev_uwb_pos[0]['x'], prev_uwb_pos[0]['y']
            displacement = math.sqrt((curr_x - prev_x) ** 2 + (curr_y - prev_y) ** 2)
            time_diff = last_uwb_pos[1] - prev_uwb_pos[1]
            if time_diff > 0:
                differential_spd = displacement / time_diff * 100   # unit in cm
                if len(speed_window) < spd_window_size:
                    speed_window.append(differential_spd)
                else:
                    speed_window.pop(0)
                    speed_window.append(differential_spd)

def parse_anchor_id(json_dict):
    ret = []
    if 'all_anc_id' in json_dict.keys():
        ret = json_dict['all_anc_id']
        ret.sort()
    return ret
    
def parse_tag_ranging(selected_anc, json_dict):
    ret = []
    for anc in selected_anc:
        anc_dict = json_dict.get(anc, None)
        if anc_dict:
            ret.append(anc_dict['dist_to'])
        else:
            ret.append(float('inf'))
    return ret

def particle_anchor_ranging(selected_anc, json_dict, particle):
    ret = []
    for anc in selected_anc:
        anc_dict = json_dict.get(anc, None)
        if anc_dict:
            ret.append(math.sqrt(   (anc_dict['x'] - particle.x) ** 2 +
                                    (anc_dict['y'] - particle.y) ** 2 +
                                    (anc_dict['z'] - particle.z) ** 2))
        else:
            ret.append(float('inf'))
    return ret


if __name__ == '__main__':
    PARTICLE_COUNT = 2000    # Total number of particles

    ROBOT_HAS_COMPASS = False # Does the robot know where north is? If so, it
    # makes orientation a lot easier since it knows which direction it is facing.
    # If not -- and that is really fascinating -- the particle filter can work
    # out its xy_heading too, it just takes more particles and more time. 
    mqtt_data = None
    speed_window = []
    spd_window_size = 10
    last_uwb_pos = None
    new_uwb_pos_semaphore = False

    client = mqtt.Client()
    client.on_connect = mqtt_on_connect
    client.on_message = mqtt_on_message
    client.connect("192.168.0.182", 1883, 60)
    client.loop_start()

    # create the particle filter maze world
    anchor_list = [('C584',30,16,78), ('DA36',21,335,129), ('9234',295,278,81), ('8287',269,37,72)] # unit in cm
    maze_data = None
    

    RANDOM_LOSS = False
    PLOT_3D = True
    if PLOT_3D:
        world = Maze(maze_data, anc_list=anchor_list, turtle_init=False)
        pl = NBPlot(world)
    else:
        world = Maze(maze_data, anc_list=anchor_list, turtle_init=True)
    # initial distribution assigns each particle an equal probability
    particles = Particle.create_random_particles(PARTICLE_COUNT, world)
    robbie = Robot(world)
    while True:
        # To expand the dimensions, use multiple anchors, then we have multiple readings
        # for particles and adjust particle weights accordingly. 
        # Update particle weight according to how good every particle matches
        # robbie's sensor reading
        if not mqtt_data:
            continue
        selected_anc = parse_anchor_id(mqtt_data)
        if RANDOM_LOSS:
            selected_anc = random.sample(selected_anc, random.randint(0, len(selected_anc)))
        r_ds = parse_tag_ranging(selected_anc, mqtt_data)  
        # unit in m, if not projection, the elevation prevents the correct result
        r_ds = [round(i*100) for i in r_ds]                 
        # convert unit to cm
        for p in particles:
            if world.is_free(*p.xyz):
                p_ds = particle_anchor_ranging(selected_anc, mqtt_data, p)
                new_weight = w_gauss_multi(r_ds, p_ds)
                if new_weight:
                    p.w = new_weight
            else:
                p.w = 0
        # ---------- Try to find current best estimate for display ----------
        if new_uwb_pos_semaphore:
            robbie.x, robbie.y, robbie.z = last_uwb_pos[0]['x']*100, last_uwb_pos[0]['y']*100, last_uwb_pos[0]['z']*100 #unit in cm
            new_uwb_pos_semaphore = False
        # ---------- Show current state ----------
        m_x, m_y, m_z, confidence_indicator = compute_mean_point(world, particles, dist_threshold=5)
        if not PLOT_3D:
            world.draw(selected_anc)
            world.show_particles(particles)
            world.show_mean(m_x, m_y, confidence_indicator)
            world.show_robot(robbie)
        else:
            if plt.get_backend() == "MacOSX":   # MacOS might require a different start method
                mp.set_start_method("forkserver")
            pl.plot(data=[selected_anc, robbie, particles, (m_x, m_y, m_z, confidence_indicator)])
        # ---------- Shuffle particles ----------
        new_particles = []

        # Normalise weights
        nu = sum(p.w for p in particles)
        if nu:
            for p in particles:
                p.w = p.w / nu
        picked, generated = [], []
        # create a weighted distribution, for fast picking
        dist = WeightedDistribution(particles)
        for _ in particles:
            p = dist.pick()
            if p is None:  # No pick b/c all totally improbable
                new_particle = Particle.create_random_particles(1, world)[0]
                generated.append(new_particle)
            else:
                new_particle = Particle(p.x, p.y, p.z, xy_heading=None, noisy=True)
                picked.append(new_particle)
            new_particles.append(new_particle)

        particles = new_particles
        if speed_window:
            robbie.speed = sum(speed_window) / len(speed_window)

        # print(min([p.w for p in particles]), max([p.w for p in particles]))      
        # print(r_ds, p_ds)
        # print("Robot speed: {}, picked particle: {}, generated particle: {}"
        #         .format(robbie.speed, len(picked), len(generated)))
        # print("particle x range: [{}-{}] y range: [{}-{}] z range: [{}-{}]"
        #         .format(round(min([p.x for p in particles]),2), round(max([p.x for p in particles]),2), 
        #                 round(min([p.y for p in particles]),2), round(max([p.y for p in particles]),2),
        #                 round(min([p.z for p in particles]),2), round(max([p.z for p in particles]),2)))
        # print("particle x: {} y: {} z: {}"
        #         .format(round(m_x,2), round(m_y,2), round(m_z, 2)))
        # print("uwb x: {}, y: {}, z: {}".format(round(robbie.x,2), round(robbie.y, 2), round(robbie.z,2)))



        # ---------- Move things ----------
        old_xy_heading = robbie.xy_heading
        robbie.move(world, speed=robbie.speed, delta_t=1)
        d_xy_heading = robbie.xy_heading - old_xy_heading
        # Move particles according to my belief of movement (this may
        # be different than the real movement, but it's all I got)
        for p in particles:
            p.xy_heading += d_xy_heading # in case robot changed xy_heading, swirl particle xy_heading too
            p.advance_by(robbie.speed)