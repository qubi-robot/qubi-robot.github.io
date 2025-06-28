#ifndef QUBI_PROTOCOL_H
#define QUBI_PROTOCOL_H

#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <functional>

#define QUBI_PROTOCOL_VERSION "1.0"
#define QUBI_DEFAULT_PORT 8888
#define QUBI_BUFFER_SIZE 1024
#define QUBI_MAX_COMMANDS 16

enum class QubiModuleType {
  ACTUATOR,
  DISPLAY,
  MOBILE,
  SENSOR,
  CUSTOM
};

enum class QubiStatusCode {
  SUCCESS = 200,
  BAD_REQUEST = 400,
  NOT_FOUND = 404,
  METHOD_NOT_ALLOWED = 405,
  INTERNAL_ERROR = 500
};

struct QubiCommand {
  String moduleId;
  QubiModuleType moduleType;
  String action;
  JsonObject params;
};

struct QubiMessage {
  String version;
  unsigned long timestamp;
  uint32_t sequence;
  QubiCommand commands[QUBI_MAX_COMMANDS];
  uint8_t commandCount;
};

class QubiModule {
protected:
  String _moduleId;
  QubiModuleType _moduleType;
  WiFiUDP _udp;
  uint16_t _port;
  bool _initialized;
  IPAddress _lastClientIP;
  uint16_t _lastClientPort;
  
  // Command handler function pointer
  std::function<void(const QubiCommand&)> _commandHandler;
  
  // Internal methods
  bool parseMessage(const char* buffer, QubiMessage& message);
  void sendResponse(QubiStatusCode statusCode, const String& message, const JsonObject& data = JsonObject());
  String moduleTypeToString(QubiModuleType type);
  QubiModuleType stringToModuleType(const String& typeStr);
  
public:
  QubiModule();
  virtual ~QubiModule() = default;
  
  // Initialization
  bool begin(const String& moduleId, QubiModuleType moduleType, uint16_t port = QUBI_DEFAULT_PORT);
  void end();
  
  // Main loop method - call this regularly
  void processMessages();
  
  // Command handling - override this or set a handler function
  virtual void handleCommand(const QubiCommand& cmd);
  void setCommandHandler(std::function<void(const QubiCommand&)> handler);
  
  // Utility methods
  bool isInitialized() const { return _initialized; }
  String getModuleId() const { return _moduleId; }
  QubiModuleType getModuleType() const { return _moduleType; }
  uint16_t getPort() const { return _port; }
  
  // Response helpers
  void sendSuccess(const String& message = "OK", const JsonObject& data = JsonObject());
  void sendError(QubiStatusCode code, const String& message);
};

// Specialized module classes
class ActuatorModule : public QubiModule {
public:
  ActuatorModule() { _moduleType = QubiModuleType::ACTUATOR; }
  
  // Actuator-specific helpers
  void sendServoResponse(int angle, int speed = -1);
  void sendPositionResponse(float x, float y, float z);
};

class DisplayModule : public QubiModule {
public:
  DisplayModule() { _moduleType = QubiModuleType::DISPLAY; }
  
  // Display-specific helpers
  void sendEyesResponse(int leftX, int leftY, int rightX, int rightY, bool blink = false);
  void sendExpressionResponse(const String& expression, int intensity = -1);
};

class MobileModule : public QubiModule {
public:
  MobileModule() { _moduleType = QubiModuleType::MOBILE; }
  
  // Mobile-specific helpers
  void sendMovementResponse(float velocity, float direction);
  void sendLocationResponse(float x, float y, float heading);
};

class SensorModule : public QubiModule {
public:
  SensorModule() { _moduleType = QubiModuleType::SENSOR; }
  
  // Sensor-specific helpers
  void sendSensorData(const String& sensorType, const JsonObject& data);
  void sendSensorReading(const String& sensorType, float value, const String& unit = "");
};

// Utility class for building responses
class QubiResponseBuilder {
private:
  JsonDocument _doc;
  JsonObject _data;
  
public:
  QubiResponseBuilder();
  QubiResponseBuilder& addField(const String& key, const String& value);
  QubiResponseBuilder& addField(const String& key, int value);
  QubiResponseBuilder& addField(const String& key, float value);
  QubiResponseBuilder& addField(const String& key, bool value);
  JsonObject build();
};

#endif // QUBI_PROTOCOL_H