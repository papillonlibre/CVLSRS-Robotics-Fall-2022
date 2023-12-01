#!/usr/bin/env python3

# NAME: motor_module.py
# PURPOSE: controlling tilt and rotation motors based on TiltCommand and 
#          RotationCommand messages
# AUTHOR: Emma Bethel
# NOTE: this module works best using the pigpio GPIO pin factory, rather than 
#       the default one. to change this, run 
#           export GPIOZERO_PIN_FACTORY=pigpio
#           sudo pigpiod
#       in the command line before running the module.

import os
import robomodules as rm

from gpiozero import PhaseEnableMotor, Servo, RotaryEncoder
from messages import MsgType, message_buffers
from simple_pid import PID


# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 60
MAX_ANGLE= 60

SERVO_PIN = 25
DC_PINS = (5, 12)
ENCODER_PINS = (17, 18)


class MotorModule(rm.ProtoModule):
    # sets up the module (subscriptions, connection to server, etc)
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.ROTATION_COMMAND, MsgType.TILT_COMMAND]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)

        # initializing motors and encoder
        self.tilt_motor = Servo(SERVO_PIN)
        self.rotation_motor = PhaseEnableMotor(*DC_PINS)
        self.encoder = RotaryEncoder(*ENCODER_PINS, max_steps=0)

        # setting up PID controller
        self.pid = PID(0.075, 0, 0)
        self.pid.sample_time = 0.01
        self.pid.output_limits = (-1.0, 1.0)
        self.pid.setpoint = 0

    # runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        if msg_type == MsgType.ROTATION_COMMAND:
            print('received rotation command', msg)
            # setting new target position
            target_pos = round(msg.position * MAX_ANGLE)
            if target_pos > MAX_ANGLE:
                target_pos = MAX_ANGLE
            elif target_pos < -MAX_ANGLE:
                target_pos = -MAX_ANGLE
            self.pid.setpoint = target_pos

            # setting new speed cap
            max_speed = min(1.0, abs(msg.max_speed))
            self.pid.output_limits = (-max_speed, max_speed)

        elif msg_type == MsgType.TILT_COMMAND:
            print('received tilt command', msg)
            self._tilt(msg.position)

    # runs every 1 / FREQUENCY seconds
    def tick(self):
        # picking rotation speed and direction based on PID controller
        current_pos = self.encoder.steps
        v = self.pid(current_pos)
        print(current_pos)
        if v > 0:
            drive_func = self.rotation_motor.forward
        else:
            drive_func = self.rotation_motor.backward
        
        # driving rotation motor w/ given speed and direction
        drive_func(abs(v))
    
    def _tilt(self, desired_position):
        if desired_position < -1:
            desired_position = -1
        elif desired_position > 1:
            desired_position = 1

        self.tilt_motor.value = desired_position
        

def main():
    module = MotorModule(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()
