import paho.mqtt.client as mqtt
import json
from draw import *
from particle_filter import *
import math
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("Tag/9A1C/Uplink/Location")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global mqtt_data, spd_window_size, last_uwb_pos
    last_mqtt_data = mqtt_data[0]
    mqtt_data[0] = json.loads(msg.payload.decode("utf-8"))
    if 'est_pos' in mqtt_data[0].keys():
        prev_uwb_pos = last_uwb_pos
        last_uwb_pos = [mqtt_data[0]['est_pos'],  time.time()]
        curr_x, curr_y = mqtt_data[0]['est_pos']['x'], mqtt_data[0]['est_pos']['y']
        if last_mqtt_data:
            prev_x, prev_y = last_mqtt_data['est_pos']['x'], last_mqtt_data['est_pos']['y']
            displacement = math.sqrt((curr_x - prev_x) ** 2 + (curr_y - prev_y) ** 2)
            if prev_uwb_pos:
                time_diff = last_uwb_pos[1] - prev_uwb_pos[1]
                if time_diff > 0:
                    differential_spd = displacement / time_diff
                    if len(speed_window) < spd_window_size:
                        speed_window.append(differential_spd)
                    else:
                        speed_window.pop(0)
                        speed_window.append(differential_spd)

def parse_anchor_idx(json_dict):
    ret = []
    if 'all_anc_id' in json_dict.keys():
        ret = json_dict['all_anc_id']
        ret.sort()
    return ret
    
def parse_ranging(chosen_idx, json_dict):
    ret = []
    for anc in chosen_idx:
        ret.append(json_dict[anc]['dist_to'])
    return ret


def particle_anchor_ranging(chosen_idx, json_dict, particle):
    ret = []
    for anc in chosen_idx:
        anc_x, anc_y = json_dict[anc]['x'], json_dict[anc]['y']
        ret.append(math.sqrt((anc_x - particle.x) ** 2 + (anc_y - particle.y) ** 2))
    return ret
    
mqtt_data = [None]
speed_window = []
spd_window_size = 10
last_uwb_pos = None

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
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
    # Read robbie's sensor
    # Only one raning result from one anchor is used. 
    # To expand the dimensions, use multiple anchors, then we have multiple readings
    # for particles and adjust particle weights accordingly. 
    # Update particle weight according to how good every particle matches
    # robbie's sensor reading
    # r_d = robbie.read_nearest_sensor(world)
    # for p in particles:
    #     if world.is_free(*p.xy):
    #         p_d = p.read_nearest_sensor(world)
    #         p.w = w_gauss(r_d, p_d)
    #     else:
    #         p.w = 0
    # time.sleep(0.5)
    if not mqtt_data[0]:
        continue
    chosen_idx = parse_anchor_idx(mqtt_data[0])
    r_ds = parse_ranging(chosen_idx, mqtt_data[0])  # unit in m
    r_ds = [i*100 for i in r_ds]                    # convert unit to cm
    for p in particles:
        if world.is_free(*p.xy):
            p_ds = particle_anchor_ranging(chosen_idx, mqtt_data[0], p)
            new_weight = w_gauss_multi(r_ds, p_ds)
            if new_weight:
                p.w = new_weight
        else:
            p.w = 0

    # ---------- Try to find current best estimate for display ----------
    m_x, m_y, m_confident = compute_mean_point(world, particles)

    # ---------- Show current state ----------
    world.draw(chosen_idx)
    world.show_particles(particles)
    world.show_mean(m_x, m_y, m_confident)
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
            new_particle = Particle(p.x, p.y,
                    heading=robbie.h if ROBOT_HAS_COMPASS else p.h,
                    noisy=True)
        new_particles.append(new_particle)

    particles = new_particles

    # ---------- Move things ----------
    old_heading = robbie.h
    robbie.move(world)
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