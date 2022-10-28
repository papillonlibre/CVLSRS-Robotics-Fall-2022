#!/usr/bin/env python3

# NAME: server.py
# PURPOSE: runs a robomodules server
# AUTHOR: Harvard Undergraduate Robotics Club

import robomodules
import os
from messages import MsgType

ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

def main():
    server = robomodules.Server(ADDRESS, PORT, MsgType)
    server.run()

if __name__ == "__main__":
    main()
