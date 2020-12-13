import os, platform, sys

import serial, glob, re
import time
from datetime import datetime

import subprocess, atexit, signal
import paho.mqtt.client as mqtt

from proximity_sensor import proximity_init, proximity_start

import json


def timestamp_log(incl_UTC=False):
    """ Get the timestamp for the stdout log message
        
        :returns:
            string format local timestamp with option to include UTC 
    """
    local_timestp = "["+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))+" local] "
    utc_timestp = "["+str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))+" UTC] "
    if incl_UTC:
        return local_timestp + utc_timestp
    else:
        return local_timestp


def mqtt_on_publish(client, data, result):
    # TODO: Define actions to take if mqtt_on_publish is needed
    pass


def is_uwb_shell_ok(serialport):
    """ Detect if the DWM1001 Tag's shell console is responding to \x0D\x0D
        
        :returns:
            True or False
    """
    serialport.reset_input_buffer()
    serialport.write(b'\x0D\x0D')
    time.sleep(0.1)
    sys.stdout.write(str(serialport.read(serialport.in_waiting))+'\n')
    if serialport.in_waiting:
        return True
    else:
        return False


def get_tag_serial_port(verbose=False):
    """ Detect the serial port name of DWM1001 Tag

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            return DWM1001 tag serial port name and make sure it is closed
    """
    if verbose:
        sys.stdout.write(timestamp_log() + "Fetching serialport...\n")
    ports = []
    import serial.tools.list_ports
    if sys.platform.startswith('win'):
        # assume there is only one J-Link COM port
        # ports += [str(i).split(' - ')[0]
        #             for  i in serial.tools.list_ports.comports() 
        #             if "JLink" in str(i)]
        ports = ['COM5']
    elif sys.platform.startswith('linux'):
        # the UART between RPi adn DWM1001-Dev is designated as serial0
        # with the drivers installed. 
        # see Section 4.3.1.2 of DWM1001-Firmware-User-Guide
        if re.search("raspberrypi", str(os.uname())):
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
        except BaseException as e:
            print("Wrong serial port detected for UWB tag")
            raise e
    if verbose:
        sys.stdout.write(timestamp_log() + "Serialport fetched as: " + str(ports))
    return ports


def on_exit(serialport, verbose=False):
    """ On exit callbacks to make sure the serialport is closed when
        the program ends.
    """
    if verbose:
        sys.stdout.write(timestamp_log() + "Serial port {} closed on exit\n".format(serialport.port))
    serialport.close()


