from time import sleep

import serial
import time

try:
    serial.Serial.close(t)
except:
    pass

def hexShow(argv):        # display in hexadecimal format 
    result = ''  
    hLen = len(argv)  
    for i in range(hLen):
        hvol = argv[i]
        print('idx: ',i,' ','item: ',repr(hvol))
        hhex = format(hvol, '02x')
        result += hhex+' '  
    print('hexShow:',result)

t = serial.Serial("COM6", baudrate=115200, timeout=3.0)
print(t.portstr)
tag = t.write(b'\x30')
length = t.write(b'\x00')

print("using ")
print("written to serial: ", b'\x30',type(b'\x30'))
print("written to serial: ", b'\x00',type(b'\x00'))

time.sleep(1)
num=t.inWaiting()
if num:
    str = t.read(num)
    hexShow(str)
serial.Serial.close(t)