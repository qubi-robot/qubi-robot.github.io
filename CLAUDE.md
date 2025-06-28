# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Qubi Communication Protocol project - a modular social robot communication system implementing UDP-based JSON messaging between Web interfaces and ESP32 devices. The project targets GitHub Pages deployment with comprehensive multi-language library support.

## Architecture

The project follows a multi-component architecture as specified in `requirement.md`:

- **Communication Protocol**: UDP on port 8888, JSON message format with versioning and module commands
- **Module System**: Four primary module types (actuator, display, mobile, sensor) with extensible custom module support
- **Multi-Language Libraries**: C++/Arduino, TypeScript/Web, and Python implementations
- **Documentation System**: Docusaurus v3.x for GitHub Pages deployment

## Development Commands

Since this is a new project, these commands will be established as implementation progresses:

**Documentation (Docusaurus)**:
```bash
npm install          # Install dependencies
npm run start        # Development server
npm run build        # Production build
npm run serve        # Serve built site locally
```

**Testing** (when implemented):
```bash
npm run test         # Run all tests
npm run test:arduino # Arduino library tests
npm run test:python  # Python library tests
npm run test:ts      # TypeScript library tests
```

**Deployment**:
```bash
npm run deploy       # Deploy to GitHub Pages
```

## Key Implementation Details

**Protocol Specification**:
- Message format: `{"version": "1.0", "timestamp": <ms>, "sequence": <num>, "commands": [...]}`
- Module commands include `module_id`, `module_type`, `action`, and `params`
- Maximum packet size: 1024 bytes
- UTF-8 encoding required

**Library Structure Targets**:
- Arduino: `QubiModule` base class with derived `ActuatorModule`, `DisplayModule`, etc.
- TypeScript: `QubiController` class with type-safe `CommandBuilder` pattern
- Python: Mirror TypeScript API with Pythonic conventions

**Performance Requirements**:
- UDP latency: <10ms (local network)
- Message processing: 100+ messages/sec
- ESP32 memory usage: <50KB

## Development Workflow

1. Start with Docusaurus setup for documentation foundation
2. Implement core protocol definitions and JSON schemas
3. Develop Arduino/ESP32 library first (hardware foundation)
4. Create TypeScript web library with type safety
5. Build Python library for automation/scripting
6. Add comprehensive examples and tutorials
7. Implement CI/CD pipeline with GitHub Actions

## Important Files

- `requirement.md`: Complete Japanese specification document with all technical requirements
- Future `docs/`: Docusaurus documentation source
- Future `libraries/`: Multi-language implementation libraries
- Future `.github/workflows/`: CI/CD automation

## Module Action Reference

**Actuator Module**:
- `set_servo`: angle (0-180), speed (0-255), easing (linear|ease-in|ease-out)
- `set_position`: x, y, z coordinates in millimeters

**Display Module**:
- `set_eyes`: left_eye/right_eye {x, y} pixel coordinates, optional blink
- `set_expression`: expression (happy|sad|surprised|neutral|angry), intensity (0-100)