import time, serial
import inspect


ERROR_CLS = {
        0 : "OK",
        1 : "unknown command or broken TLV frame",
        2 : "internal error",
        3 : "invalid parameter",
        4 : "busy",
        5 : "operation not permitted",
        6 : "unknown error (non API error)"
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

def hex_in_string(bytes_to_show):
    """ Show hexadecimal in string format
    """
    return ''.join('0x{:02x} '.format(letter) for letter in bytes_to_show)

def verbose_request(TLV_bytes):
    _func_name = inspect.stack()[1][3]
    print("[{}] TLV Written to serial: {}".format(_func_name, hex_in_string(TLV_bytes)))

def verbose_response(TLV_bytes, err_code, func_name):
    print("[{}] Responded TLV: {}".format(func_name, hex_in_string(TLV_bytes)))
    if err_code == 0:
        print("[{}] Success".format(func_name))
    else:
        print("[{}] Error; error code: {}, message: {}"
        .format(func_name, err_code, ERROR_CLS[err_code]))
    
def error_handler(TLV_response, err_code, func_name):
    if err_code != 0:
        raise ValueError("[{}]: Error returned as code {}: {}."
                        .format(func_name, err_code, ERROR_CLS[err_code]))

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
    This API function set the default position of the node. Default position is not used when in tag mode
    but is stored anyway so the module can be configured to anchor mode and use the value previously
    set by dwm_pos_set. This call does a write to internal flash in case of new value being set, hence
    should not be used frequently as can take, in worst case, hundreds of milliseconds.
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
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 6
    if verbose:
        verbose_response(TLV_response, err_code, _func_name)
    error_handler(TLV_response, err_code, _func_name)
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
    This API function obtain position of the node. If the current position of the node is not available, the
    default position previously set by dwm_pos_set will be returned.
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
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 6
    if verbose:
        verbose_response(TLV_response, err_code, _func_name)
    error_handler(TLV_response, err_code, _func_name)
    
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
    This API function sets the update rate and the stationary update rate of the position in unit of 100
    milliseconds. Stationary update rate must be greater or equal to normal update rate. This call does a
    write to the internal flash in case of new value being set, hence should not be used frequently as can
    take, in worst case, hundreds of milliseconds.
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
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 6
    if verbose:
        verbose_response(TLV_response, err_code, _func_name)
    error_handler(TLV_response, err_code, _func_name)
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
    This API function gets position update rate. 
    ------------------------------------
    :return: 
        [act_upd_intval, sta_upd_intval, err_code] unit in milliseconds
    """ 
    _func_name = inspect.stack()[0][3]

    TYPE, LENGTH, VALUE = b'\x04', b'\x00', b''
    output_bytes = TYPE + LENGTH + VALUE

    t.reset_output_buffer()
    t.reset_input_buffer()
    t.write(output_bytes)
    if verbose:
        verbose_request(output_bytes)
    TLV_response = t.read(9)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 6
    if verbose:
        verbose_response(TLV_response, err_code, _func_name)
    error_handler(TLV_response, err_code, _func_name)
    
    # Parsing the returned TLV value
    _upd_idx_pos = [5, 7]
    act_upd_intval, sta_upd_intval = [float("nan")] * 2
    [act_upd_intval, sta_upd_intval] = [
        100 * int.from_bytes(upd_bytes, byteorder='little', signed=False) 
        for upd_bytes in [TLV_response[idx:idx+2] for idx in _upd_idx_pos]
        ]
    
    return [act_upd_intval, sta_upd_intval, err_code]


def dwm_cfg_tag_set(t, 
                    stnry_en=True, 
                    meas_mode=0, 
                    low_power_en=False, 
                    loc_engine_en=True, 
                    enc_en=False, 
                    led_en=True, 
                    ble_en=True, 
                    uwb_mode=2, 
                    fw_upd_en=True, 
                    verbose=False):
    """ API Section 5.3.5
    API Sample TLV Request:
    Type    |Length |Value-cfg_tag
    0x05    |0x02   |16-bit integer, 2-byte, configuration of the tag
                    |(* BYTE 1 *)
                    |(bits 3-7) reserved
                    |(bit 2) stnry_en
                    |(bits 0-1) meas_mode : 0 - TWR, 1-3 reserved
                    |(* BYTE 0 *)
                    |(bit 7) low_power_en
                    |(bit 6) loc_engine_en
                    |(bit 5) enc_en
                    |(bit 4) led_en
                    |(bit 3) ble_en
                    |(bit 2) fw_update_en
                    |(bits 0-1) uwb_mode 
    API Sample TLV Resonse:
    Type    |Length |Value-err_code
    0x40    |0x01   |0x00
    ------------------------------------
    This API function configures the node as tag with given options.
    BLE option can’t be enabled together with encryption otherwise the configuration is considered
    invalid and it is refused. Encryption can’t be enabled if encryption key is not set.
    This call does a write to internal flash in case of new value being set, hence should not be used
    frequently as can take, in worst case, hundreds of milliseconds. Note that this function only sets the
    configuration parameters. To make effect of the settings, users should issue a reset command
    (dwm_reset()), see section 5.3.13 for more detail.
    ------------------------------------
    :return: 
        error_code
    """ 
    _func_name = inspect.stack()[0][3]
    
    TYPE, LENGTH, VALUE = b'\x05', b'\x02', b''
    
    if ble_en and enc_en:
        raise ValueError("[{}]: Refused. BLE option can’t be enabled together \
                          with encryption.".format(_func_name))
    cfg_tag_byte_1 = 0b00000000
    cfg_tag_byte_0 = 0b00000000
    
    cfg_tag_byte_1 = cfg_tag_byte_1 | (stnry_en << 5)
    cfg_tag_byte_1 = cfg_tag_byte_1 | (meas_mode << 6)
    
    cfg_tag_byte_0 = cfg_tag_byte_0 | (low_power_en << 0)
    cfg_tag_byte_0 = cfg_tag_byte_0 | (loc_engine_en << 1)
    cfg_tag_byte_0 = cfg_tag_byte_0 | (enc_en << 2)
    cfg_tag_byte_0 = cfg_tag_byte_0 | (led_en << 3)
    cfg_tag_byte_0 = cfg_tag_byte_0 | (ble_en << 4)
    cfg_tag_byte_0 = cfg_tag_byte_0 | (fw_upd_en << 5)
    cfg_tag_byte_0 = cfg_tag_byte_0 | (uwb_mode << 6)
    
    VALUE = cfg_tag_byte_0.to_bytes(1, byteorder='little', signed=False) + \
            cfg_tag_byte_1.to_bytes(1,  byteorder='little', signed=False)
    output_bytes = TYPE + LENGTH + VALUE
    
    t.reset_output_buffer()
    t.reset_input_buffer()
    t.write(output_bytes)
    if verbose:
        verbose_request(output_bytes)   
    TLV_response = t.read(3)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 6
    if verbose:
        verbose_response(TLV_response, err_code, _func_name)
    error_handler(TLV_response, err_code, _func_name)
    # Parsing the returned TLV value
    # do nothing
    return err_code
    

def dwm_cfg_anchor_set( t, 
                        initiator=True, 
                        bridge=False, 
                        enc_en=False, 
                        led_en=True, 
                        ble_en=True, 
                        uwb_mode=2, 
                        fw_upd_en=True, 
                        verbose=False):
    """ API Section 5.3.6
    API Sample TLV Request:
    Type    |Length |Value-cfg_anchor
    0x07    |0x02   |16-bit integer, 2-byte, configuration of the anchor
                    |(* BYTE 1 *)
                    |(bits 2-7) reserved
                    |(bits 0-1) reserved
                    |(* BYTE 0 *)
                    |(bit 7) initiator
                    |(bit 6) bridge
                    |(bit 5) enc_en
                    |(bit 4) led_en
                    |(bit 3) ble_en
                    |(bit 2) fw_update_en
                    |(bits 0-1) uwb_mode 
    API Sample TLV Resonse:
    Type    |Length |Value-err_code
    0x40    |0x01   |0x00
    ------------------------------------
    Configure node as anchor with given options. BLE option can’t be enabled together with encryption
    otherwise the configuration is considered invalid and it is refused.
    Encryption can’t be enabled if encryption key is not set. This call requires reset for new configuration
    to take effect (dwm_reset). Enabling encryption on initiator will cause automatic enabling of
    encryption of all nodes that have the same encryption key set (dwm_enc_key_set). This allows to
    enable encryption for whole network that has the same pan ID (network ID) and the same
    encryption key remotely from one place.
    This call does a write to internal flash in case of new value being set, hence should not be used
    frequently and can take in worst case hundreds of milliseconds.
    ------------------------------------
    :return: 
        error_code
    """ 
    _func_name = inspect.stack()[0][3]
    
    TYPE, LENGTH, VALUE = b'\x07', b'\x02', b''
    
    if ble_en and enc_en:
        raise ValueError("[{}]: Refused. BLE option can’t be enabled together \
                          with encryption.".format(_func_name))
    cfg_anc_byte_1 = 0b00000000
    cfg_anc_byte_0 = 0b00000000

    cfg_anc_byte_0 = cfg_anc_byte_0 | (initiator << 0)
    cfg_anc_byte_0 = cfg_anc_byte_0 | (bridge << 1)
    cfg_anc_byte_0 = cfg_anc_byte_0 | (enc_en << 2)
    cfg_anc_byte_0 = cfg_anc_byte_0 | (led_en << 3)
    cfg_anc_byte_0 = cfg_anc_byte_0 | (ble_en << 4)
    cfg_anc_byte_0 = cfg_anc_byte_0 | (fw_upd_en << 5)
    cfg_anc_byte_0 = cfg_anc_byte_0 | (uwb_mode << 6)
    
    VALUE = cfg_anc_byte_0.to_bytes(1, byteorder='little', signed=False) + \
            cfg_anc_byte_1.to_bytes(1,  byteorder='little', signed=False)
    output_bytes = TYPE + LENGTH + VALUE
    
    t.reset_output_buffer()
    t.reset_input_buffer()
    t.write(output_bytes)
    if verbose:
        verbose_request(output_bytes)   
    TLV_response = t.read(3)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 6
    if verbose:
        verbose_response(TLV_response, err_code, _func_name)
    error_handler(TLV_response, err_code, _func_name)
    # Parsing the returned TLV value
    # do nothing
    return err_code

def dwm_cfg_get(t, verbose=False):
    """ API Section 5.3.7
    API Sample TLV Request:
    Type    |Length
    0x08    |0x00  

    API Sample TLV Resonse:
    Type    |Length |Value-err_code |...
    0x40    |0x01   |0x00           |...
    Type    |Length |Value-cfg_node
    0x45    |0x04   |16-bit integer, configuration of the node
                    |(* BYTE 1 *)
                    |(bit 5) mode : 0 - tag, 1 - anchor
                    |(bit 4) initiator
                    |(bit 3) bridge
                    |(bit 2) stnry_en
                    |(bits 0-1) meas_mode : 0 - TWR, 1-3 not supported
                    |(* BYTE 0 *)
                    |(bit 7) low_power_en
                    |(bit 6) loc_engine_en
                    |(bit 5) enc_en 
                    |(bit 4) led_en
                    |(bit 3) ble_en
                    |(bit 2) fw_update_en
                    |(bits 0-1) uwb_mode
    ------------------------------------
    This API function obtains the configuration of the node.
    ------------------------------------
    :return: 
        [node_cfg, err_code]
    """ 
    _func_name = inspect.stack()[0][3]

    TYPE, LENGTH, VALUE = b'\x08', b'\x00', b''
    output_bytes = TYPE + LENGTH + VALUE

    t.reset_output_buffer()
    t.reset_input_buffer()
    t.write(output_bytes)
    if verbose:
        verbose_request(output_bytes)
    
    cfg_node_byte_1 = 0b00000000
    cfg_node_byte_0 = 0b00000000

    TLV_response = t.read(7)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 6
    if verbose:
        verbose_response(TLV_response, err_code, _func_name)
    error_handler(TLV_response, err_code, _func_name)
    
    # Parsing the returned TLV value
    cfg_node_byte_0, cfg_node_byte_0_str = TLV_response[-2], bin(TLV_response[-2])[2:]
    cfg_node_byte_1, cfg_node_byte_1_str = TLV_response[-1], bin(TLV_response[-1])[2:]
    
    cfg_node = {
        "mode":         int(cfg_node_byte_1_str[5]),
        "initiator":    True if int(cfg_node_byte_1_str[4]) else False,
        "bridge":       True if int(cfg_node_byte_1_str[3]) else False,
        "stnry_en":     True if int(cfg_node_byte_1_str[2]) else False,
        "meas_mode":    int(cfg_node_byte_1_str[0:2], 2),
        "low_power_en": True if int(cfg_node_byte_0_str[7]) else False,
        "loc_engine_en":True if int(cfg_node_byte_0_str[6]) else False,
        "enc_en":       True if int(cfg_node_byte_0_str[5]) else False,
        "led_en":       True if int(cfg_node_byte_0_str[4]) else False,
        "ble_en":       True if int(cfg_node_byte_0_str[3]) else False,
        "fw_update_en": True if int(cfg_node_byte_0_str[2]) else False,
        "uwb_mode":     int(cfg_node_byte_0_str[0:2], 2),
    }
    
    return [cfg_node, err_code]

def dwm_sleep(t, verbose=False):
    """ API Section 5.3.8
    API Sample TLV Request:
    Type    |Length
    0x0A    |0x00  
    API Sample TLV Resonse:
    Type    |Length |Value-err_code
    0x40    |0x01   |0x00
    ------------------------------------
    This API function puts the module into sleep mode. Low power option must be enabled otherwise an
    error will be returned.
    ------------------------------------
    """
    _func_name = inspect.stack()[0][3]

    TYPE, LENGTH, VALUE = b'\x0A', b'\x00', b''
    output_bytes = TYPE + LENGTH + VALUE

    t.reset_output_buffer()
    t.reset_input_buffer()
    t.write(output_bytes)
    if verbose:
        verbose_request(output_bytes)
    
    TLV_response = t.read(3)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 6
    if verbose:
        verbose_response(TLV_response, err_code, _func_name)
    error_handler(TLV_response, err_code, _func_name)
    
    return err_code


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