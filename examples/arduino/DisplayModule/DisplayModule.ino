#include <WiFi.h>
#include <QubiProtocol.h>

// WiFi credentials
const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";

// Display hardware pins (adjust for your setup)
const int leftEyeLEDPin = 2;
const int rightEyeLEDPin = 4;
const int brightnessPin = 5;

// Qubi module
DisplayModule display;

// Current state
int currentLeftX = 50, currentLeftY = 50;
int currentRightX = 50, currentRightY = 50;
String currentExpression = "neutral";
int currentBrightness = 100;

void setup() {
  Serial.begin(115200);
  
  // Initialize hardware
  pinMode(leftEyeLEDPin, OUTPUT);
  pinMode(rightEyeLEDPin, OUTPUT);
  pinMode(brightnessPin, OUTPUT);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Initialize Qubi display module
  if (display.begin("display_01", QubiModuleType::DISPLAY)) {
    Serial.println("Display module started successfully");
  } else {
    Serial.println("Failed to start display module");
    return;
  }
  
  // Set command handler
  display.setCommandHandler([](const QubiCommand& cmd) {
    handleDisplayCommand(cmd);
  });
  
  // Set initial state
  updateDisplay();
}

void loop() {
  // Process incoming Qubi messages
  display.processMessages();
  
  // Add any animation or autonomous behavior here
  
  delay(10);
}

void handleDisplayCommand(const QubiCommand& cmd) {
  if (cmd.action == "set_eyes") {
    // Extract eye positions
    JsonObject leftEye = cmd.params["left_eye"];
    JsonObject rightEye = cmd.params["right_eye"];
    
    currentLeftX = leftEye["x"];
    currentLeftY = leftEye["y"];
    currentRightX = rightEye["x"];
    currentRightY = rightEye["y"];
    
    bool blink = cmd.params["blink"] | false;
    
    updateEyes();
    
    if (blink) {
      performBlink();
    }
    
    // Send response
    display.sendEyesResponse(currentLeftX, currentLeftY, 
                           currentRightX, currentRightY, blink);
    
    Serial.printf("Eyes set to Left(%d,%d) Right(%d,%d)\n", 
                  currentLeftX, currentLeftY, currentRightX, currentRightY);
    
  } else if (cmd.action == "set_expression") {
    currentExpression = cmd.params["expression"].as<String>();
    int intensity = cmd.params["intensity"] | 100;
    
    setExpression(currentExpression, intensity);
    
    // Send response
    display.sendExpressionResponse(currentExpression, intensity);
    
    Serial.printf("Expression set to %s (intensity: %d)\n", 
                  currentExpression.c_str(), intensity);
    
  } else if (cmd.action == "set_brightness") {
    currentBrightness = cmd.params["brightness"];
    
    // Validate brightness range
    if (currentBrightness < 0 || currentBrightness > 100) {
      display.sendError(QubiStatusCode::BAD_REQUEST, "Brightness must be 0-100");
      return;
    }
    
    setBrightness(currentBrightness);
    
    // Send response
    QubiResponseBuilder builder;
    builder.addField("brightness", currentBrightness);
    display.sendSuccess("Brightness set", builder.build());
    
    Serial.printf("Brightness set to %d%%\n", currentBrightness);
    
  } else if (cmd.action == "clear_display") {
    clearDisplay();
    
    display.sendSuccess("Display cleared");
    Serial.println("Display cleared");
    
  } else if (cmd.action == "get_status") {
    // Send current status
    QubiResponseBuilder builder;
    builder.addField("left_x", currentLeftX)
           .addField("left_y", currentLeftY)
           .addField("right_x", currentRightX)
           .addField("right_y", currentRightY)
           .addField("expression", currentExpression)
           .addField("brightness", currentBrightness);
    
    display.sendSuccess("Status retrieved", builder.build());
    
  } else {
    display.sendError(QubiStatusCode::METHOD_NOT_ALLOWED, "Unknown action: " + cmd.action);
  }
}

void updateDisplay() {
  updateEyes();
  setBrightness(currentBrightness);
}

void updateEyes() {
  // Simple LED control based on eye position
  // In a real implementation, you might control servo motors or LED matrices
  
  // Map eye positions to LED brightness
  int leftBrightness = map(currentLeftX + currentLeftY, 0, 200, 0, 255);
  int rightBrightness = map(currentRightX + currentRightY, 0, 200, 0, 255);
  
  analogWrite(leftEyeLEDPin, leftBrightness);
  analogWrite(rightEyeLEDPin, rightBrightness);
}

void setExpression(const String& expression, int intensity) {
  // Implement expression patterns
  if (expression == "happy") {
    // Bright, quick blinking pattern
    for (int i = 0; i < 3; i++) {
      digitalWrite(leftEyeLEDPin, HIGH);
      digitalWrite(rightEyeLEDPin, HIGH);
      delay(100);
      digitalWrite(leftEyeLEDPin, LOW);
      digitalWrite(rightEyeLEDPin, LOW);
      delay(100);
    }
  } else if (expression == "sad") {
    // Dim, slow fade
    for (int brightness = 255; brightness >= 0; brightness -= 5) {
      analogWrite(leftEyeLEDPin, brightness * intensity / 100);
      analogWrite(rightEyeLEDPin, brightness * intensity / 100);
      delay(20);
    }
  } else if (expression == "surprised") {
    // Sudden bright flash
    digitalWrite(leftEyeLEDPin, HIGH);
    digitalWrite(rightEyeLEDPin, HIGH);
    delay(500);
    digitalWrite(leftEyeLEDPin, LOW);
    digitalWrite(rightEyeLEDPin, LOW);
  } else if (expression == "angry") {
    // Rapid flashing
    for (int i = 0; i < 10; i++) {
      digitalWrite(leftEyeLEDPin, HIGH);
      digitalWrite(rightEyeLEDPin, HIGH);
      delay(50);
      digitalWrite(leftEyeLEDPin, LOW);
      digitalWrite(rightEyeLEDPin, LOW);
      delay(50);
    }
  }
  
  // Return to normal eye position
  updateEyes();
}

void performBlink() {
  // Simple blink animation
  digitalWrite(leftEyeLEDPin, LOW);
  digitalWrite(rightEyeLEDPin, LOW);
  delay(150);
  updateEyes();
}

void setBrightness(int brightness) {
  // Control overall brightness using PWM
  int pwmValue = map(brightness, 0, 100, 0, 255);
  analogWrite(brightnessPin, pwmValue);
}

void clearDisplay() {
  digitalWrite(leftEyeLEDPin, LOW);
  digitalWrite(rightEyeLEDPin, LOW);
  digitalWrite(brightnessPin, LOW);
  
  // Reset state
  currentLeftX = currentLeftY = 0;
  currentRightX = currentRightY = 0;
  currentExpression = "neutral";
  currentBrightness = 0;
}