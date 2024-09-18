# -*- coding: utf-8 -*-
import time
import sys
from typing import List, Tuple

# local module imports
from blinker import signal
import gv
import uuid

def verify_pi():
    """
    Verify that we are running on a Raspberry Pi.
    """
    rpi_MAC = ["28CDC1", "B827EB", "D83ADD", "DCA632", "E45F01"]
    vendor = str((hex(uuid.getnode())))[2:8].upper()
    return vendor in rpi_MAC

if verify_pi():
    gv.platform = "pi"
    # print("Pi verified")  # - test

try:
    import RPi.GPIO as GPIO
    gv.platform = "pi"
except ImportError:
    try:
        import Adafruit_BBIO.GPIO as GPIO  # Required for accessing GPIO pins on Beagle Bone Black
        gv.pin_map = [None] * 11  # map only the pins we are using
        gv.pin_map.extend(["P9_" + str(i) for i in range(11, 17)])
        gv.platform = "bo"
    except ImportError:
        gv.pin_map = [
            i for i in range(27)
        ]  # assume 26 pins all mapped.  Maybe we should not assume anything, but...
        gv.platform = ""  # if no platform, allows program to still run.
        print("\33[31mWARNING: No GPIO library was loaded,\nSIP will run but stations will NOT be activated.")
        print("Please be sure either RPI.GPIO or pigpio for Python (or both) is installed.\33[0m")

# fmt: off
if gv.platform == "pi":
    rev = GPIO.RPI_INFO['P1_REVISION']
    if rev == 1:
        # map 26 physical pins (1 based) with 0 for pins that do not have a gpio number
        if gv.use_pigpio:
            gv.pin_map = [ #  BMC numbering
                0, #  offset for 1 based numbering
                0,  0,
                0,  0,
                1,  0,
                4,  14,
                0,  15,
                17, 18,
                21, 0,
                22, 23,
                0,  24,
                10, 0,
                9,  25,
                11, 8,
                0,  7,
            ]
        else:
            gv.pin_map = [ #  Board numbering
                0, #  offset for 1 based numbering
                0,  0,
                3,  0,
                5,  0,
                7,  8,
                0,  10,
                11, 12,
                13, 0,
                15, 16,
                0,  18,
                19, 0,
                21, 22,
                23, 24,
                0,  26,
            ]
    elif rev == 2:
        # map 26 physical pins (1 based) with 0 for pins that do not have a gpio number
        if gv.use_pigpio:
            gv.pin_map = [ #  BMC numbering
                0, #  offset for 1 based numbering
                0,  0,
                2,  0,
                3,  0,
                4,  14,
                0,  15,
                17, 18,
                27, 0,
                22, 23,
                0,  24,
                10, 0,
                9,  25,
                11, 8,
                0,  7,
            ]
        else:
            gv.pin_map = [#  Board numbering
                0, #  offset for 1 based numbering
                0,  0,
                3,  0,
                5,  0,
                7,  8,
                0,  10,
                11, 12,
                13, 0,
                15, 16,
                0,  18,
                19, 0,
                21, 22,
                23, 24,
                0,  26,
            ]
    elif rev == 3:
        # map 40 physical pins (1 based) with 0 for pins that do not have a gpio number
        print(f"gpio_pins: pi rev==3, gv.use_pigpio={gv.use_pigpio}", file=sys.stderr, flush=True)
        if gv.use_pigpio:
            gv.pin_map = [ #  BMC numbering
                0, #  offset for 1 based numbering
                0,  0,
                2,  0,
                3,  0,
                4,  14,
                0,  15,
                17, 18,
                27, 0,
                22, 23,
                0,  24,
                10, 0,
                9,  25,
                11, 8,
                0,  7,
                0,  0,
                5,  0,
                6,  12,
                13, 0,
                19, 16,
                26, 20,
                0,  21,
            ]
        else:
            # <<<<<<<<<<<<< HERE >>>>>>>>>>>
            gv.pin_map = [#  Board numbering
                0, #  offset for 1 based numbering
                0,  0,
                3,  0,
                5,  0,
                7,  8,
                0,  10,
                11, 12,
                13, 0,
                15, 16,
                0,  18,
                19, 0,
                21, 22,
                23, 24,
                0,  26,
                0,  0,
                29, 0,
                31, 32,
                33, 0,
                35, 36,
                37, 38,
                0,  40,
            ]
    else:
        print("Unknown pi pin revision.  Using pin mapping for rev 3")
# fmt: on

# (off_pin, on_pin)
BERMAD_STATION_OFF_ON_PINS: List[Tuple[int, int]] = [(gv.pin_map[11], gv.pin_map[13]), (gv.pin_map[29], gv.pin_map[31]), (gv.pin_map[35], gv.pin_map[37]), (gv.pin_map[38], gv.pin_map[40])]

