import sys
import time

import RPi.GPIO as GPIO

def pulse(pinNum: int):
    print(f"pulse {pinNum}", file=sys.stderr, flush=True)
    GPIO.output(pinNum, GPIO.HIGH)
    time.sleep(0.060) # wait for latching
    GPIO.output(pinNum, GPIO.LOW)
    # let things settle
    time.sleep(0.020)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

try:
    while True:
        pulse(16)
        time.sleep(2)
        pulse(18)
        time.sleep(2)
finally:
    GPIO.cleanup()
