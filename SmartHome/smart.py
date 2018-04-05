#!/usr/bin/python3.4
import os
import signal
import threading
import traceback
from threading import Semaphore

import RPi.GPIO as GPIO
import time

import mmap

import struct

from builtins import print

import os

os.nice(-20)

GPIO.setmode(GPIO.BOARD)
sem = threading.Semaphore(value=1)
# define the pin that goes to the circuit
# pin_to_circuit = 11

# upper leds, light1
pinr = 13
ping = 15
pinb = 16

# motion sensor for timer
pinm = 7
# motion sensor for always on
pinm2 = 18
# light sensor
pinl = 11

# lower leds, light2
pinr2 = 19
ping2 = 23
pinb2 = 21

running = True
always_on = False
lights_on = False

# light_counter = 150
# lights_on = False
light_threshold = 500


# current_light = 0
# light1 = None
# light2 = None

def setup():
    print("setting up motion")
    GPIO.setup(pinm, GPIO.IN)
    GPIO.setup(pinm2, GPIO.IN)
    # Output on the pin for
    print("red")
    GPIO.setup(pinr, GPIO.OUT)
    print("green")
    GPIO.setup(ping, GPIO.OUT)
    print("blue")
    GPIO.setup(pinb, GPIO.OUT)
    GPIO.setup(pinr2, GPIO.OUT)
    print("green")
    GPIO.setup(ping2, GPIO.OUT)
    print("blue")
    GPIO.setup(pinb2, GPIO.OUT)

    global light1
    global light2
    light1 = Light(pinr, ping, pinb)
    light2 = Light(pinr2, ping2, pinb2)


def get_light():
    pin_to_circuit = pinl
    print("Light sensor running")
    global current_light

    while running:

        count = 0

        # Output on the pin for
        GPIO.setup(pin_to_circuit, GPIO.OUT)
        GPIO.output(pin_to_circuit, GPIO.LOW)
        time.sleep(0.5)

        # Change the pin back to input
        GPIO.setup(pin_to_circuit, GPIO.IN)

        # Count until the pin goes high
        while (GPIO.input(pin_to_circuit) == GPIO.LOW):
            count += 1
        sem.acquire()
        current_light = count
        sem.release()

    print("Light sensor exited")


def get_motion():
    motion = GPIO.input(pinm)
    return motion


def get_motion_always():
    motion = GPIO.input(pinm2)
    return motion


def toggle_always_on():
    print("toggle always on called")
    global always_on
    global lights_on
    color1 = light1.get_dc()
    color2 = light2.get_dc()

    if always_on:
        always_on = False
        lights_on = False
        # blink red
        light1.turn_off()
        light2.turn_off()
        time.sleep(0.1)
        light1.set_duty_cycle(100, 0, 0)
        light2.set_duty_cycle(100, 0, 0)
        light1.turn_on()
        light2.turn_on()
        time.sleep(0.1)
        light1.turn_off()
        light2.turn_off()
        # reset to default
        light1.set_duty_cycle(color1[0], color1[1], color1[2])
        light2.set_duty_cycle(color2[0], color2[1], color2[2])
        lights_on = False
        time.sleep(0.1)
    else:
        always_on = True
        # blink green
        light1.turn_off()
        light2.turn_off()
        time.sleep(0.1)
        light1.set_duty_cycle(0, 100, 0)
        light2.set_duty_cycle(0, 100, 0)
        light1.turn_on()
        light2.turn_on()
        time.sleep(0.1)
        light1.turn_off()
        light2.turn_off()
        time.sleep(0.1)
        # turn light on
        light1.turn_on()
        light2.turn_on()
        lights_on = True
        light1.set_duty_cycle(color1[0], color1[1], color1[2])
        light2.set_duty_cycle(color2[0], color2[1], color2[2])
        light1.turn_on()
        light2.turn_on()


def check_sensors():
    try:
        print("Check Sensors running")
        global light_counter
        global current_light
        global always_on
        global lights_on
        lights_on = False
        always_on = False
        light_counter = 150
        always_on_counter = 0
        while running:

            # check if always_on toggle was requested
            motion_always = get_motion_always()
            #
            # if (always_on or lights_on) and light1.is_dirty():
            #     #light1.turn_off()
            #     #light2.turn_off()
            #     light1.turn_on()
            #     light2.turn_on()
            #     light1.dirty = False
            #     light2.dirty = False

            if always_on_counter <= 0 and motion_always:
                toggle_always_on()
                always_on_counter = 60
                # wait for the motion sensor to calm down

            if always_on:
                # print("in always on mode")
                # nothing to do here, light is on and should stay on
                pass
            else:
                # light should be off here, check motion and light sensors
                # print("in normal mode")
                motion = get_motion()
                sem.acquire()
                light = current_light
                sem.release()

                # If lights are on decrease timer
                if lights_on:
                    # print("lights on")
                    light_counter -= 1

                if motion and light > light_threshold:
                    # Light should be on, set timer to 150
                    light_counter = 300

                    if lights_on:
                        # print("nothing to do")
                        # Nothing to do at all :)
                        pass
                    else:
                        # print("switching on")
                        lights_on = True
                        light1.turn_on()
                        light2.turn_on()

                elif light_counter <= 0:
                    light1.turn_off()
                    lights_on = False
                    light2.turn_off()

            if always_on_counter > 0:
                always_on_counter -= 1

            time.sleep(0.1)

        print("Check sensors exited")
    except Exception as e:
        print(e)
        tb = traceback.format_exc()
        print(tb)
        print("Error occurred")
        pass
    finally:
        GPIO.cleanup()