def available_ttys(portlist):
    """ Generator to yield all available ports that are not locked by flock.
        Filters out the ports that are already opened. Preventing the program
        from running on multilple processes.
        
        Notice: if the other processes don't use flock, that process(es) will
        still be able to open the port, skipping the flock protection.
        
        Only works for POSIX/LINUX environment. 
        
        :yield:timestamp_log() + "Port is busy\n"
            Comports that aren't locked by flock.
    """
    for tty in portlist:
        try:
            port = serial.Serial(port=tty[0])
            if port.isOpen():
                try:
                    fcntl.flock(port.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except (IOError, BlockingIOError):
                    sys.stdout.write(timestamp_log() + "Port is busy\n")
                else:
                    yield port
        except serial.SerialException as ex:
            print('Port {0} is unavailable: {1}'.format(tty, ex))


def is_reporting_loc(serialport, timeout=2):
    """ Detect if the DWM1001 Tag is running on data reporting mode
        
        :returns:
            True or False
    """
    init_bytes_avail = serialport.in_waiting
    time.sleep(timeout)
    final_bytes_avail = serialport.in_waiting
    if final_bytes_avail - init_bytes_avail > 0:
        time.sleep(0.1)
        return True
    time.sleep(0.1)
    return False


def get_sys_info(serial_port, verbose=False):
    """ Get the system config information of the tag device through UART

        :returns:
            Dictionary of system information
    """
    if verbose:
        sys.stdout.write(timestamp_log() + "Fetching system information of UWB...\n")
    sys_info = {}
    if is_reporting_loc(serial_port):
        serial_port.write(b'\x6C\x65\x63\x0D')
        time.sleep(0.1)
    # Write "si" to show system information of DWM1001
    serial_port.reset_input_buffer()
    serial_port.write(b'\x73\x69\x0D')
    time.sleep(0.1)
    byte_si = serial_port.read(serial_port.in_waiting)
    si = str(byte_si)
    serial_port.reset_input_buffer()
    if verbose:
        sys.stdout.write(timestamp_log() + "Raw system info fetched as: \n" + str(byte_si, encoding="UTF-8") + "\n")
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


def parse_uart_init(serial_port, mqtt_broker, mqtt_port):
    # register the callback functions when the service ends
    # atexit for regular exit, signal.signal for system kills    
    atexit.register(on_exit, t, True)
    signal.signal(signal.SIGTERM, on_killed)
    # Pause for 0.1 sec after establishment
    time.sleep(0.1)
    # Double enter (carriage return) as specified by Decawave
    serial_port.write(b'\x0D\x0D')
    time.sleep(0.1)
    serial_port.reset_input_buffer()

    # By default the update rate is 10Hz/100ms. Check again for data flow
    # if data is flowing before getting the device ID, stop it.
    if is_reporting_loc(t):
        serial_port.write(b'\x6C\x65\x63\x0D')
        time.sleep(0.1)

    
def report_uart_data(serial_port):
    sys_info = get_sys_info(serial_port)
    tag_id = sys_info.get("device_id") 
    upd_rate = sys_info.get("upd_rate") 
    # type "lec\n" to the dwm shell console to activate data reporting
    serial_port.write(b'\x6C\x65\x63\x0D')
    time.sleep(0.1)
    assert is_reporting_loc(t, timeout=upd_rate/10)
    
    # location data flow is confirmed. Start publishing to localhost (MQTT)
    sys.stdout.write(timestamp_log() + "Connecting to Broker...\n")
    tag_client = mqtt.Client("Tag:"+tag_id)
    # tag_client.on_publish = mqtt_on_publish
    tag_client.connect(MQTT_BROKER, MQTT_PORT)
    sys.stdout.write(timestamp_log() + "Connected to Broker! Publishing\n")
    serial_port.reset_input_buffer()

    super_frame = 0
    while True:
        try:
            data = str(serial_port.readline(), encoding="UTF-8").rstrip()
            if not data[:4] == "DIST":
                continue
            json_dic = make_json_dic(data)
            json_dic['tag_id'] = tag_id
            json_dic['superFrameNumber'] = super_frame
            json_data = json.dumps(json_dic)
            tag_client.publish("Tag/{}/Uplink/Location".format(tag_id[-4:]), json_data, qos=0, retain=True)
            super_frame += 1
        except Exception as exp:
            data = str(serial_port.readline(), encoding="UTF-8").rstrip()
            sys.stdout.write(timestamp_log() + data)
            raise exp

if __name__ == "__main__":
    
    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883
    sys.stdout.write(timestamp_log() + "MQTT publisher service started. PID: {}\n".format(os.getpid()))
    com_ports = get_tag_serial_port()
    tagport = com_ports.pop()
    assert len(com_ports) == 0
    
    # In Python the readline timeout is set in the serialport init part
    t = serial.Serial(tagport, baudrate=115200, timeout=3.0)
    
    def on_killed(signum, frame):
        """ Closure function as handler to signal.signal in order to pass serialport name
        """
        # if killed by UNIX, no need to execute on_exit callback
        atexit.unregister(on_exit)
        sys.stdout.write(timestamp_log() + "Serial port {} closed on killed\n".format(t.port))
        t.close()
    
    if sys.platform.startswith('linux'):
        import fcntl
        try:
            fcntl.flock(t.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, BlockingIOError) as exp:
            sys.stdout.write(timestamp_log() + "Port is busy. Another process is accessing the port. \n")
            raise exp
        else:
            sys.stdout.write(timestamp_log() + "Port is ready.\n")
    
    # main thread is used for uart
    # a secondary thread is used for proximity sensor
    import threading

    def proximity_thread_job():
        TRIG=26
        ECHO=16
        PROXI=15
        INTERVAL=2
        startt = time.time()
        try:
            proximity_init(trig=TRIG, echo=ECHO)
            while True:
                dist = proximity_start(trig=TRIG, echo=ECHO, proximity_threshold=PROXI)
                if not dist:
                    print("Non in the range, greater than 15cm")
                else:
                    print("Distance: {} cm".format(dist))
                time.sleep(INTERVAL)
        except BaseException as e:
            raise(e)
        finally:
            stopt = time.time()
            print("program running time: {} seconds".format(stopt - startt))

    added_thread = threading.Thread(target=proximity_thread_job, name="Proximity Sensor")
    added_thread.start()
    
    try:
        parse_uart_init(t, MQTT_BROKER, MQTT_PORT)
    except BaseException as e:
        sys.stdout.write(timestamp_log() + "Initialization failed. \n")
        raise e
    try:
        report_uart_data(t)
    except BaseException as e:
        sys.stdout.write(timestamp_log() + "Reporting process failed. \n")
        raise e

    