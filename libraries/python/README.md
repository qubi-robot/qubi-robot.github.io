# Qubi Protocol - Python Library

Python library for the Qubi modular social robot communication protocol.

## Installation

```bash
pip install qubi-protocol
```

## Quick Start

```python
from qubi_protocol import QubiController, create_command_builder

# Connect to a robot module
controller = QubiController("192.168.1.100")

# Create command builder
builder = create_command_builder()

# Control a servo actuator
servo_cmd = builder.actuator("servo_01").set_servo(90, speed=128)
response = controller.send_command(servo_cmd)

# Control display eyes
eyes_cmd = builder.display("display_01").set_eyes(50, 50, 60, 60)
controller.send_command(eyes_cmd)

# Discover modules on the network
modules = controller.discover()
for module in modules:
    print(f"Found: {module['id']} ({module['type']}) at {module['ip']}")
```

## Documentation

Full documentation is available at: https://qubi-robot.github.io

## License

MIT License