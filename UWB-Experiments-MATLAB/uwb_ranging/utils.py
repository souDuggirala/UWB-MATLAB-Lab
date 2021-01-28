from datetime import datetime
import sys, time, json, re


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


def on_killed(signum, frame):
    """ Closure function as handler to signal.signal in order to pass serialport name
    """
    # if killed by UNIX, no need to execute on_exit callback
    atexit.unregister(on_exit)
    sys.stdout.write(timestamp_log() + "Serial port {} closed on killed\n".format(t.port))
    if sys.platform.startswith('linux'):
        import fcntl
        fcntl.flock(t, fcntl.LOCK_UN)
    t.close()


def load_config_json(json_path):
    try:
        with open(json_path) as f:
            return json.load(f)
    except BaseException as e:
        sys.stdout.write(timestamp_log() + "failed to load JSON configuration file\n")
        raise e
    

def is_uwb_shell_ok(serialport, verbose=False):
    """ Detect if the DWM1001 Tag's shell console is responding to \x0D\x0D
        
        :returns:
            True or False
    """
    serialport.reset_input_buffer()
    serialport.write(b'\x0D\x0D')
    time.sleep(0.1)
    if verbose:
        sys.stdout.write(str(serialport.read(serialport.in_waiting))+'\n')
    if serialport.in_waiting:
        return True
    else:
        return False


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


def port_available_check(port):
    if sys.platform.startswith('linux'):
        import fcntl
    try:
        fcntl.flock(port, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (IOError, BlockingIOError) as exp:
        sys.stdout.write(timestamp_log() + "Port is busy. Another process is accessing the port. \n")
        raise exp
    else:
        sys.stdout.write(timestamp_log() + "Port is ready.\n")

    
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
    all_anc_id = []
    for i in range(num_anc):
        data[raw_elem[2+6*i+1]] = {}
        data[raw_elem[2+6*i+1]]['anc_id'] = raw_elem[2+6*i]
        all_anc_id.append(raw_elem[2+6*i+1])
        data[raw_elem[2+6*i+1]]['x'] = float(raw_elem[2+6*i+2])
        data[raw_elem[2+6*i+1]]['y'] = float(raw_elem[2+6*i+3])
        data[raw_elem[2+6*i+1]]['z'] = float(raw_elem[2+6*i+4])
        data[raw_elem[2+6*i+1]]['dist_to'] = float(raw_elem[2+6*i+5])
    data['all_anc_id'] = all_anc_id
    data['est_pos'] = {}
    data['est_pos']['x'] = float(raw_elem[-4])
    data['est_pos']['y'] = float(raw_elem[-3])
    data['est_pos']['z'] = float(raw_elem[-2])
    data['est_qual'] = float(raw_elem[-1])
    return data