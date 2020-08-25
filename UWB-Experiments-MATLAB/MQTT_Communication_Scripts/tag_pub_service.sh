#!/bin/bash
# starting the python publisher, with console standard output/errors
# both stored in /home/pi/tag_pub_out.log
echo "initialization of mqtt pub service - tag"
nohup python3 -u /home/pi/tag_mqtt_publisher.py >> /home/pi/tag_pub_out.log 2>&1 &
