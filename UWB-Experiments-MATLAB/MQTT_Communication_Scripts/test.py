import DWM1001 as dwm 
import serial
import time
t = serial.Serial("COM9",baudrate=115200,timeout=3)

dwm.dwm_pos_set((121,50,100),100,t)

to_write=[b'\x01',b'\x0D',b'\x80',b'\x00',b'\x00',b'\x00',b'\x32',b'\x00',b'\x00',b'\x00',b'\xfb',b'\x00',b'\x00',b'\x00',b'\x64']
print(len(to_write))
bytes_to_write = b''
for n in range(len(to_write)):
    bytes_to_write += to_write[n]
t.write(bytes_to_write)
    # t.write(item)
    # print("written: ", item, "\tbuffer: ", t.read(t.inWaiting()))
    # print(item,type(item),"inwaiting: ",t.inWaiting())

time.sleep(1)
dwm.dwm_pos_get(t)
dwm.dwm_nodeid_get(t)