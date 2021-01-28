

import os, platform, sys, json

import serial, glob, re
import time
from utils import *

import subprocess, atexit, signal

import threading

# ttyACM0 -> 421F
# ttyACM1 -> 0487
# ttyACM2 -> 0E15
# ttyACM3 -> 15BA


def parse_uart_init(serial_port):
    # register the callback functions when the service ends
    # atexit for regular exit, signal.signal for system kills    
    atexit.register(on_exit, serial_port, True)
    signal.signal(signal.SIGTERM, on_killed)
    # Pause for 0.1 sec after establishment
    time.sleep(0.1)
    # Double enter (carriage return) as specified by Decawave
    serial_port.write(b'\x0D\x0D')
    time.sleep(0.1)
    serial_port.reset_input_buffer()

    # By default the update rate is 10Hz/100ms. Check again for data flow
    # if data is flowing, stop the data flow (temporarily) to execute commands.
    if is_reporting_loc(serial_port):
        serial_port.write(b'\x6C\x65\x63\x0D')
        time.sleep(0.1)


def on_exit(serialport, verbose=False):
    """ On exit callbacks to make sure the serialport is closed when
        the program ends.
    """
    if verbose:
        sys.stdout.write(timestamp_log() + "Serial port {} closed on exit\n".format(serialport.port))
    if sys.platform.startswith('linux'):
        import fcntl
        fcntl.flock(serialport, fcntl.LOCK_UN)
    serialport.close()


def parse_uart_reportings(serial_port, data_pointer):
    if data_pointer[0] is None:
        data_pointer[0] = {}
    while True:
        try:
            data = str(serial_port.readline(), encoding="UTF-8").rstrip()
            if not data[:4] == "DIST":
                continue
            data_pointer[0] = make_json_dic(data)
            # data_pointer[0]['tag_id'] = tag_id
            data_pointer[0]['superFrameNumber'] = super_frame
            json_data = json.dumps(json_dic)
            # tag_client.publish("Tag/{}/Uplink/Location".format(tag_id[-4:]), json_data, qos=0, retain=True)
            super_frame += 1
            # pass out coordinates using uwb_pointer[0] pointer for other threads
            uwb_pointer[0] = json_dic
        except Exception as exp:
            data = str(serial_port.readline(), encoding="UTF-8").rstrip()
            sys.stdout.write(timestamp_log() + data)
            raise exp
        
def a_end_ranging_thread_job(port, sys_info, data_pointer):
    atexit.register(on_exit, port, True)
    tag_id = sys_info.get("device_id") 
    upd_rate = sys_info.get("upd_rate")
    # type "lec\n" to the dwm shell console to activate data reporting
    if not is_reporting_loc(port, timeout=upd_rate/10):        
        port.write(b'\x6C\x65\x63\x0D')
        time.sleep(0.1)
    assert is_reporting_loc(port, timeout=upd_rate/10)
    super_frame = 0
    port.reset_input_buffer()
    while True:
        try:
            data = str(port.readline(), encoding="UTF-8").rstrip()
            if not data[:4] == "DIST":
                continue
            data_pointer[0] = make_json_dic(data)
            # data_pointer[0]['tag_id'] = tag_id
            data_pointer[0]['superFrameNumber'] = super_frame
            json_data = json.dumps(data_pointer[0])
            # tag_client.publish("Tag/{}/Uplink/Location".format(tag_id[-4:]), json_data, qos=0, retain=True)
            super_frame += 1
        except Exception as exp:
            data = str(port.readline(), encoding="UTF-8").rstrip()
            sys.stdout.write(timestamp_log() + "A End reporting process failed. \n\t\tLast fetched UART data: {}\n".format(data))
            raise exp
            sys.exit()

