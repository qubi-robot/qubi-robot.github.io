# Qubi Protocol

[![Documentation](https://img.shields.io/badge/docs-qubi--robot.github.io-blue)](https://qubi-robot.github.io)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Arduino](https://img.shields.io/badge/Arduino-compatible-orange)](libraries/arduino)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)](libraries/typescript)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow)](libraries/python)

A modular social robot communication protocol enabling real-time UDP-based control between web interfaces and ESP32 devices.

## 🚀 Quick Start

### ESP32 Servo Control

```arduino
#include <QubiProtocol.h>

ActuatorModule actuator;
Servo servo;

void setup() {
  servo.attach(9);
  actuator.begin("servo_01", QubiModuleType::ACTUATOR);
  
  actuator.setCommandHandler([](const QubiCommand& cmd) {
    if (cmd.action == "set_servo") {
      int angle = cmd.params["angle"];
      servo.write(angle);
      actuator.sendServoResponse(angle);
    }
  });
}

void loop() {
  actuator.processMessages();
}
```

### Web Interface Control

```typescript
import { QubiController, createCommandBuilder } from '@qubi/protocol';

const controller = new QubiController('192.168.1.100');
const builder = createCommandBuilder();

// Move servo to 90 degrees
const command = builder.actuator('servo_01').setServo(90);
const response = await controller.sendCommand(command);
```

### Python Automation

```python
from qubi_protocol import QubiController, create_command_builder

controller = QubiController("192.168.1.100")
builder = create_command_builder()

# Discover modules
modules = controller.discover()

# Control robot
command = builder.actuator("servo_01").set_servo(90)
response = controller.send_command(command)
```

## 📦 Features

- **🚀 Low Latency**: <10ms UDP communication
- **🔧 Modular Design**: Actuator, display, mobile, and sensor modules
- **🌐 Multi-Platform**: Arduino/ESP32, TypeScript, Python libraries
- **⚡ Type Safe**: Full TypeScript support with validation
- **📚 Well Documented**: Comprehensive guides and API references
- **🧪 Tested**: CI/CD with automated testing

## 🏗️ Architecture

```
┌─────────────────┐    UDP/JSON    ┌─────────────────┐
│   Web Interface │◄──────────────►│   ESP32 Module  │
│   (TypeScript)  │                │   (Arduino C++)  │
└─────────────────┘                └─────────────────┘
         ▲                                   ▲
         │                                   │
         ▼                                   ▼
┌─────────────────┐                ┌─────────────────┐
│ Python Scripts  │                │ Mobile Platform │
│  (Automation)   │                │    (Sensor)     │
└─────────────────┘                └─────────────────┘
```

## 📁 Project Structure

```
qubi-robot.github.io/
├── docs/                   # Docusaurus documentation
├── libraries/
│   ├── arduino/           # ESP32/Arduino library
│   ├── typescript/        # Web/Node.js library  
│   └── python/           # Python library
├── examples/             # Example implementations
├── .github/workflows/    # CI/CD automation
└── static/              # Documentation assets
```

## 🛠️ Installation

### Arduino/ESP32
```bash
# Arduino Library Manager
Tools → Manage Libraries → Search "QubiProtocol"
```

### TypeScript/JavaScript
```bash
npm install @qubi/protocol
```

### Python
```bash
pip install qubi-protocol
```

## 📖 Documentation

**Full documentation available at: [qubi-robot.github.io](https://qubi-robot.github.io)**

### Key Sections
- [Getting Started](https://qubi-robot.github.io/docs/getting-started/installation) - Setup and installation
- [Quick Start](https://qubi-robot.github.io/docs/getting-started/quick-start) - Build your first robot
- [Protocol Overview](https://qubi-robot.github.io/docs/protocol/overview) - Understand the communication protocol
- [API Reference](https://qubi-robot.github.io/docs/api-reference/arduino) - Complete API documentation
- [Examples](https://qubi-robot.github.io/docs/tutorials/custom-module) - Sample implementations

## 🔧 Protocol Overview

### Message Format
```json
{
  "version": "1.0",
  "timestamp": 1699123456789,
  "sequence": 42,
  "commands": [
    {
      "module_id": "servo_01",
      "module_type": "actuator",
      "action": "set_servo",
      "params": {
        "angle": 90,
        "speed": 128
      }
    }
  ]
}
```

### Module Types
- **Actuator**: Servo motors, linear actuators, robotic arms
- **Display**: LED matrices, facial expressions, eye movement
- **Mobile**: Wheels, tracks, locomotion systems
- **Sensor**: Cameras, distance sensors, environmental monitoring
- **Custom**: User-defined functionality

## 🚀 Examples

### Multi-Module Robot
```python
# Discover all modules
modules = controller.discover()

# Coordinate multiple modules
commands = [
    builder.actuator("arm_01").set_position(100, 50, 75),
    builder.display("face_01").set_expression("happy"),
    builder.mobile("base_01").move(0.5, 90, duration=2.0)
]

# Send batch commands
responses = controller.send_batch(commands)
```

### Real-time Sensor Monitoring
```typescript
// Stream sensor data
const sensorCmd = builder.sensor('distance_01').startStreaming('distance', 100);
await controller.sendCommand(sensorCmd);

// Handle responses
controller.on('response', (response) => {
  if (response.data?.sensor_type === 'distance') {
    console.log(`Distance: ${response.data.value}cm`);
  }
});
```

## 🧪 Development

### Build Documentation
```bash
npm install
npm run start      # Development server
npm run build      # Production build
```

### Test Libraries
```bash
# TypeScript
cd libraries/typescript
npm test

# Python  
cd libraries/python
pytest

# Arduino
arduino-cli compile --fqbn esp32:esp32:esp32 examples/ServoActuator/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://qubi-robot.github.io/docs/contributing/guidelines).

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Documentation**: [qubi-robot.github.io](https://qubi-robot.github.io)
- **Issues**: [GitHub Issues](https://github.com/qubi-robot/qubi-robot.github.io/issues)
- **Discussions**: [GitHub Discussions](https://github.com/qubi-robot/qubi-robot.github.io/discussions)

## 🌟 Showcase

Built something amazing with Qubi? We'd love to feature it! Share your projects in [GitHub Discussions](https://github.com/qubi-robot/qubi-robot.github.io/discussions).

---

**Made with ❤️ by the Qubi Project team**