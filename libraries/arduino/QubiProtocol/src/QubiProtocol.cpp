#include "QubiProtocol.h"

QubiModule::QubiModule() : _initialized(false), _port(QUBI_DEFAULT_PORT) {}

bool QubiModule::begin(const String& moduleId, QubiModuleType moduleType, uint16_t port) {
  _moduleId = moduleId;
  _moduleType = moduleType;
  _port = port;
  
  if (!_udp.begin(_port)) {
    Serial.println("Failed to start UDP server");
    return false;
  }
  
  _initialized = true;
  Serial.printf("Qubi module '%s' started on port %d\n", _moduleId.c_str(), _port);
  return true;
}

void QubiModule::end() {
  if (_initialized) {
    _udp.stop();
    _initialized = false;
  }
}

void QubiModule::processMessages() {
  if (!_initialized) return;
  
  int packetSize = _udp.parsePacket();
  if (packetSize > 0) {
    char buffer[QUBI_BUFFER_SIZE];
    int len = _udp.read(buffer, QUBI_BUFFER_SIZE - 1);
    buffer[len] = '\0';
    
    _lastClientIP = _udp.remoteIP();
    _lastClientPort = _udp.remotePort();
    
    QubiMessage message;
    if (parseMessage(buffer, message)) {
      // Process each command in the message
      for (uint8_t i = 0; i < message.commandCount; i++) {
        const QubiCommand& cmd = message.commands[i];
        
        // Check if this command is for our module
        if (cmd.moduleId == _moduleId || cmd.moduleId == "*") {
          if (_commandHandler) {
            _commandHandler(cmd);
          } else {
            handleCommand(cmd);
          }
        }
      }
    } else {
      sendError(QubiStatusCode::BAD_REQUEST, "Invalid message format");
    }
  }
}

bool QubiModule::parseMessage(const char* buffer, QubiMessage& message) {
  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, buffer);
  
  if (error) {
    Serial.printf("JSON parsing failed: %s\n", error.c_str());
    return false;
  }
  
  // Extract message fields
  message.version = doc["version"].as<String>();
  message.timestamp = doc["timestamp"].as<unsigned long>();
  message.sequence = doc["sequence"].as<uint32_t>();
  
  if (message.version != QUBI_PROTOCOL_VERSION) {
    Serial.printf("Unsupported protocol version: %s\n", message.version.c_str());
    return false;
  }
  
  // Parse commands array
  JsonArray commands = doc["commands"];
  message.commandCount = min((int)commands.size(), QUBI_MAX_COMMANDS);
  
  for (uint8_t i = 0; i < message.commandCount; i++) {
    JsonObject cmdObj = commands[i];
    QubiCommand& cmd = message.commands[i];
    
    cmd.moduleId = cmdObj["module_id"].as<String>();
    cmd.moduleType = stringToModuleType(cmdObj["module_type"].as<String>());
    cmd.action = cmdObj["action"].as<String>();
    cmd.params = cmdObj["params"].as<JsonObject>();
  }
  
  return true;
}

void QubiModule::handleCommand(const QubiCommand& cmd) {
  Serial.printf("Received command: %s.%s\n", cmd.moduleId.c_str(), cmd.action.c_str());
  sendError(QubiStatusCode::METHOD_NOT_ALLOWED, "Command handler not implemented");
}

void QubiModule::setCommandHandler(std::function<void(const QubiCommand&)> handler) {
  _commandHandler = handler;
}

void QubiModule::sendResponse(QubiStatusCode statusCode, const String& message, const JsonObject& data) {
  JsonDocument doc;
  doc["status"] = (int)statusCode;
  doc["message"] = message;
  doc["module_id"] = _moduleId;
  doc["timestamp"] = millis();
  
  if (!data.isNull()) {
    doc["data"] = data;
  }
  
  String response;
  serializeJson(doc, response);
  
  _udp.beginPacket(_lastClientIP, _lastClientPort);
  _udp.print(response);
  _udp.endPacket();
}

void QubiModule::sendSuccess(const String& message, const JsonObject& data) {
  sendResponse(QubiStatusCode::SUCCESS, message, data);
}

void QubiModule::sendError(QubiStatusCode code, const String& message) {
  sendResponse(code, message);
}

