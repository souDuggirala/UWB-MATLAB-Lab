import paho
import time
import paho.mqtt.subscribe as subscribe

"""
Sample code of loading MQTT Decawave data from the gateway
usage: 
    change the HOST address accordingly to the correct gateway of the network lister.
    change the sample topic (specifying the tag)
"""
HOST = "172.16.46.92"
SAMPLE_TOPICS = ["dwm/node/47a3/uplink/location"]  # select the DMW47A3 as the tag
try:
    while True:
        msg = subscribe.simple(SAMPLE_TOPICS, hostname=HOST)
        print("%s %s" % (msg.topic, msg.payload)) 
except Exception as e:
    print(e)
    pass
