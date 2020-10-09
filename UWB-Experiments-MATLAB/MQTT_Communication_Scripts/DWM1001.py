import time, serial
import inspect


ERROR_CLS = {
        0 : "OK",
        1 : "unknown command or broken TLV frame",
        2 : "internal error",
        3 : "invalid parameter",
        4 : "busy",
        5 : "operation not permitted",
    }

SCALE_TO_MM = {
        "mm"    : 1,
        "cm"    : 10,
        "m"     : 1000,
        }

SCALE_TO_100MS = {
        "100ms" : 1,
        "s"     : 10,
        "min"   : 600,
        }

# Show hexadecimal in string format
def hex_in_string(bytes_to_show):
    return ''.join('0x{:02x} '.format(letter) for letter in bytes_to_show)

def verbose_request(TLV_bytes):
    _func_name = inspect.stack()[1][3]
    print("[{}] TLV Written to serial: {}".format(_func_name, hex_in_string(TLV_bytes)))

def verbose_response(TLV_bytes, err_code=1):
    _func_name = inspect.stack()[1][3]
    print("[{}] Responded TLV: {}".format(_func_name, hex_in_string(TLV_bytes)))
    if err_code == 0:
        print("[{}] Success".format(_func_name))
    else:
        print("[{}] Error; error code: {}, message: {}"
        .format(_func_name, err_code, ERROR_CLS[err_code]))
    

def hexTodemical(argv):

    factor=1
    res=0

    for hex in argv:
        res+=(int(hex,16))*factor
        factor*=256

    return res

#helpers functions end
#------------------------------------------------------------------------------------------#
############################################################################################
############################################################################################
############################################################################################
#------------------------------------------------------------------------------------------#
# DWM1001 API functions start

def dwm_pos_set(t, coords, qual_fact_percent, unit="mm", verbose=False):
    """ API Section 5.3.1
    API Sample TLV Request:
    Type    |Length |Value-position
    0x01    |0x0D   |x (4B, little), y (4B, little), z (4B, little), 
                    |percentage quality factor (1B)

    API Sample TLV Resonse:
    Type    |Length |Value-err_code
    0x40    |0x01   |0x00
    ------------------------------------
    :return: 
        error_code
    """ 
    _func_name = inspect.stack()[0][3]
    if unit not in ("mm", "cm", "m"):
        raise ValueError("[{}]: Invalid input unit".format(_func_name))
    
    TYPE, LENGTH, VALUE = b'\x01', b'\x0D', b''
    
    [x, y, z] = [c * SCALE_TO_MM[unit] for c in coords]
    pos_bytes = b''
    for dim in [x, y, z]:
        pos_bytes += dim.to_bytes(4, byteorder='little', signed=True)
    pos_bytes += qual_fact_percent.to_bytes(1, byteorder='little', signed=False)
    
    VALUE = pos_bytes
    output_bytes = TYPE + LENGTH + VALUE
    
    t.reset_output_buffer()
    t.reset_input_buffer()
    t.write(output_bytes)
    if verbose:
        verbose_request(output_bytes)   
    TLV_response = t.read(3)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 1
    if verbose:
        verbose_response(TLV_response, err_code)
    # Parsing the returned TLV value
    # do nothing
    return err_code


def dwm_pos_get(t, verbose=False):
    """ API Section 5.3.2
    API Sample TLV Request:
    Type    |Length
    0x02    |0x00  

    API Sample TLV Resonse:
    Type    |Length |Value-err_code |...
    0x40    |0x01   |0x00           |...
    Type    |Length |Value-position
    0x41    |0x0D   |x (4B, little), y (4B, little), z (4B, little), 
                    |percentage quality factor (1B)
    ------------------------------------
    :return: 
        [x, y, z, qual_fact_percent, err_code] unit in millimeter
    """ 
    _func_name = inspect.stack()[0][3]
    TYPE, LENGTH, VALUE = b'\x02', b'\x00', b''  
    output_bytes = TYPE + LENGTH + VALUE

    t.reset_output_buffer()
    t.reset_input_buffer()
    t.write(output_bytes)
    if verbose:
        verbose_request(output_bytes)
    TLV_response = t.read(18)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 1
    if verbose:
        verbose_response(TLV_response, err_code)
    
    # Parsing the returned TLV value
    _dim_idx_pos = [5, 9, 13]
    x, y, z, qual_fact_percent = [float("nan")] * 4
    [x, y, z] = [
        int.from_bytes(dim_bytes, byteorder='little', signed=True) 
        for dim_bytes in [TLV_response[idx:idx+4] for idx in _dim_idx_pos]
        ]
    qual_fact_percent = TLV_response[-1]

    return [x, y, z, qual_fact_percent, err_code]


def dwm_upd_rate_set(t, act_upd_intval, sta_upd_intval, unit="100ms", verbose=False):
    """ API Section 5.3.3
    API Sample TLV Request:
    Type    |Length |Value-update_rate
    0x03    |0x04   |active/stationary position update interval in multiples
                    |of 100 milliseconds (2B each, little, unsigned)

    API Sample TLV Resonse:
    Type    |Length |Value-err_code
    0x40    |0x01   |0x00
    ------------------------------------
    :return: 
        error_code
    """ 
    _func_name = inspect.stack()[0][3]
    if unit not in ("100ms", "s", "min"):
        raise ValueError("[{}]: Invalid input unit".format(_func_name))
    
    TYPE, LENGTH, VALUE = b'\x03', b'\x04', b''
    
    [act_upd_intval, sta_upd_intval] = [i * SCALE_TO_100MS[unit] 
                                for i in [act_upd_intval, sta_upd_intval]]
    if act_upd_intval > sta_upd_intval:
        raise ValueError("[{}]: Stationary interval must be greater or equal to \
                          Active interval".format(_func_name))
    upd_bytes = b''
    for upd in [act_upd_intval, sta_upd_intval]:
        upd_bytes += upd.to_bytes(2, byteorder='little', signed=False)
    
    VALUE = upd_bytes
    output_bytes = TYPE + LENGTH + VALUE
    
    t.reset_output_buffer()
    t.reset_input_buffer()
    t.write(output_bytes)
    if verbose:
        verbose_request(output_bytes)   
    TLV_response = t.read(3)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 1
    if verbose:
        verbose_response(TLV_response, err_code)
    # Parsing the returned TLV value
    # do nothing
    return err_code

