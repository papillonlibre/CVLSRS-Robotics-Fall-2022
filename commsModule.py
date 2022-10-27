#!/usr/bin/env python3

# NAME: commsModule.py
# PURPOSE: forwards vision target commands from game server to local server
# AUTHOR: Emma Bethel

import os
import robomodules as rm
from messages import *

SERVER_ADDRESS = os.environ.get("BIND_ADDRESS","localhost")
SERVER_PORT = os.environ.get("BIND_PORT", 11297)

LOCAL_ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
LOCAL_PORT = os.environ.get("LOCAL_PORT", 11295)

SERVER_FREQUENCY = 0
LOCAL_FREQUENCY = 30

# receives target messages from game server
class ServerClient(rm.ProtoModule):
    def __init__(self, addr, port, loop):
        self.subscriptions = [MsgType.TARGET]
        super().__init__(addr, port, message_buffers, MsgType, SERVER_FREQUENCY, self.subscriptions, loop)
        self.state = None

    def msg_received(self, msg, msg_type):
        # Receive and store target messages
        if msg_type == MsgType.TARGET:
            self.state = msg

    def tick(self):
        pass

    def get_target(self):
        return self.state

# forwards new target messages to local server
class CommsModule(rm.ProtoModule):
    def __init__(self, server_addr, server_port, local_addr, local_port):
        self.subscriptions = []
        super().__init__(local_addr, local_port, message_buffers, MsgType, LOCAL_FREQUENCY, self.subscriptions)
        self.server_module = ServerClient(server_addr, server_port, self.loop)
        self.server_module.connect()
        self.current_target = None

    def msg_received(self, msg, msg_type):
        pass

    def tick(self):
        # Get current target
        target = self.server_module.get_target()

        # If new target has been received, broadcast to local modules
        if self.current_target != target:
            self.write(target.SerializeToString(), MsgType.TARGET)
            self.current_target = target
            
            

def main():
    module = CommsModule(SERVER_ADDRESS, SERVER_PORT, LOCAL_ADDRESS, LOCAL_PORT)
    module.run()

if __name__ == "__main__":
    main()
