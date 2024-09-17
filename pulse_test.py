import sys
import time
import argparse
import RPi.GPIO as GPIO

parser = argparse.ArgumentParser(
    description='Pulse GPIO pins.\n\n'
                'Example usage:\n'
                '  python pulse_test.py 16 18 3 5 --pulse-width 1.5 --delay 0.2\n\n'
                'Refer to the GPIO pins layout here:\n'
                '  https://webofthings.org/wp-content/uploads/2016/10/pi-gpio.png\n'
                'Watch pin status:\n'
                '  watch -d -n1 pinctrl -p -v  1-40',
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument('pins', metavar='N', type=int, nargs='*', default=[16, 18], help='an integer for the GPIO pin')
parser.add_argument('--pulse-width', type=float, default=0.060, help='pulse width in seconds (default 60ms for Barmed)')
parser.add_argument('--delay', type=float, default=5, help='delay between pulses in seconds')
args = parser.parse_args()

pins = args.pins
pulse_width = args.pulse_width
delay = args.delay

def pulse(pinNum: int, width: float):
    print(f"pulse {pinNum} for {width} seconds", file=sys.stderr, flush=True)
    GPIO.output(pinNum, GPIO.HIGH)
    time.sleep(width)
    GPIO.output(pinNum, GPIO.LOW)
    # let things settle
    time.sleep(0.020)

GPIO.setmode(GPIO.BOARD)
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

try:
    while True:
        for pin in pins:
            pulse(pin, pulse_width)
            time.sleep(delay)
finally:
    GPIO.cleanup()