def dwm_upd_rate_get(t, verbose=False):
    """ API Section 5.3.4
    API Sample TLV Request:
    Type    |Length
    0x04    |0x00  

    API Sample TLV Resonse:
    Type    |Length |Value-err_code |...
    0x40    |0x01   |0x00           |...
    Type    |Length |Value-update_rate
    0x45    |0x04   |active/stationary position update interval in multiples
                    |of 100 milliseconds (2B each, little, unsigned)
    ------------------------------------
    :return: 
        [act_upd_intval, sta_upd_intval, err_code] unit in milliseconds
    """ 
    TYPE, LENGTH, VALUE = b'\x04', b'\x00', b''
    output_bytes = TYPE + LENGTH + VALUE

    t.reset_output_buffer()
    t.reset_input_buffer()
    t.write(output_bytes)
    if verbose:
        verbose_request(output_bytes)
    TLV_response = t.read(9)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 1
    if verbose:
        verbose_response(TLV_response, err_code)
    
    # Parsing the returned TLV value
    _upd_idx_pos = [5, 7]
    act_upd_intval, sta_upd_intval = [float("nan")] * 2
    [act_upd_intval, sta_upd_intval] = [
        100 * int.from_bytes(upd_bytes, byteorder='little', signed=False) 
        for upd_bytes in [TLV_response[idx:idx+2] for idx in _upd_idx_pos]
        ]
    
    return [act_upd_intval, sta_upd_intval, err_code]


def dwm_cfg_tag_set(tag,t):

    TYPE=b'\x07'
    LENGTH=b'\x02'
    # t.write(TYPE)
    # t.write(LENGTH)
    t.write(TYPE + LENGTH)

    SHOW_OPE_INFO(t.portstr,TYPE,LENGTH)
    ######################################
    t.write(b"\xCE\x00")## NEDD MODIFY (SET)
    ######################################

    time.sleep(1)
    num=t.inWaiting()
    print("num",num)
    if num:
        str = t.read(num)
        serial.Serial.close(t)
        if format(str[-1],"02x")=="01":
            print("error")
        else:
            print("set success")
    


def dwm_cfg_anchor_set(t):

    TYPE=b'\x07'
    LENGTH=b'\x02'
    # t.write(TYPE)
    # t.write(LENGTH)
    t.write(TYPE + LENGTH)
    #######################################
    t.write(b"\xCE\x00")#### NEED MODIFY (SET)
    #######################################
    print("using ")
    print("written to serial: ", TYPE,type(b'\x04'))
    print("written to serial: ", LENGTH,type(b'\x00'))

    time.sleep(1)
    num=t.inWaiting()
    print("num",num)
    if num:
        str = t.read(num)
        serial.Serial.close(t)
        if format(str[-1],"02x")=="01":
            print("error")
        else:
            print("set success")

def dwm_cfg_get():
    return -1

def dwm_sleep():
    return -1

def dwm_anchor_list_get():
    return -1

def dwm_loc_get():
    return -1

def dwm_baddr_set():
    return -1

def dwm_baddr_get():
    return -1

def dwm_stnry_cfg_set():
    return -1

def dwm_stnry_cfg_get():
    return -1

def dwm_factory_reset():
    return -1 

def dwm_reset():
    return -1

def dwm_ver_get():
    return -1

def dwm_uwb_cfg_set():
    return -1

def dwm_uwb_cfg_get():
    return -1 

def dwm_usr_data_read():
    return -1 

def dwm_usr_data_write():
    return -1 

def dwm_label_read():
    return -1 

def dwm_label_write():
    return -1 

def dwm_gpio_cfg_output_bytes():
    return -1 

def dwm_gpio_cfg_input():
    return -1 

def dwm_gpio_value_set():
    return -1

def dwm_gpio_value_get():
    return -1 

def dwm_gpio_value_toggle():
    return -1 

def dwm_panid_set():
    return -1 

def dwm_panid_get():
    return -1 

def dwm_nodeid_get(t):
    t.write(b'\x30\x00')
    time.sleep(1)
    num=t.inWaiting()
    print("num",num)
    if num:
        str = t.read(num)
        serial.Serial.close(t)
        hex_in_string(str)

def dwm_status_get():
    return -1 

def dwm_int_cfg_set():
    return -1 

def dwm_int_cfg_get():
    return -1 

def dwm_enc_key_set():
    return -1 

def dwm_enc_key_clear():
    return -1 

def dwm_nvm_usr_data_set():
    return -1 

def dwm_nvm_usr_data_get():
    return -1  

def dwm_gpio_irq_cfg():
    return -1  

def dwm_gpio_irq_dis():
    return -1 

def dwm_i2c_read():
    return -1 

def dwm_i2c_write():
    return -1 

def dwm_evt_listener_register():
    return -1 

def dwm_evt_wait():
    return -1 

def dwm_wake_up():
    return -1   

def dwm_bh_status_get():
    return -1 

def dwm_backhaul_xfer():
    return -1 
#######################----------
#################################