from time import sleep
import serial
import time
import paho.mqtt.client as mqtt

def is_reporting_loc(serialport):
    init_bytes_avail = t.in_waiting
    time.sleep(2)
    final_bytes_avail = t.in_waiting
    if final_bytes_avail - init_bytes_avail > 0:
        return True
    return False
def mqtt_on_publish(client, data, result):
    pass

mqtt_broker = "192.168.204.197"
port = 1883

# print("Enter the tag serial port name in string: (to be automated)")
comport = "COM6"
# # In Python the readline timeout is set in the serialport initialization part
t = serial.Serial(comport, baudrate=115200, timeout=3.0)
# Pause for 1 sec after establishment
time.sleep(1)
# Double enter (carriage return) as specified by Decawave
t.write(b'\x0D')
time.sleep(0.1)
t.write(b'\x0D')
t.reset_input_buffer()


# By default the update rate is 10Hz/100ms. Check again for data flow
print("Comport dataflow reporting properly?")
print(is_reporting_loc(t))
time.sleep(1)

if not is_reporting_loc(t):
# type "lep\n" to the dwm shell console to activate data reporting
    t.write(b'\x6C\x65\x70\x0D')

print("Connecting to Broker")
tag_client = mqtt.Client("Tag")
tag_client.on_publish = mqtt_on_publish
tag_client.connect(mqtt_broker, port)

while True:
    data = str(t.readline(), encoding="UTF-8").rstrip()
    print(data)
    tag_client.publish("Tag/Location", data)
t.close()
