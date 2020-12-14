import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

TRIG=26
ECHO=16

PROXI=15
INTERVAL=2
# 15 CM as the maximum threshold for proximity detection

def proximity_init(trig=TRIG, echo=ECHO):
    print("Distance Measurement In Progress")
    GPIO.setup(trig, GPIO.OUT)
    GPIO.setup(echo, GPIO.IN)

def proximity_start(trig=TRIG, echo=ECHO, proximity_threshold=PROXI):
    GPIO.output(trig, False)
#    print("Waiting for Sensor to Settle")
    time.sleep(0.00001)

    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    pulse_duration_threshold = proximity_threshold / 17150

    while GPIO.input(echo)==0:
        pass
    pulse_start = time.time()

    PROX_FLAG = 1
    while GPIO.input(echo)==1:
        pulse_end = time.time()
        if pulse_end - pulse_start > pulse_duration_threshold:
            PROX_FLAG = 0
            break
        
    if PROX_FLAG:
        pulse_duration = pulse_end - pulse_start
        dist = pulse_duration * 17150
        dist = round(dist, 2)
        
        return dist
    else:
        return None
if __name__ == "__main__":
    startt = time.time()
    try:
        proximity_init()
        while True:
            dist = proximity_start()
            if not dist:
                print("Non in the range, greater than 15cm")
            else:
                print("Distance: {} cm".format(dist))
            time.sleep(INTERVAL)
    except BaseException as e:
        raise(e)
    finally:
        stopt = time.time()
        print("program running time: {} seconds".format(stopt - startt))
        GPIO.cleanup()
  