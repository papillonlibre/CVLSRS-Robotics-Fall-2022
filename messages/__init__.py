from enum import Enum
from .target_pb2 import Target
from .rotationCommand_pb2 import RotationCommand
from .tiltCommand_pb2 import TiltCommand
from .emitterCommand_pb2 import EmitterCommand

class MsgType(Enum):
    TARGET = 0
    TILT_COMMAND = 1
    ROTATION_COMMAND = 2
    EMITTER_COMMAND = 3

message_buffers = {
    MsgType.TARGET: Target,
    MsgType.TILT_COMMAND: TiltCommand,
    MsgType.ROTATION_COMMAND: RotationCommand,
    MsgType.EMITTER_COMMAND: EmitterCommand
}


__all__ = ['MsgType', 'message_buffers', 'Target', 'TiltCommand', 'RotationCommand', 'EmitterCommand']