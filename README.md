# CVLSRS Competition Starter Code

Welcome to the official starter code for the 2022 CVLSRS (Computer Vision Laser Space Robot Satellite) Competition!

This code is implemented using Robomodules, a Python framework that models a robot as a set of isolated modules that pass messages between each other over a server. In genral, modules publish messages of specified types to the server, which are then picked up and processed by the modules subscribed to those message types. For more information on Robomodules, see the [official documentation](https://github.com/HarvardURC/robomodules#robomodules).

## Messages

This starter code contains one message type. Further message types can be created as follows:

1. Create a `.proto` file in the messages directory specifying the data types/structures you want in your message. The full list of supported data types can be found [here](https://developers.google.com/protocol-buffers/docs/reference/proto2-spec).
2. From inside the messages directory, compile that `.proto` file into python code with `protoc -I=./ --python_out=./ ./<path to proto file>` (for example, to compile `target.proto` I used `protoc -I=./ --python_out=./ ./target.proto`)
3. In `__init__.py`, add an entry to the `MsgType` enum for your new message type (just copy the format of the `TARGET` one, but with a new integer value).
4. Also in `__init__.py`, import the auto-generated message class from the file crated with that `protoc` command (should be `<message name>_pb2.py`) and add it to the message_buffers mapping (again, just follow the format of the `Target` one).

## Modules

This starter code comes with two modules:

* [Comms Module](comms_module.py): Picks up Target messages from a remote game server and forwards them to the local server that your own modules will run on.
* [Target Sender Module](target_sender_module.py): For use in testing; generates and sends randomized Target messages over your local robomodules server (as an alternative to picking them up from a separate game server).

Further modules (for catching and handling these target messages, image processing, motor driving, etc) will be designed and implemented by you! For more information on how to create modules, see the [official Robomodules documentation](https://github.com/HarvardURC/robomodules#mocksensormodulepy), as well as the [blank module template](blank_module.py) provided in this code!

### Target

During the competition, your code will accept Target messages from the game server. Each target message contains two enum values: a shape and a color. The definitions for these enums can be found [here](messages/target.proto).

## How to Run

First, run a local robomodules server on the Raspberry Pi with `python3 server.py`. This will allow your local modules to send messages between each other.

### Receiving Target Messages

You can receive Target messages in one of two ways: forwarded onto your local server from a remote game server by the comms module (for use in actual competition), or locally from an instance of the target_sender_module.py. Both methods will be detailed below:

#### From Remote Game Server

First, you'll need the IP address and port of the remote game server. Then, execute the following commands:

1. `export BIND_ADDRESS=<game server ip>` (for example, if the game serve rwas running on 192.168.0.52, this would be `export BIND_ADDRESS=192.168.0.52`)
2. `export BIND_PORT=<game server port>`
3. `python3 comms_module.py`

This will start up an instance of the comms module that picks up messages from that game server and forwards them to your local server (assuming that local server is running on the default IP `localhost` and port `11295`)

#### From Local Module

For testing, you can also just run a version of the target sender module- which is included in this repository- locally. For this, just run `python3 target_sender_module.py` (no need to set any special environment variables since its running on your local Robomodules server). Any time you press the enter key while in this command line window, a new Target command will be generated and send to your local robomodules server.