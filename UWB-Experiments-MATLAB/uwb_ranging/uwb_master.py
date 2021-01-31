

import os, platform, sys, json

import serial, glob, re
import time

import subprocess, atexit, signal

import threading

from utils import *
from lcd import lcd_init, lcd_disp

# ttyACM0 -> 421F
# ttyACM1 -> 0487
# ttyACM2 -> 0E15
# ttyACM3 -> 15BA

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


def config_uart_settings(serial_port, settings):
    pass


def end_ranging_thread_job(port_info_dict, data_pointer):
    port = port_info_dict.get("port")
    sys_info = port_info_dict.get("sys_info")
    atexit.register(on_exit, port, True)

    # tag_id = sys_info.get("device_id") 
    # type "lec\n" to the dwm shell console to activate data reporting
    if not is_reporting_loc(port, timeout=sys_info.get("upd_rate")/10):        
        port.write(b'\x6C\x65\x63\x0D')
        time.sleep(0.1)
    assert is_reporting_loc(port, timeout=sys_info.get("upd_rate")/10)
    super_frame = 0
    port.reset_input_buffer()
    while True:
        try:
            data = str(port.readline(), encoding="UTF-8").rstrip()
            if not data[:4] == "DIST":
                continue
            uwb_reporting_dict = make_json_dic(data)
            # uwb_reporting_dict['tag_id'] = tag_id
            uwb_reporting_dict['superFrameNumber'] = super_frame
            json_data = json.dumps(uwb_reporting_dict)
            # tag_client.publish("Tag/{}/Uplink/Location".format(tag_id[-4:]), json_data, qos=0, retain=True)
            super_frame += 1
            data_pointer[0] = uwb_reporting_dict
        except Exception as exp:
            data = str(port.readline(), encoding="UTF-8").rstrip()
            sys.stdout.write(timestamp_log() + "{} end reporting process failed. \n\t\tLast fetched UART data: {}\n".format(sys_info["config"]["end_size"], data))
            raise exp
            sys.exit()


if __name__ == "__main__":
    # Manually change the device setting file (json) before run this program.
    dirname = os.path.dirname(__file__)
    config_data = load_config_json(os.path.join(dirname, "uwb_device_config.json"))
    uwb_devices = config_data.get("uwb_devices", [])
    self_id = config_data.get("id", None) # id of self
    vehicles = {} # the hashmap of all vehicles, self and others
    vehicle = [] # the list of other vehicles to range with
    
    # Identify the Master devices and their ends
    a_end_master, b_end_master = None, None
    a_end_slave, b_end_slave = None, None
    for dev in uwb_devices:
        if config_data[dev]["config"] == "master":
            if config_data[dev]["end_side"] == "a":
                a_end_master = dev
            if config_data[dev]["end_side"] == "b":
                b_end_master = dev
        if config_data[dev]["config"] == "slave":
            if config_data[dev]["end_side"] == "a":
                a_end_slave = dev
            if config_data[dev]["end_side"] == "b":
                b_end_slave = dev
    
    serial_devices = ["/dev/ttyACM"+str(i) for i in range(len(uwb_devices))]
    serial_ports = {}
    # Match the serial ports with the device list    
    for dev in serial_devices:
        p = serial.Serial(dev, baudrate=115200, timeout=3.0)        
        port_available_check(p)
        # Initialize the UART shell command
        parse_uart_init(p)
        sys_info = parse_uart_sys_info(p)
        device_id_short = sys_info.get("device_id")[-4:]
        # Link the individual Master/Slave with the serial ports by hashmap
        serial_ports[device_id_short] = {}
        serial_ports[device_id_short]["port"] = p
        serial_ports[device_id_short]["sys_info"] = sys_info
        serial_ports[device_id_short]["config"] = config_data.get(sys_info.get(device_id_short))
        # Type "lec\n" to the dwm shell console to activate data reporting
        if not is_reporting_loc(p, timeout=sys_info.get("upd_rate")/10):
            if dev == a_end_master or dev == b_end_master:
                p.write(b'\x6C\x65\x63\x0D')
                time.sleep(0.1)
                assert is_reporting_loc(p, timeout=sys_info.get("upd_rate")/10)
        # Maybe later we can close the ports linking to the Slave/Anchors if no needs
        
    a_end_dist_ptr, b_end_dist_ptr = [{}], [{}]
    a_end_ranging_thread = threading.Thread(target=end_ranging_thread_job, 
                                            args=(serial_ports[a_end_master],
                                                  a_end_dist_ptr,),
                                            name="A End Ranging")
    b_end_ranging_thread = threading.Thread(target=end_ranging_thread_job, 
                                            args=(serial_ports[b_end_master],
                                                  b_end_dist_ptr,),
                                            name="B End Ranging")
    a_end_ranging_thread.daemon, b_end_ranging_thread.daemon = True, True
    a_end_ranging_thread.start()
    b_end_ranging_thread.start()
    
    lcd_init()
    while True:
        # wait for new UWB reporting results
        a_end_dist_old, b_end_dist_old = a_end_dist_ptr[0], b_end_dist_ptr[0]
        while True:
            a_end_dist, b_end_dist = a_end_dist_ptr[0], b_end_dist_ptr[0]
            if a_end_dist is a_end_dist_old and b_end_dist is b_end_dist_old:
                continue
            else:
                break
        a_ranging_results, b_ranging_results = [], []  
        for anc in a_end_dist.get("all_anc_id", []):
            if anc == a_end_slave or anc == b_end_slave:
                continue
            a_ranging_results.append((anc, a_end_dist_ptr[0].get(anc, {})))
        for anc in b_end_dist.get("all_anc_id", []):
            if anc == a_end_slave or anc == b_end_slave:
                continue
            b_ranging_results.append((anc, b_end_dist_ptr[0].get(anc, {})))
            
        a_ranging_results.sort(key=lambda x: x[1].get("dist_to", float("inf")))
        b_ranging_results.sort(key=lambda x: x[1].get("dist_to", float("inf")))
        line1 = "A End:{} {}".format(a_ranging_results[0][0], a_ranging_results[0][1]["dist_to"]) if a_ranging_results else "A End OutOfRange"
        line2 = "B End:{} {}".format(b_ranging_results[0][0], b_ranging_results[0][1]["dist_to"]) if b_ranging_results else "B End OutOfRange"
        lcd_disp(line1, line2)
        print("A end reporting: ", a_ranging_results)
        print("B end reporting: ", b_ranging_results)
        