def b_end_ranging_thread_job(port, sys_info, data_pointer):
    atexit.register(on_exit, port, True)
    tag_id = sys_info.get("device_id") 
    upd_rate = sys_info.get("upd_rate")
    # type "lec\n" to the dwm shell console to activate data reporting
    if not is_reporting_loc(port, timeout=upd_rate/10):        
        port.write(b'\x6C\x65\x63\x0D')
        time.sleep(0.1)
    assert is_reporting_loc(port, timeout=upd_rate/10)
    super_frame = 0
    port.reset_input_buffer()
    while True:
        try:
            data = str(port.readline(), encoding="UTF-8").rstrip()
            if not data[:4] == "DIST":
                continue
            data_pointer[0] = make_json_dic(data)
            # data_pointer[0]['tag_id'] = tag_id
            data_pointer[0]['superFrameNumber'] = super_frame
            json_data = json.dumps(data_pointer[0])
            # tag_client.publish("Tag/{}/Uplink/Location".format(tag_id[-4:]), json_data, qos=0, retain=True)
            super_frame += 1
        except Exception as exp:
            data = str(port.readline(), encoding="UTF-8").rstrip()
            sys.stdout.write(timestamp_log() + "A End reporting process failed. \n\t\tLast fetched UART data: {}\n".format(data))
            raise exp
            sys.exit()

if __name__ == "__main__":
    # Manually change the device setting file (json) before run this program.
    config_data = load_config_json("./uwb_device_config.json")
    uwb_devices = config_data.get("uwb_devices", [])
    self_id = config_data.get("id", None) # id of self
    vehicles = {} # the hashmap of all vehicles, self and others
    vehicle = [] # the list of other vehicles to range with
    
    # Identify the Master devices and their ends
    a_end_master, b_end_master = None, None
    for dev in uwb_devices:
        if config_data[dev]["config"] == "master":
            if config_data[dev]["end_side"] == "a":
                a_end_master = dev
            if config_data[dev]["end_side"] == "b":
                b_end_master = dev
    
    serial_devices = ["/dev/ttyACM"+str(i) for i in range(len(uwb_devices))]
    serial_ports = {}
    # Match the serial ports with the device list    
    for dev in serial_devices:
        p = serial.Serial(dev, baudrate=115200, timeout=3.0)        
        # Initialize the UART shell command
        parse_uart_init(p)
        sys_info = get_sys_info(p, verbose=False)
        # Link the individual Master/Slave with the serial ports by hashmap
        serial_ports[sys_info.get("device_id")[-4:]] = {}
        serial_ports[sys_info.get("device_id")[-4:]]["port"] = p
        serial_ports[sys_info.get("device_id")[-4:]]["sys_info"] = sys_info
        # Type "lec\n" to the dwm shell console to activate data reporting
        if not is_reporting_loc(p, timeout=sys_info.get("upd_rate")/10):
            if dev == a_end_master or dev == b_end_master:
                p.write(b'\x6C\x65\x63\x0D')
                time.sleep(0.1)
                assert is_reporting_loc(p, timeout=sys_info.get("upd_rate")/10)
        # Maybe later we can close the ports linking to the Slave/Anchors if no needs
        
    a_end_dist_ptr, b_end_dist_ptr = [{}], [{}]
    print(b_end_master, serial_ports[b_end_master]["port"])
    a_end_ranging_thread = threading.Thread(target=a_end_ranging_thread_job, 
                                            args=(serial_ports[a_end_master]["port"],
                                                  serial_ports[a_end_master]["sys_info"],
                                                  a_end_dist_ptr,),
                                            name="A End Ranging")
    b_end_ranging_thread = threading.Thread(target=b_end_ranging_thread_job, 
                                            args=(serial_ports[b_end_master]["port"],
                                                  serial_ports[b_end_master]["sys_info"],
                                                  b_end_dist_ptr,),
                                            name="B End Ranging")
    a_end_ranging_thread.daemon, b_end_ranging_thread.daemon = True, True
    a_end_ranging_thread.start()
    b_end_ranging_thread.start()
    
    while True:
        print("A end reporting: ", a_end_dist_ptr)
        print("B end reporting: ", b_end_dist_ptr)
        time.sleep(1)
