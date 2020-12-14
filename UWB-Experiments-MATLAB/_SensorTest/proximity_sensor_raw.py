import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

TRIG=26
ECHO=16

if __name__ == "__main__":
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)
    print("Waiting for Sensor to Settle")
    time.sleep(2)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO)==0:
        pulse_start=time.time()
    while GPIO.input(ECHO)==1:
        pulse_end=time.time()
    
    pulse_duration = pulse_end - pulse_start
    dist = pulse_duration * 17150
    dist = round(dist, 2)
    print("distance: {} cm".format(dist))
    GPIO.setup()