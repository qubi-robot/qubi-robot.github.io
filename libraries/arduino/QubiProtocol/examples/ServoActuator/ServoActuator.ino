#include <WiFi.h>
#include <Servo.h>
#include <QubiProtocol.h>

// WiFi credentials
const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";

// Hardware
Servo servo;
const int servoPin = 9;

// Qubi module
ActuatorModule actuator;

void setup() {
  Serial.begin(115200);
  
  // Initialize servo
  servo.attach(servoPin);
  servo.write(90); // Center position
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Initialize Qubi actuator module
  if (actuator.begin("servo_01", QubiModuleType::ACTUATOR)) {
    Serial.println("Actuator module started successfully");
  } else {
    Serial.println("Failed to start actuator module");
  }
  
  // Set command handler
  actuator.setCommandHandler([](const QubiCommand& cmd) {
    handleActuatorCommand(cmd);
  });
}

void loop() {
  // Process incoming Qubi messages
  actuator.processMessages();
  
  // Add your other loop code here
  delay(10);
}

void handleActuatorCommand(const QubiCommand& cmd) {
  if (cmd.action == "set_servo") {
    int angle = cmd.params["angle"];
    int speed = cmd.params["speed"] | 255; // Default to max speed if not specified
    
    // Validate angle range
    if (angle < 0 || angle > 180) {
      actuator.sendError(QubiStatusCode::BAD_REQUEST, "Angle must be between 0 and 180");
      return;
    }
    
    // Move servo to position
    servo.write(angle);
    
    // Send response
    actuator.sendServoResponse(angle, speed);
    
    Serial.printf("Servo moved to %d degrees\n", angle);
    
  } else if (cmd.action == "get_position") {
    // Return current servo position
    int currentAngle = servo.read();
    actuator.sendServoResponse(currentAngle);
    
  } else {
    actuator.sendError(QubiStatusCode::METHOD_NOT_ALLOWED, "Unknown action: " + cmd.action);
  }
}