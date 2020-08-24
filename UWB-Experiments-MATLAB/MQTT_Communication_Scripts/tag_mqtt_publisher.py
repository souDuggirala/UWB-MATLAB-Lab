import os, platform, sys

import serial, glob, re
import time
from datetime import datetime

import subprocess
import paho.mqtt.client as mqtt

import json

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

def mqtt_on_publish(client, data, result):
    pass

def is_reporting_loc(serialport, timeout=2):
    """ Detect if the DWM1001 Tag is running on data reporting mode
        :returns: True or False
    """
    init_bytes_avail = serialport.in_waiting
    time.sleep(timeout)
    final_bytes_avail = serialport.in_waiting
    if final_bytes_avail - init_bytes_avail > 0:
        time.sleep(0.1)
        return True
    time.sleep(0.1)
    return False

def get_tag_serial_port():
    """ Detect the serial port name of DWM1001 Tag

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            return DWM1001 tag serial port name and make sure it is closed
    """
    ports = []
    import serial.tools.list_ports
    if sys.platform.startswith('win'):
        # assume there is only one J-Link COM port
        ports += [str(i).split(' - ')[0]
                    for  i in serial.tools.list_ports.comports() 
                    if "JLink" in str(i)]
    elif sys.platform.startswith('linux'):
        # the UART between RPi adn DWM1001-Dev is designated as serial0
        # with the drivers installed. 
        # see Section 4.3.1.2 of DWM1001-Firmware-User-Guide
        if "raspberrypi" in os.uname():
            ports += ["/dev/serial0"]
        else:
            ports += glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.usbmodem*')
    else:
        raise EnvironmentError('Unsupported platform')
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
        except:
            raise ConnectionError("Wrong serial port detected for UWB tag")
    return ports

def get_sys_info(serialport):
    """ Get the system config information of the tag device through UART

        :returns:
            Dictionary of system information
    """
    sys_info = {}
    if is_reporting_loc(serialport):
        serialport.write(b'\x6C\x65\x63\x0D')
        time.sleep(0.1)
    # Write "si" to show system information of DWM1001
    serialport.reset_input_buffer()
    serialport.write(b'\x73\x69\x0D')
    time.sleep(0.1)
    # TODO parse the ID of the tag
    si = str(serialport.read(serialport.in_waiting))
    serialport.reset_input_buffer()
    
    # PANID in hexadecimal
    pan_id = re.search("(?<=uwb0\:\spanid=)(.{5})(?=\saddr=)", si).group(0)
    sys_info["pan_id"] = pan_id
    # Device ID in hexadecimal
    device_id = re.search("(?<=panid=.{6}addr=)(.{17})", si).group(0)
    sys_info["device_id"] = device_id
    # Update rate of location reporting in int
    upd_rate = re.search("(?<=upd_rate_stat=)(.*)(?=\slabel=)",si).group(0)
    sys_info["upd_rate"] = int(upd_rate)

    return sys_info

def make_json_dic(raw_string):
    # sample input:
    # les\n: 022E[7.94,8.03,0.00]=3.38 9280[7.95,0.00,0.00]=5.49 DCAE[0.00,8.03,0.00]=7.73 5431[0.00,0.00,0.00]=9.01 le_us=3082 est[6.97,5.17,-1.77,53]
    # lep\n: DIST,4,AN0,022E,7.94,8.03,0.00,3.44,AN1,9280,7.95,0.00,0.00,5.68,AN2,DCAE,0.00,8.03,0.00,7.76,AN3,5431,0.00,0.00,0.00,8.73,POS,6.95,5.37,-1.97,52
    # lec\n: POS,7.10,5.24,-2.03,53
    data = {}
    # parse csv
    raw_elem = raw_string.split(',')
    num_anc = int(raw_elem[1])
    data['anc_num'] = int(raw_elem[1])
    for i in range(num_anc):
        data[raw_elem[2+6*i]] = {}
        data[raw_elem[2+6*i]]['anc_id'] = raw_elem[2+6*i+1]
        data[raw_elem[2+6*i]]['x'] = float(raw_elem[2+6*i+2])
        data[raw_elem[2+6*i]]['y'] = float(raw_elem[2+6*i+3])
        data[raw_elem[2+6*i]]['z'] = float(raw_elem[2+6*i+4])
        data[raw_elem[2+6*i]]['dist_to'] = float(raw_elem[2+6*i+5])
    data['est_pos'] = {}
    data['est_pos']['x'] = float(raw_elem[-4])
    data['est_pos']['y'] = float(raw_elem[-3])
    data['est_pos']['z'] = float(raw_elem[-2])
    data['est_qual'] = float(raw_elem[-1])
    return data


if __name__ == "__main__":
    com_ports = get_tag_serial_port()
    tagport = com_ports.pop()
    assert len(com_ports) == 0
    # In Python the readline timeout is set in the serialport init part
    t = serial.Serial(tagport, baudrate=115200, timeout=3.0)
    # Pause for 1 sec after establishment
    time.sleep(0.5)
    # Double enter (carriage return) as specified by Decawave
    t.write(b'\x0D\x0D')
    t.reset_input_buffer()

    # By default the update rate is 10Hz/100ms. Check again for data flow
    # if data is flowing before getting the device ID, stop it.
    if is_reporting_loc(t):
        t.write(b'\x6C\x65\x63\x0D')
        time.sleep(0.1)

    sys_info = get_sys_info(t)
    tag_id = sys_info.get("device_id") 
    upd_rate = sys_info.get("upd_rate") 
    # type "lec\n" to the dwm shell console to activate data reporting
    t.write(b'\x6C\x65\x63\x0D')
    time.sleep(0.1)
    assert is_reporting_loc(t, timeout=upd_rate/10)
    
    # location data flow is confirmed. Start publishing to localhost (MQTT)
    sys.stdout.write("["+str(datetime.utcnow().strftime('%H:%M:%S.%f'))+"] Connecting to Broker...\n")
    tag_client = mqtt.Client("Tag:"+tag_id)
    # tag_client.on_publish = mqtt_on_publish
    tag_client.connect(MQTT_BROKER, MQTT_PORT)
    sys.stdout.write("["+str(datetime.utcnow().strftime('%H:%M:%S.%f'))+"] Connected to Broker! Publishing\n")
    t.reset_input_buffer()

    super_frame = 0
    while True:
        data = str(t.readline(), encoding="UTF-8").rstrip()
        json_dic = make_json_dic(data)
        json_dic['tag_id'] = tag_id
        json_dic['superFrameNumber'] = super_frame
        json_data = json.dumps(json_dic)
        tag_client.publish("Tag/{}/Uplink/Location".format(tag_id[-4:]), json_data)
        super_frame += 1
    t.close()
