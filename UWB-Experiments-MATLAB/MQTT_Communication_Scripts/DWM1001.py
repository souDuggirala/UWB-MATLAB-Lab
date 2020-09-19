from time import sleep
import serial
import time


#---------------------------------------------------------
# helper functions start

def SHOW_OPE_INFO(port,info1,info2):

    print("USING",port)
    print("written to serial: ", info1,type(b'\x01'))
    print("written to serial: ", info2,type(b'\x01'))

def hexShow(argv):       

    result = []
    hLen = len(argv)  
    for i in range(hLen):
        hvol = argv[i]
        hhex = format(hvol, "02x")
        result.append(hex(int(hhex,16)))  
    
    print('hexShow:',result)
    return result


    
# convert decimal num to byte
def decimalTobytes(coordinate,qf,unit="mm"):
    def decimalTohex(num):
        if num > 2**32-1 or num<0:
            print("invalidInput")
        hexnum=hex(num)
        i = len(hexnum)-1
        hexArray=[b'\x00']*4
        temp=""
        index=0
        while i>1:
            temp=hexnum[i]+temp
            i-=1
            if len(temp)==2:
                # temp='\x'+temp
                hexArray[index]=bytes.fromhex(temp)
                index+=1
                temp=""
        if len(temp)==1:
            hexArray[index]=bytes.fromhex('0'+temp)
        return hexArray


    scale={"mm":1,"cm":10,"m":1000}
    if unit not in scale:
        print("invalid unit")
        return [b'\x00',b"\x00",b"\x00",b"\x00",b"\x00",b"\x00",b"\x00",b"\x00",b"\x00",b"\x00",b"\x00",b"\x00",b"\x00"]

    x,y,z=coordinate*scale[unit]
    
    pos=[]
    pos.extend(decimalTohex(x))
    pos.extend(decimalTohex(y))
    pos.extend(decimalTohex(z))
    pos.append(bytes.fromhex(hex(qf)[2:4]))

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

def dwm_pos_set(position,qf,t):        # display in hexadecimal format 

    TYPE=b'\x01'
    LENGTH=b'\x0D'
    # t.write(TYPE)
    # t.write(LENGTH)
    t.write(TYPE + LENGTH)
    
    SHOW_OPE_INFO(t.portstr,TYPE,LENGTH)
    print(len(decimalTobytes(position,qf)))
    for pos in decimalTobytes(position,qf):
        t.write(pos)
        print("written to serial: ", pos,type(b'\x01'))
        time.sleep(0.1)

    time.sleep(1)
    num=t.inWaiting()
    print(num)
    if num:
        str=t.read(num)
        # serial.Serial.close(t)

        if format(str[-1],"02x")=="01":
            print("error")
        else:
            print("set success")


         
def dwm_pos_get(t):        # display in hexadecimal format and decimal format 

    TYPE=b'\x02'
    LENGTH=b'\x00'
    # t.write(TYPE)
    # t.write(LENGTH)
    t.write(TYPE + LENGTH)

    SHOW_OPE_INFO(t.portstr,TYPE,LENGTH)

    time.sleep(1)
    num=t.inWaiting()
    print(num)
    if num:
        str=t.read(num)
        # serial.Serial.close(t)
        hexvalue=hexShow(str)
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
        hexvalue=hexShow(str)   

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
        hexShow(str)

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