from enum import Enum
from .target_pb2 import Target

class MsgType(Enum):
    TARGET = 0

message_buffers = {
    MsgType.TARGET: Target,
}


__all__ = ['MsgType', 'message_buffers', 'Target',]