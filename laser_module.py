#!/usr/bin/env python3

# NAME: laser_module.py
# PURPOSE: controlling laser emitter
# AUTHOR: Emma Bethel

import os
import robomodules as rm
from time import sleep

from gpiozero import LED
from messages import MsgType, message_buffers


# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 2
LASER_PIN = 14


class LaserModule(rm.ProtoModule):
    # sets up the module (subscriptions, connection to server, etc)
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.LASER_COMMAND]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)

        # initializing laser diode
        self.laser = LED(LASER_PIN)
        self.laser.on()

    # runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        if msg_type == MsgType.LASER_COMMAND:
            print('received laser command with value:', msg.seconds)

            self.laser.off()
            sleep(msg.seconds)
            self.laser.on()


    # runs every 1 / FREQUENCY seconds
    def tick(self):
        pass
        

def main():
    module = LaserModule(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()