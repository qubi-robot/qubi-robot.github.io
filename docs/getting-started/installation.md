---
sidebar_position: 1
---

# Installation

Get started with Qubi by installing the libraries for your preferred platform.

## Arduino/ESP32 Library

### Using Arduino Library Manager

1. Open Arduino IDE
2. Go to **Tools** → **Manage Libraries**
3. Search for "QubiProtocol"
4. Click **Install**

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/qubi-robot/qubi-robot.github.io/releases)
2. Extract to your Arduino libraries folder
3. Restart Arduino IDE

### Dependencies

The Arduino library requires:
- **ArduinoJson** (>=6.21.0)
- **WiFi** library (included with ESP32 core)

## TypeScript/JavaScript Library

### npm Installation

```bash
npm install @qubi/protocol
```

### yarn Installation

```bash
yarn add @qubi/protocol
```

### Requirements

- Node.js 20.x or higher
- TypeScript 5.x (optional, for TypeScript projects)

## Python Library

### pip Installation

```bash
pip install qubi-protocol
```

### Requirements

- Python 3.9 or higher
- No additional dependencies for basic usage

### Development Installation

For contributing to the Python library:

```bash
git clone https://github.com/qubi-robot/qubi-robot.github.io.git
cd qubi-robot.github.io/libraries/python
pip install -e ".[dev]"
```

## Verification

### Arduino

Create a simple test sketch:

```arduino
#include <QubiProtocol.h>

ActuatorModule actuator;

void setup() {
  Serial.begin(115200);
  
  if (actuator.begin("test_module", QubiModuleType::ACTUATOR)) {
    Serial.println("Qubi library installed correctly!");
  }
}

void loop() {
  actuator.processMessages();
}
```

### TypeScript/JavaScript

Create a test file:

```typescript
import { QubiController, createCommandBuilder } from '@qubi/protocol';

console.log('Qubi TypeScript library installed correctly!');

const controller = new QubiController('192.168.1.100');
const builder = createCommandBuilder();
```

### Python

Test the installation:

```python
import qubi_protocol

print("Qubi Python library installed correctly!")
print(f"Version: {qubi_protocol.__version__}")

# Test basic functionality
controller = qubi_protocol.QubiController("192.168.1.100")
builder = qubi_protocol.create_command_builder()
```

## Next Steps

Once you have the libraries installed, continue with the [Quick Start Guide](./quick-start.md) to build your first Qubi robot!