
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
import math
import numpy as np
from scipy.stats import multivariate_normal
import bisect


# ------------------------------------------------------------------------
# Some utility functions

def add_noise(level, *coords):
    if isinstance(coords[0], list):
        return [x + random.uniform(-level, level) for x in coords[0]]
    return [x + random.uniform(-level, level) for x in coords]

def add_little_noise(*coords):
    return add_noise(0.5, *coords)

def add_some_noise(*coords):
    return add_noise(1, *coords)


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

    m_x, m_y, m_count = 0, 0, 0
    for p in particles:
        m_count += p.w
        m_x += p.x * p.w
        m_y += p.y * p.w

    if m_count == 0:
        return -1, -1, False

    m_x /= m_count
    m_y /= m_count

    # Now compute how good that mean is -- check how many particles
    # actually are in the immediate vicinity
    m_count = 0
    for p in particles:
        if world.euclidean_dist(p.x, p.y, m_x, m_y) < dist_threshold:
            m_count += 1

    return m_x, m_y, m_count > PARTICLE_COUNT * 0.95

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
    def __init__(self, x, y, heading=None, w=1, noisy=False):
        if heading is None:
            heading = random.uniform(0, 360)
        if noisy:
            x, y, heading = add_some_noise(x, y, heading)

        self.x = x
        self.y = y
        self.h = heading
        self.w = w

    def __repr__(self):
        return "(%f, %f, w=%f)" % (self.x, self.y, self.w)

    @property
    def xy(self):
        return self.x, self.y

    @property
    def xyh(self):
        return self.x, self.y, self.h

    @classmethod
    def create_random_particles(cls, particle_count, maze):
        return [cls(*maze.random_free_place()) for _ in range(0, particle_count)]

    def read_nearest_sensor(self, maze):
        """
        Find distance to nearest beacon.
        """
        return maze.distance_to_nearest_beacon(*self.xy)
    
    def read_sensors(self, maze):
        """
        Find all distances to all available beacons.
        """
        return maze.distances_to_all_beacons(*self.xy)
        # if not specified_idx:
        #     return readings
        # if specified_idx:
        #     # Choose specified sensors within all t
        #     # positive infinity in readings indicates signal loss - the beacon 
        #     # is not reachable
        #     for i in specified_idx:
        #         readings[i] = float('inf')
        #     return readings

    def advance_by(self, speed, delta_t=1, checker=None, noisy=False):
        h = self.h
        if noisy:
            speed, h = add_little_noise(speed, h)
            h += random.uniform(-3, 3) # needs more noise to disperse better
        r = math.radians(h)
        dx = math.sin(r) * speed * delta_t
        dy = math.cos(r) * speed * delta_t
        if checker is None or checker(self, dx, dy):
            self.move_by(dx, dy)
            return True
        return False

    def move_by(self, x, y):
        self.x += x
        self.y += y

# ------------------------------------------------------------------------
class Robot(Particle):
    speed = 0

    def __init__(self, maze):
        super(Robot, self).__init__(*maze.random_free_place(), heading=90)
        self.chose_random_direction()
        self.step_count = 0

    def chose_random_direction(self):
        heading = random.uniform(0, 360)
        self.h = heading

    def read_nearest_sensor(self, maze):
        """
        Poor robot, it's sensors are noisy and pretty strange,
        it only can measure the distance to the nearest beacon(!)
        and is not very accurate at that too!
        """
        return add_little_noise(super(Robot, self).read_nearest_sensor(maze))[0]
    
    def read_sensors(self, maze):
        """
        Returns the distances to all the sensors (beacons) in the same order as
        the way sensors are stored (maze.beacons). 
        -------------
        random_loss: True/False
            Simulate the randomized reading loss for some of the sensors (beacons)
        """
        return add_little_noise(super(Robot, self).read_sensors(maze))

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
            ret.append(math.sqrt((anc_dict['x'] - particle.x) ** 2 + (anc_dict['y'] - particle.y) ** 2))
        else:
            ret.append(float('inf'))
    return ret


if __name__ == '__main__':
    PARTICLE_COUNT = 2000    # Total number of particles

    ROBOT_HAS_COMPASS = False # Does the robot know where north is? If so, it
    # makes orientation a lot easier since it knows which direction it is facing.
    # If not -- and that is really fascinating -- the particle filter can work
    # out its heading too, it just takes more particles and more time. 
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
    anchor_list = [('C584',37,20,78), ('DA36',21,335,129), ('9234',295,278,118), ('8287',269,36,66)] # unit in cm
    maze_data = None
    world = Maze(maze_data, anc_list=anchor_list)

    RANDOM_LOSS = False

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
        r_ds = parse_tag_ranging(selected_anc, mqtt_data)  # unit in m
        r_ds = [round(i*100) for i in r_ds]                 # convert unit to cm
        for p in particles:
            p_ds = particle_anchor_ranging(selected_anc, mqtt_data, p)
            new_weight = w_gauss_multi(r_ds, p_ds)
            if new_weight:
                p.w = new_weight
        # ---------- Try to find current best estimate for display ----------
        m_x, m_y, confidence_indicator = compute_mean_point(world, particles, dist_threshold=5)
        if new_uwb_pos_semaphore:
            robbie.x, robbie.y = last_uwb_pos[0]['x']*100, last_uwb_pos[0]['y']*100 #unit in cm
            new_uwb_pos_semaphore = False
        # ---------- Show current state ----------
        world.draw(selected_anc)
        world.show_particles(particles)
        world.show_mean(m_x, m_y, confidence_indicator)
        world.show_robot(robbie)
        # ---------- Shuffle particles ----------
        new_particles = []

        # Normalise weights
        nu = sum(p.w for p in particles)
        if nu:
            for p in particles:
                p.w = p.w / nu
        

        # create a weighted distribution, for fast picking
        dist = WeightedDistribution(particles)

        for _ in particles:
            p = dist.pick()
            if p is None:  # No pick b/c all totally improbable
                new_particle = Particle.create_random_particles(1, world)[0]
            else:
                new_particle = Particle(p.x, p.y, heading=None, noisy=True)
                # new_particle = Particle(p.x, p.y, heading=p.h, noisy=True)
            new_particles.append(new_particle)

        particles = new_particles
        if speed_window:
            robbie.speed = sum(speed_window) / len(speed_window)
        # ---------- Move things ----------
        old_heading = robbie.h
        robbie.move(world, speed=robbie.speed, delta_t=1)
        d_h = robbie.h - old_heading
        # Move particles according to my belief of movement (this may
        # be different than the real movement, but it's all I got)
        for p in particles:
            p.h += d_h # in case robot changed heading, swirl particle heading too
            p.advance_by(robbie.speed)
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    # client.loop_forever()