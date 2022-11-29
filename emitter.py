# NAME: emitter.py
# PURPOSE: controlling the IR emitter, which sends pulses to the vision targets
# AUTHOR: Emma Bethel

from gpiozero import DigitalOutputDevice

EMITTER_PIN = 24
PULSE_PERIOD = 0.00005

class Emitter:
    def __init__(self):
        self.emitter = DigitalOutputDevice(EMITTER_PIN)

    # PURPOSE:
    # PARAMETERS: blocking - whether or not you want this function to be
    #                        blocking (i.e. whether the program should wait to
    #                        complete the function until the emitter stops
    #                        emitting)
    # RETURNS: N/A
    def send_pulse(self, blocking=False):
        self.emitter.blink(PULSE_PERIOD, PULSE_PERIOD, 100, not blocking)
