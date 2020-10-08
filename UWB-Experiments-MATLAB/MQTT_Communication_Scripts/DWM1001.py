from time import sleep
import serial
import time

# Show hexadecimal in string format
def hex_show(bytes_to_show):
    return ''.join('0x{:02x},'.format(letter) for letter in bytes_to_show)


    
# convert decimal num to byte
def decimalTobytes(coords, qual_fact_percent, unit="mm"):
    if unit not in ("mm", "cm", "m"):
        raise ValueError("Invalid Input Unit")
    scale={"mm":1,"cm":10,"m":1000}
    x, y, z = coords * scale[unit]
    pos = b''
    pos += x.to_bytes(4, byteorder='little', signed=True)
    pos += y.to_bytes(4, byteorder='little', signed=True)
    pos += z.to_bytes(4, byteorder='little', signed=True)
    pos += qual_fact_percent.to_bytes(1, byteorder='little', signed=False)
    return pos

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

def dwm_pos_set(t, coords, qual_fact_percent, unit="mm"):        # display in hexadecimal format 
    t.reset_input_buffer()
    TYPE = b'\x01'
    LENGTH = b'\x0D'

    if unit not in ("mm", "cm", "m"):
        raise ValueError("Invalid Input Unit")
    scale={"mm":1,"cm":10,"m":1000}

    [x, y, z]= [c* scale[unit] for c in coords]
    pos_bytes = b''
    pos_bytes += x.to_bytes(4, byteorder='little', signed=True)
    pos_bytes += y.to_bytes(4, byteorder='little', signed=True)
    pos_bytes += z.to_bytes(4, byteorder='little', signed=True)
    pos_bytes += qual_fact_percent.to_bytes(1, byteorder='little', signed=False)
    VALUE = pos_bytes
    input_bytes = TYPE + LENGTH + VALUE
    t.write(input_bytes)
    
    print("written to serial: ",input_bytes)
    returned_values = t.read(3)
    print(hex_show(returned_values))
    if format(returned_values[-1],"02x")=="01":
        print("error")
    else:
        print("set success")


         
def dwm_pos_get(t):        # display in hexadecimal format and decimal format 
    TYPE=b'\x02'
    LENGTH=b'\x00'
    # t.write(TYPE)
    # t.write(LENGTH)
    t.write(TYPE + LENGTH)
    time.sleep(1)
    num=t.inWaiting()
    print(num)
    if num:
        str=t.read(num)
        # serial.Serial.close(t)
        hexvalue=hex_show(str)
        print("hexvalue: ", hexvalue)
        x,y,z,qf = hexTodemical(hexvalue[5:9]),hexTodemical(hexvalue[9:13]),hexTodemical(hexvalue[13:17]),int(hexvalue[-1],16)
        print('x:',hexvalue[5:9],"y:",hexvalue[9:13],"z:",hexvalue[13:17],"qf:",qf)
        print('x:',x,"y:",y,"z:",z,"qf:",qf)

###################################
#########################----------
def dwm_upd_rate_set(rate,t):
    return -1
########################-----------
###################################

def dwm_upd_rate_get(t):

    TYPE=b'\x04'
    LENGTH=b'\x00'
    # t.write(TYPE)
    # t.write(LENGTH)
    t.write(TYPE + LENGTH)

    SHOW_OPE_INFO(t.portstr,TYPE,LENGTH)

    time.sleep(1)
    num=t.inWaiting()
    print("num",num)
    if num:
        str = t.read(num)
        serial.Serial.close(t)
        hexvalue=hex_show(str)   

#################################
#######################----------
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

def dwm_gpio_cfg_output():
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
        hex_show(str)

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