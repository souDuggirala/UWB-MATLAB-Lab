import DWM1001 as dwm 
import serial
import time
t = serial.Serial("COM9",baudrate=115200,timeout=3)

to_write=[b'\x01',b'\x0D',b'\x80',b'\x00',b'\x00',b'\x00',b'\x32',b'\x00',b'\x00',b'\x00',b'\xfb',b'\x00',b'\x00',b'\x00',b'\x64']
print('bytes to write', len(to_write))
# Initialize an empty byte object to concantenate
bytes_to_write = b''
for n in range(len(to_write)):
    bytes_to_write += to_write[n]
# This line below shows a way to correctly print bytes without ASCII coversion
print("written:", ''.join('{:02x} '.format(letter) for letter in bytes_to_write))
# This line above shows a way to correctly print bytes without ASCII coversion
t.write(bytes_to_write)
time.sleep(1)
print(t.read(t.inWaiting()))

time.sleep(1)
dwm.dwm_pos_set(t, [2,3,4], 100)
dwm.dwm_pos_get(t)
dwm.dwm_nodeid_get(t)