class Light():
    def __init__(self, pinr, ping, pinb):
        self.frequency = 0.1
        self.r = GPIO.PWM(pinr, self.frequency)
        self.g = GPIO.PWM(ping, self.frequency)
        self.b = GPIO.PWM(pinb, self.frequency)
        self.dcr = 100
        self.dcg = 100
        self.dcb = 100
        self.dirty = False

    def is_dirty(self):
        return self.dirty

    def get_dc(self):
        return [self.dcr, self.dcg, self.dcb]

    def set_frequency(self, freq):
        self.frequency = freq
        print("setting frequ ",freq)
        self.r.ChangeFrequency(freq)
        self.g.ChangeFrequency(freq)
        self.b.ChangeFrequency(freq)

    def turn_on(self):
        print("turning lights on ", self.dcr, self.dcg, self.dcb)
        self.r.start(self.dcr)
        self.g.start(self.dcg)
        self.b.start(self.dcb)

    def set_duty_cycle(self, dcr=100, dcg=100, dcb=100):
        self.dcr = dcr
        self.dcg = dcg
        self.dcb = dcb
        self.dirty = True

    def turn_off(self):
        self.r.stop()
        self.g.stop()
        self.b.stop()

    def normalize_rgbb(self, rgbb):
        rgb = [0, 0, 0]
        for i in range(0, 3):
            rgb[i] = rgbb[i] * 100 / 255 * rgbb[3]
        return rgb

run = True

def handler_stop_signals(signum, frame):
    global run
    run = False

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

def start_smarthome():
    import _thread

    try:
        print("starting..")
        setup()
        global current_light
        current_light = 100
        print("setup done, starting threads")
        thread_check_sensors = _thread.start_new_thread(check_sensors, ())
        #    thread_check_sensors.daemon=True
        thread_light_sensor = _thread.start_new_thread(get_light, ())
        print("starting light sensor")
        #    thread_light_sensor.start()
        print("starting sensors thread")
        fd = os.open('/tmp/mmaptest', os.O_RDONLY)
        buf = mmap.mmap(fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_READ)
        #    thread_check_sensors.start()
        # Main loop

        r, = struct.unpack('>I', buf[:4])
        g, = struct.unpack('>I', buf[4:8])
        b, = struct.unpack('>I', buf[8:12])
        rgb_dc_previous = light1.normalize_rgbb([r, g, b, 1])
        frequency_previous = struct.unpack('>I', buf[12:16])
        while run:

            # print(current_light)

            r, = struct.unpack('>I', buf[:4])

            g, = struct.unpack('>I', buf[4:8])

            b, = struct.unpack('>I', buf[8:12])

            frequency, = struct.unpack('>I', buf[12:16])
            # print(r, g, b)

            #            light1 = get_light1()
            #            light2 = get_light2()

            rgb_dc = light1.normalize_rgbb([r, g, b, 1])

            if frequency != frequency_previous:
                print("freq changed")
                light1.set_frequency(frequency)
                light2.set_frequency(frequency)
                frequency_previous = frequency

            if rgb_dc != rgb_dc_previous:

                light1.set_duty_cycle(rgb_dc[0], rgb_dc[1], rgb_dc[2])
                light2.set_duty_cycle(rgb_dc[0], rgb_dc[1], rgb_dc[2])
                if lights_on or always_on:
                    light1.turn_on()
                    light2.turn_on()
                rgb_dc_previous = rgb_dc

            time.sleep(1)
            #       rc_time(pinr)
            # time.sleep(10)
    except Exception as e:
        print(e)
        tb = traceback.format_exc()
        print(tb)
        print("Error occurred")
        pass
    finally:
        running = False
        GPIO.cleanup()
    print("Got sigterm, cleaning up")
    GPIO.cleanup()

def get_light1():
    return light1


def get_light2():
    return light2


start_smarthome()
