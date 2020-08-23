import os, platform, sys

import serial, glob, re
import time

import subprocess
import paho.mqtt.client as mqtt

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
    print("Connecting to Broker...")
    tag_client = mqtt.Client("Tag:"+tag_id)
    # tag_client.on_publish = mqtt_on_publish
    tag_client.connect(MQTT_BROKER, MQTT_PORT)

    t.reset_input_buffer()
    while True:
        data = str(t.readline(), encoding="UTF-8").rstrip()
        tag_client.publish("Tag/{}/Uplink/Location".format(tag_id[-4:]), data)
    t.close()