String QubiModule::moduleTypeToString(QubiModuleType type) {
  switch (type) {
    case QubiModuleType::ACTUATOR: return "actuator";
    case QubiModuleType::DISPLAY: return "display";
    case QubiModuleType::MOBILE: return "mobile";
    case QubiModuleType::SENSOR: return "sensor";
    case QubiModuleType::CUSTOM: return "custom";
    default: return "unknown";
  }
}

QubiModuleType QubiModule::stringToModuleType(const String& typeStr) {
  if (typeStr == "actuator") return QubiModuleType::ACTUATOR;
  if (typeStr == "display") return QubiModuleType::DISPLAY;
  if (typeStr == "mobile") return QubiModuleType::MOBILE;
  if (typeStr == "sensor") return QubiModuleType::SENSOR;
  if (typeStr == "custom") return QubiModuleType::CUSTOM;
  return QubiModuleType::CUSTOM;
}

// ActuatorModule implementations
void ActuatorModule::sendServoResponse(int angle, int speed) {
  QubiResponseBuilder builder;
  builder.addField("angle", angle);
  if (speed >= 0) {
    builder.addField("speed", speed);
  }
  sendSuccess("Servo position set", builder.build());
}

void ActuatorModule::sendPositionResponse(float x, float y, float z) {
  QubiResponseBuilder builder;
  builder.addField("x", x)
         .addField("y", y)
         .addField("z", z);
  sendSuccess("Position set", builder.build());
}

// DisplayModule implementations
void DisplayModule::sendEyesResponse(int leftX, int leftY, int rightX, int rightY, bool blink) {
  QubiResponseBuilder builder;
  JsonDocument doc;
  JsonObject leftEye = doc.createNestedObject("left_eye");
  leftEye["x"] = leftX;
  leftEye["y"] = leftY;
  JsonObject rightEye = doc.createNestedObject("right_eye");
  rightEye["x"] = rightX;
  rightEye["y"] = rightY;
  if (blink) {
    doc["blink"] = true;
  }
  sendSuccess("Eyes position set", doc.as<JsonObject>());
}

void DisplayModule::sendExpressionResponse(const String& expression, int intensity) {
  QubiResponseBuilder builder;
  builder.addField("expression", expression);
  if (intensity >= 0) {
    builder.addField("intensity", intensity);
  }
  sendSuccess("Expression set", builder.build());
}

// MobileModule implementations
void MobileModule::sendMovementResponse(float velocity, float direction) {
  QubiResponseBuilder builder;
  builder.addField("velocity", velocity)
         .addField("direction", direction);
  sendSuccess("Movement command executed", builder.build());
}

void MobileModule::sendLocationResponse(float x, float y, float heading) {
  QubiResponseBuilder builder;
  builder.addField("x", x)
         .addField("y", y)
         .addField("heading", heading);
  sendSuccess("Location updated", builder.build());
}

// SensorModule implementations
void SensorModule::sendSensorData(const String& sensorType, const JsonObject& data) {
  QubiResponseBuilder builder;
  builder.addField("sensor_type", sensorType);
  JsonDocument doc;
  doc["sensor_type"] = sensorType;
  doc["data"] = data;
  sendSuccess("Sensor data", doc.as<JsonObject>());
}

void SensorModule::sendSensorReading(const String& sensorType, float value, const String& unit) {
  QubiResponseBuilder builder;
  builder.addField("sensor_type", sensorType)
         .addField("value", value);
  if (unit.length() > 0) {
    builder.addField("unit", unit);
  }
  sendSuccess("Sensor reading", builder.build());
}

// QubiResponseBuilder implementations
QubiResponseBuilder::QubiResponseBuilder() {
  _data = _doc.to<JsonObject>();
}

QubiResponseBuilder& QubiResponseBuilder::addField(const String& key, const String& value) {
  _data[key] = value;
  return *this;
}

QubiResponseBuilder& QubiResponseBuilder::addField(const String& key, int value) {
  _data[key] = value;
  return *this;
}

QubiResponseBuilder& QubiResponseBuilder::addField(const String& key, float value) {
  _data[key] = value;
  return *this;
}

QubiResponseBuilder& QubiResponseBuilder::addField(const String& key, bool value) {
  _data[key] = value;
  return *this;
}

JsonObject QubiResponseBuilder::build() {
  return _data;
}