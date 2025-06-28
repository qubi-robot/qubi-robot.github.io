---
sidebar_position: 1
---

# Introduction

Welcome to the **Qubi Protocol** documentation! Qubi is a modular social robot communication protocol that enables seamless UDP-based communication between web interfaces and ESP32 devices.

## What is Qubi?

Qubi is designed for modular social robots where different components (actuators, displays, sensors, and mobile platforms) need to work together through a unified communication protocol. The system uses UDP messaging with JSON payloads to ensure low-latency, real-time control.

## Key Features

- **🚀 Low Latency**: UDP-based communication with &lt;10ms latency
- **📦 Modular Design**: Support for actuator, display, mobile, and sensor modules
- **🌐 Multi-Language**: Libraries for Arduino/ESP32, TypeScript, and Python
- **🔧 Type Safe**: Full TypeScript support with command builders
- **📚 Well Documented**: Comprehensive guides and API references
- **🧪 Tested**: Unit and integration tests for all components

## Protocol Overview

The Qubi protocol uses JSON messages sent over UDP port 8888 (configurable). Each message contains:

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

## Getting Started

Ready to build your first Qubi robot? Check out our [Installation Guide](./getting-started/installation.md) to get started!

## Libraries

Choose your preferred language:

- **[Arduino/ESP32](./api-reference/arduino.md)**: For embedded device control
- **[TypeScript](./api-reference/typescript.md)**: For web interfaces and Node.js applications  
- **[Python](./api-reference/python.md)**: For automation scripts and AI integration