zone_change = signal("zone_change")

try:
    if gv.use_pigpio:
        import pigpio

        pi = pigpio.pi()
    else:
        GPIO.setwarnings(False)
        GPIO.setmode(
            GPIO.BOARD
        )  # IO channels are referenced by header connector pin numbers.
except Exception:
    pass


global pin_rain_sense
global pin_relay

try:
    if gv.platform == "pi":  # If this will run on Raspberry Pi:
        GPIO.setmode(GPIO.BOARD)
        pin_rain_sense = gv.pin_map[8]
        pin_relay = gv.pin_map[10]
        pin_bermad_relay = gv.pin_map[7]
    elif gv.platform == "bo":  # If this will run on Beagle Bone Black:
        pin_rain_sense = gv.pin_map[15]
        pin_relay = gv.pin_map[16]
except AttributeError:
    pass

try:
    if gv.use_pigpio:
        pi.set_mode(pin_rain_sense, pigpio.INPUT)
        pi.set_pull_up_down(pin_rain_sense, pigpio.PUD_UP)
        pi.set_mode(pin_relay, pigpio.OUTPUT)
    else:
        GPIO.setup(pin_rain_sense, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_relay, GPIO.OUT)
except NameError:
    pass

def setup_pins():
    """
    Define and setup GPIO pins for shift register operation
    """

    global pin_sr_dat
    global pin_sr_clk
    global pin_sr_noe
    global pin_sr_lat
    global pi

    try:
        if gv.platform == "pi":  # If this will run on Raspberry Pi:
            if not gv.use_pigpio:
                GPIO.setmode(
                    GPIO.BOARD
                )  # IO channels are identified by header connector pin numbers. Pin numbers are always the same regardless of Raspberry Pi board revision.
            pin_sr_dat = gv.pin_map[13]
            pin_sr_clk = gv.pin_map[7]
            pin_sr_noe = gv.pin_map[11]
            pin_sr_lat = gv.pin_map[15]
        elif gv.platform == "bo":  # If this will run on Beagle Bone Black:
            pin_sr_dat = gv.pin_map[11]
            pin_sr_clk = gv.pin_map[13]
            pin_sr_noe = gv.pin_map[14]
            pin_sr_lat = gv.pin_map[12]

    except AttributeError:
        pass

    #### setup GPIO pins as output or input ####
    try:
        if gv.use_pigpio:
            pi.set_mode(pin_sr_noe, pigpio.OUTPUT)
            pi.set_mode(pin_sr_clk, pigpio.OUTPUT)
            pi.set_mode(pin_sr_dat, pigpio.OUTPUT)
            pi.set_mode(pin_sr_lat, pigpio.OUTPUT)
            pi.write(pin_sr_noe, 1)
            pi.write(pin_sr_clk, 0)
            pi.write(pin_sr_dat, 0)
            pi.write(pin_sr_lat, 0)
        else:
            GPIO.setup(pin_sr_noe, GPIO.OUT)
            GPIO.setup(pin_sr_clk, GPIO.OUT)
            GPIO.setup(pin_sr_dat, GPIO.OUT)
            GPIO.setup(pin_sr_lat, GPIO.OUT)
            GPIO.output(pin_sr_noe, GPIO.HIGH)
            GPIO.output(pin_sr_clk, GPIO.LOW)
            GPIO.output(pin_sr_dat, GPIO.LOW)
            GPIO.output(pin_sr_lat, GPIO.LOW)
    except NameError:
        pass


def disableShiftRegisterOutput():
    """Disable output from shift register."""

    global pi
    try:
        pin_sr_noe
    except NameError:
        if gv.use_gpio_pins:
            setup_pins()
    try:
        if gv.use_pigpio:
            pi.write(pin_sr_noe, 1)
        else:
            GPIO.output(pin_sr_noe, GPIO.HIGH)
    except Exception:
        pass


def enableShiftRegisterOutput():
    """Enable output from shift register."""

    global pi
    try:
        if gv.use_pigpio:
            pi.write(pin_sr_noe, 0)
        else:
            GPIO.output(pin_sr_noe, GPIO.LOW)
    except Exception:
        pass

