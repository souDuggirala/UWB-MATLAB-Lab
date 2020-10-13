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

def read_single_TLV_frame(port, cutoff_bytes=0):
    if not cutoff_bytes:
        _TL_header = port.read(2)
        if _TL_header:
            _frame_value = port.read(_TL_header[1])
            return _TL_header + _frame_value
        else:
            return b''
    else:
        return port.read(cutoff_bytes)
    
def read_all_TLV(port, expecting=0, timeout=0.5):
    if expecting:
        TLV_frames = [read_single_TLV_frame(port) for n in range(expecting)]
    else:
        TLV_frames = []
        _time_cnt = 0
        while port.inWaiting() or _time_cnt < timeout:
            if port.inWaiting():
                TLV_frames.append(read_single_TLV_frame(port))
                _time_cnt = 0
            elif _time_cnt < timeout:
                time.sleep(0.01)
                _time_cnt += 0.01
            else:
                break
    return TLV_frames

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
        print("[{}] Error with error code: {}, message: {}"
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
    Type    |Length |Value-position (13B)
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
    
    TLV_frames = read_all_TLV(t, expecting=1)
    TLV_response = b''.join(TLV_frames)
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
    Type    |Length |Value-position (13B)
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
    TLV_frames = read_all_TLV(t, expecting=2)
    TLV_response = b''.join(TLV_frames)
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
    Type    |Length |Value-update_rate (4B)
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
    TLV_frames = read_all_TLV(t, expecting=1)
    TLV_response = b''.join(TLV_frames)
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
    Type    |Length |Value-update_rate (4B)
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
    TLV_frames = read_all_TLV(t, expecting=2)
    TLV_response = b''.join(TLV_frames)
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
    Type    |Length |Value-cfg_tag (2B)
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
    BLE option can't be enabled together with encryption otherwise the configuration is considered
    invalid and it is refused. Encryption can't be enabled if encryption key is not set.
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
        raise ValueError("[{}]: Refused. BLE option can't be enabled together \
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
    TLV_frames = read_all_TLV(t, expecting=1)
    TLV_response = b''.join(TLV_frames)
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
    Type    |Length |Value-cfg_anchor (2B)
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
    Configure node as anchor with given options. BLE option can't be enabled together with encryption
    otherwise the configuration is considered invalid and it is refused.
    Encryption can't be enabled if encryption key is not set. This call requires reset for new configuration
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
        raise ValueError("[{}]: Refused. BLE option can't be enabled together \
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
    TLV_frames = read_all_TLV(t, expecting=1)
    TLV_response = b''.join(TLV_frames)
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
    Type    |Length |Value-cfg_node (2B)
    0x46    |0x02   |16-bit integer, configuration of the node
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

    TLV_frames = read_all_TLV(t, expecting=2)
    TLV_response = b''.join(TLV_frames)
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
    
    TLV_frames = read_all_TLV(t, expecting=1)
    TLV_response = b''.join(TLV_frames)
    err_code = TLV_response[2] if TLV_response[0:2] == b'\x40\x01' else 6
    if verbose:
        verbose_response(TLV_response, err_code, _func_name)
    error_handler(TLV_response, err_code, _func_name)
    
    return err_code


def dwm_anchor_list_get(t, verbose=False, timeout=5):
    """ API Section 5.3.9, modified by Zezhou Wang
    API Sample TLV Request:
    Type    |Length |Value
    0x0B    |0x01   |page_number

    page_number: when the returned values become greater than 253 Bytes (maximum TLV length), 
    it will separate into extra pages.
    
    API Sample TLV Resonse Example 1 (3 anchors):
    Type    |Length |Value-err_code |...
    0x40    |0x01   |0x00           |...
    Type    |Length |Value (1 + 16 * Anchors bytes).............................................           
    0x56    |0x31   |uint8_t (1B)               |...
                    |number of elements         |...
                    |encoded in the value       |...
                    |0x03                       |...
    |Value (Cont.) .........................................................................|..................................
    |uint16_t (2B)          |3×int32_t (12B)    |int8_t - RSSI (1B) |uint8_t - seat (1B)    |..................................
    |UWB address in little  |position coords xyz|                   |                       |(Cont.) anchor nr.2 anchor nr.3...
    |endian                 |in little endian   |                   |                       |..................................
    |-----------------------------------anchor nbr.1 (16B)----------------------------------|..................................

    Sample (4 anchors):
    "40 01 00 56 41 04" 
    "84 c5 (Addr)| 3c 05 00 00 (x) | da 07 00 00 (y) | f4 0b 00 00 (z) | b2 (RSSI) | 00 (seat)" 
    "0c 0c (Addr)| dc 05 00 00 (x) | c4 09 00 00 (y) | b8 0b 00 00 (z) | b2 (RSSI) | 01 (seat)" 
    "28 13 (Addr)| 18 06 00 00 (x) | ce 04 00 00 (y) | 52 0d 00 00 (z) | b3 (RSSI) | 02 (seat)" 
    "1c 9a (Addr)| 00 fa 00 00 (x) | 50 c3 00 00 (y) | 50 46 00 00 (z) | 81 (RSSI) | 04 (seat)"

    API Sample TLV Resonse Example 2 (no anchor):
    Type    |Length |Value-err_code
    0x40    |0x01   |0x00          
    Type    |Length |Value              
    0x56    |0x01   |uint8_t -              
                    |number of elements     
                    |encoded in the value   
                    |0x0F                   

    ------------------------------------
    This API function reads list of surrounding anchors. Works for anchors only. Anchors in the list can be
    from the same network or from the neighbor network as well.
    Requesting page number that ain't exist will make the device frozen. Power-off and restart is needed. 
    ------------------------------------
    :return:
        list of hash maps (key-value pairs for anchors), length unit in millimeter
    """
    _func_name = inspect.stack()[0][3]
    TYPE, LENGTH, VALUE = b'\x0B', b'\x01', b''

    _page_nbr = 0
    _anchor_bytes_nbr_by_page = []
    # collect raw bytes and determine how many pages
    while True:
        _page_polling_bytes = TYPE + LENGTH + _page_nbr.to_bytes(1, byteorder="little", signed=False)
        t.reset_output_buffer()
        t.reset_input_buffer()
        t.write(_page_polling_bytes)
        TLV_frames = read_all_TLV(t, expecting=2)
        _page_polling_response = TLV_frames[0]
        err_code = _page_polling_response[2] if _page_polling_response[0:2] == b'\x40\x01' else 6
        error_handler(_page_polling_response, err_code, _func_name)
        anchor_nbr_in_this_page = TLV_frames[1][2]
        if anchor_nbr_in_this_page != 0:
            anchor_bytes = TLV_frames[1][3:]
            if len(anchor_bytes) != anchor_nbr_in_this_page * 16:
                raise ValueError("[{}]: Bytes for anchors do not match specs: 16 bits per anchor on page {}. Expecting {} anchors. Got {} Bytes."
                                    .format(_func_name, _page_nbr, anchor_nbr_in_this_page, t.inWaiting()))
            if verbose:
                verbose_response(anchor_bytes, err_code, _func_name)
            _anchor_bytes_nbr_by_page.append([anchor_bytes, anchor_nbr_in_this_page])
        else:
            break
        _page_nbr += 1

    # parse raw bytes into anchor hashmaps
    anchors = []
    for [B, nbr] in _anchor_bytes_nbr_by_page:
        for i in range(nbr):
            _anchor_i = {}
            _anchor_i['addr'] = "{0:0{1}X}"\
                            .format(int.from_bytes(B[i*16 + 0:i*16 + 2],        byteorder='little', signed=False), 4)
            _anchor_i['x'] =        int.from_bytes(B[i*16 + 2  :i*16 + 6],      byteorder='little', signed=True)
            _anchor_i['y'] =        int.from_bytes(B[i*16 + 6  :i*16 + 10],     byteorder='little', signed=True)
            _anchor_i['z'] =        int.from_bytes(B[i*16 + 10 :i*16 + 14],     byteorder='little', signed=True)
            _anchor_i['RSSI'] = B[i*16 + 14]
            _anchor_i['seat'] = B[i*16 + 15]
            anchors.append(_anchor_i)

    return [anchors, err_code]


def dwm_loc_get(t, verbose=False):
    """ API Section 5.3.10, modified by Zezhou Wang
    API Sample TLV Request:
    Type    |Length 
    0x0C    |0x00   
    
    API Sample TLV Resonse Example 2 (Anchor node):
    Type    |Length |Value-err_code |...
    0x40    |0x01   |0x00           |...
    Type    |Length |Value-position (13B)                               |...    
    0x41    |0x0D   |x (4B, little), y (4B, little), z (4B, little),    |...
            |       |percentage quality factor (1B)                     |...
    Type    |Length |Value-Number of anchors w. distances (1B) .............    
    0x48    |0xC4   |0x0F                                               |...
    |Value (cont.) .............................................................|..................................
    |UWB address (8B)       |distance_to (4B)   |distance quality factoir (1B)  |..................................
    |-----------------------distance to anchor nbr.1 (13B)----------------------|(Cont.) anchor nr.2 anchor nr.3...



    
    
    |uint16_t (2B)          |3×int32_t (12B)    |int8_t - RSSI (1B) |uint8_t - seat (1B)    |...
    |UWB address in little  |position coords xyz|                   |                       |
    |endian                 |in little endian   |                   |                       |
    |-----------------------------------anchor nbr.1 (16B)----------------------------------|...anchor nr.2 anchor nr.3

    Sample (4 anchors):
    "40 01 00 56 41 04" 
    "84 c5 (Addr)| 3c 05 00 00 (x) | da 07 00 00 (y) | f4 0b 00 00 (z) | b2 (RSSI) | 00 (seat)" 
    "0c 0c (Addr)| dc 05 00 00 (x) | c4 09 00 00 (y) | b8 0b 00 00 (z) | b2 (RSSI) | 01 (seat)" 
    "28 13 (Addr)| 18 06 00 00 (x) | ce 04 00 00 (y) | 52 0d 00 00 (z) | b3 (RSSI) | 02 (seat)" 
    "1c 9a (Addr)| 00 fa 00 00 (x) | 50 c3 00 00 (y) | 50 46 00 00 (z) | 81 (RSSI) | 04 (seat)"

    API Sample TLV Resonse Example 2 (no anchor):
    Type    |Length |Value-err_code
    0x40    |0x01   |0x00          
    Type    |Length |Value              
    0x56    |0x01   |uint8_t -              
                    |number of elements     
                    |encoded in the value   
                    |0x0F                   

    ------------------------------------
    Get last distances to the anchors (tag is currently ranging to) and the associated position. The
    interrupt is triggered when all TWR measurements have completed and the LE has finished. If the LE
    is disabled, the distances will just be returned. This API works the same way in both Responsive and
    Low-Power tag modes. 
    ------------------------------------
    :return:
        list of hash maps (key-value pairs for anchors), length unit in millimeter
    """
    _func_name = inspect.stack()[0][3]
    TYPE, LENGTH, VALUE = b'\x0C', b'\x00', b''

    _page_nbr = 0
    _anchor_bytes_nbr_by_page = []
    # collect raw bytes and determine how many pages
    while True:
        _page_polling_bytes = TYPE + LENGTH + _page_nbr.to_bytes(1, byteorder="little", signed=False)
        t.reset_output_buffer()
        t.reset_input_buffer()
        t.write(_page_polling_bytes)
        _page_polling_response = t.read(6)
        err_code = _page_polling_response[2] if _page_polling_response[0:2] == b'\x40\x01' else 6
        error_handler(_page_polling_response, err_code, _func_name)
        anchor_nbr_in_this_page = _page_polling_response[-1]
        if anchor_nbr_in_this_page == 0:
            break
        else:
            _time_cnt = 0
            while t.inWaiting() < 16 * anchor_nbr_in_this_page and _time_cnt < timeout:
                time.sleep(0.01)
                _time_cnt += 0.01
            if _time_cnt > timeout:
                raise TimeoutError("[{}]: Reading anchors timeout on page {}."
                                    .format(_func_name, _page_nbr))
            if t.inWaiting() != 16 * anchor_nbr_in_this_page:
                raise ValueError("[{}]: Bytes for anchors do not match specs: 16 bits \
                                    per anchor on page {}. Expecting {} anchors. Got {} Bytes."
                                    .format(_func_name, _page_nbr, anchor_nbr_in_this_page, t.inWaiting()))
            anchor_bytes = t.read(t.inWaiting())
            if verbose:
                verbose_response(anchor_bytes, err_code, _func_name)
            _anchor_bytes_nbr_by_page.append([anchor_bytes, anchor_nbr_in_this_page])
        _page_nbr += 1

    # parse raw bytes into anchor hashmaps
    anchors = []
    for [B, nbr] in _anchor_bytes_nbr_by_page:
        for i in range(nbr):
            _anchor_i = {}
            _anchor_i['addr'] = "{0:0{1}X}"\
                            .format(int.from_bytes(B[i*16 + 0:i*16 + 2],        byteorder='little', signed=False), 4)
            _anchor_i['x'] =        int.from_bytes(B[i*16 + 2  :i*16 + 6],      byteorder='little', signed=True)
            _anchor_i['y'] =        int.from_bytes(B[i*16 + 6  :i*16 + 10],     byteorder='little', signed=True)
            _anchor_i['z'] =        int.from_bytes(B[i*16 + 10 :i*16 + 14],     byteorder='little', signed=True)
            _anchor_i['RSSI'] = B[i*16 + 14]
            _anchor_i['seat'] = B[i*16 + 15]
            anchors.append(_anchor_i)

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