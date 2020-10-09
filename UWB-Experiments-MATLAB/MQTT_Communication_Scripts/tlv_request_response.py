from time import sleep

import serial
import time

try:
    serial.Serial.close(t)
except:
    pass

def hex_in_string(bytes_to_show):       
    return ''.join('{:02x} '.format(letter) for letter in bytes_to_show)

t = serial.Serial("COM9", baudrate=115200, timeout=3.0)
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
    print(hex_in_string(str))
    
serial.Serial.close(t)