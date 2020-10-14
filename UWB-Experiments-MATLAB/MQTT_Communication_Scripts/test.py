import DWM1001 as dwm 
import serial
import time

t = serial.Serial("COM9",baudrate=115200,timeout=3)

# dwm.dwm_pos_set(t, [2,3,4], 100, verbose=True)
[x, y, z, qual, err] = dwm.dwm_pos_get(t, verbose=True)
print([x, y, z, qual, err])
# dwm.dwm_upd_rate_set(t, 1, 1, verbose=True)
[a, b, err] = dwm.dwm_upd_rate_get(t, verbose=True)
print([a,b])
# anchors = dwm.dwm_anchor_list_get(t, verbose=True)
# print(anchors)

[pos, anchors, node_mode, err] = dwm.dwm_loc_get(t, verbose=True)
[print(n) for n in [pos, anchors, node_mode]]

# dwm.dwm_baddr_set(t, "E6FCB689AD01", verbose=True)
# [print(n) for n in [pos, anchors, node_mode]]

print(dwm.dwm_baddr_get(t, verbose=True))