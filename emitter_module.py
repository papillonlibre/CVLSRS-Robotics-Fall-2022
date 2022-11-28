#!/usr/bin/env python3

# NAME: emitter_module.py
# PURPOSE: sends out pings to vision targets based on input messages
# AUTHOR: Emma Bethel
# NOTE: currently in development; should be done by 11/28. for now just prints 
#       whenever it receives a command

import os
import robomodules as rm
from messages import MsgType, message_buffers

# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 2


class EmitterModule(rm.ProtoModule):
    # sets up the module (subscriptions, connection to server, etc)
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.EMITTER_COMMAND]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)

    # runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        if msg_type == MsgType.EMITTER_COMMAND:
            print('Message received! Will emit IR signal for', msg.seconds, 'seconds.')

    # runs every 1 / FREQUENCY seconds
    def tick(self):
        pass


def main():
    module = EmitterModule(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()