# 0.06s pulse width is for Bermad S-392T-2W
# https://catalog.bermad.com/BERMAD%20Assets/Irrigation/Solenoids/IR-SOLENOID-S-392T-2W/IR_Accessories-Solenoid-S-392T-2W_Product-Page_English_2-2020_XSB.pdf
# Actuated by H-Bridge L298 https://projecthub.arduino.cc/hibit/how-to-use-the-l298n-motor-driver-module-0bb697
def pulse(pinNum: int):
    #Serial.println(String("Pulse") + String(pinNum));
    if pinNum not in gv.pin_map:
        print(f"pinNum {pinNum} not in gv.pin_map", file=sys.stderr, flush=True)
        return
    # print(f"pulse {pinNum}", file=sys.stderr, flush=True)
    if gv.use_pigpio:
        pi.write(pinNum, 1)
        time.sleep(0.060) # wait for latching
        pi.write(pinNum, 0)
    else:
        GPIO.output(pinNum, GPIO.HIGH)
        time.sleep(0.060) # wait for latching
        GPIO.output(pinNum, GPIO.LOW)
    # let things settle
    time.sleep(0.020)

def set_bermad_pins_output(output: bool):
    if gv.use_pigpio:
        pi.set_mode(pin_bermad_relay, pigpio.OUTPUT if output else pigpio.INPUT)
    else:
        GPIO.setup(pin_bermad_relay, GPIO.OUT if output else GPIO.IN)
    time.sleep(0.100) # wait for H-Bridge to power up
    for off_pin, on_pin in BERMAD_STATION_OFF_ON_PINS:
        if gv.use_pigpio:
            pi.set_mode(off_pin, pigpio.OUTPUT if output else pigpio.INPUT)
            pi.set_mode(on_pin, pigpio.OUTPUT if output else pigpio.INPUT)
        else:
            GPIO.setup(off_pin, GPIO.OUT if output else GPIO.IN)
            GPIO.setup(on_pin, GPIO.OUT if output else GPIO.IN)

# if BERMAD_STATION_OFF_ON_PINS:
#     set_bermad_pins_output(True)
#     time.sleep(0.250) # wait for H-Bridge to power up
#     for off_pin, on_pin in BERMAD_STATION_OFF_ON_PINS:
#         pulse(off_pin)
#     set_bermad_pins_output(False)

def setShiftRegister(srvals):
    """Set the state of each output pin on the shift register from the srvals list."""

    global pi
    try:
        if gv.use_pigpio:
            pi.write(pin_sr_clk, 0)
            pi.write(pin_sr_lat, 0)
            for s in range(gv.sd["nst"]):
                pi.write(pin_sr_clk, 0)
                if srvals[gv.sd["nst"] - 1 - s]:
                    pi.write(pin_sr_dat, 1)
                else:
                    pi.write(pin_sr_dat, 0)
                pi.write(pin_sr_clk, 1)
            pi.write(pin_sr_lat, 1)
        else:
            GPIO.output(pin_sr_clk, GPIO.LOW)
            GPIO.output(pin_sr_lat, GPIO.LOW)
            for s in range(gv.sd["nst"]):
                print(f's={s}, srvals[{gv.sd["nst"] - 1 - s}]={srvals[gv.sd["nst"] - 1 - s]}', file=sys.stderr, flush=True)
                GPIO.output(pin_sr_clk, GPIO.LOW)
                if srvals[gv.sd["nst"] - 1 - s]:
                    GPIO.output(pin_sr_dat, GPIO.HIGH)
                else:
                    GPIO.output(pin_sr_dat, GPIO.LOW)
                GPIO.output(pin_sr_clk, GPIO.HIGH)
            GPIO.output(pin_sr_lat, GPIO.HIGH)
    except Exception:
        pass


def set_output():
    """
    Activate pins according to gv.srvals.
    """

    with gv.output_srvals_lock:
        gv.output_srvals = gv.srvals
        if gv.sd["alr"]:
            gv.output_srvals = [
                1 - i for i in gv.output_srvals
            ]  #  invert logic of shift registers
        if BERMAD_STATION_OFF_ON_PINS:
            set_bermad_pins_output(True)
            for s in range(gv.sd["nst"]):
                station_id = gv.sd["nst"] - 1 - s
                if station_id >= len(BERMAD_STATION_OFF_ON_PINS):
                    print(f"Station {station_id} is not mapped to a BERMAD_STATION_OFF_ON_PINS pin pair", file=sys.stderr, flush=True)
                    continue
                off_pin, on_pin = BERMAD_STATION_OFF_ON_PINS[station_id]
                pulse_pin = on_pin if gv.output_srvals[station_id] else off_pin
                print(f"Station {station_id} (off_pin={off_pin}, on_pin={on_pin}) will be set {gv.output_srvals[station_id]} using pulse({pulse_pin})", file=sys.stderr, flush=True)
                pulse(pulse_pin)
            set_bermad_pins_output(False)
        else:
            disableShiftRegisterOutput()
            setShiftRegister(gv.output_srvals)  # gv.srvals stores shift register state
            enableShiftRegisterOutput()
        zone_change.send()
