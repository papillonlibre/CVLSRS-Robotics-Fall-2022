#!/usr/bin/env python3

# NAME: target_sender_module.py
# PURPOSE: randomly generating and sending Target commands upon keypress
# AUTHOR: Emma Bethel

import os
import random
import robomodules as rm
from messages import MsgType, message_buffers, Target

# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 1


class TargetSenderModule(rm.ProtoModule):
    # sets up the module (subscriptions, connection to server, etc)
    def __init__(self, addr, port):
        self.subscriptions = []
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)

    # runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        pass

    # runs every 1 / FREQUENCY seconds
    def tick(self):
        input().lower()

        msg = Target()
        msg.shape = 0 # hardcoded square, can change for further testing
        msg.color = 0 # hardcoded red, can change for further testing

        self.write(msg.SerializeToString(), MsgType.TARGET)
        print('sent', msg)
        

def main():
    print('press enter to send a target message!')
    module = TargetSenderModule(ADDRESS, PORT) # inits the module
    module.run()


if __name__ == "__main__":
    main()
