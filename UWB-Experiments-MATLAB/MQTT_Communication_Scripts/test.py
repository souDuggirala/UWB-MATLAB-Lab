import DWM1001 as dwm 
import serial
import time

t = serial.Serial("COM4",baudrate=115200,timeout=3)

dwm.dwm_pos_set(t, [2,3,4], 100, verbose=True)
[x, y, z, qual, err] = dwm.dwm_pos_get(t, verbose=True)
print([x, y, z, qual, err])
dwm.dwm_upd_rate_set(t, 1, 1, verbose=True)
[a, b, err] = dwm.dwm_upd_rate_get(t, verbose=True)
print([a,b])