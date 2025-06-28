---
sidebar_position: 2
---

# Quick Start

Get up and running with Qubi in under 10 minutes! This guide will walk you through creating your first robot with a servo actuator and web control interface.

## What You'll Build

- ESP32 module controlling a servo motor
- Web interface to control the servo
- Real-time communication over WiFi

## Prerequisites

- ESP32 development board
- Servo motor (SG90 or similar)
- WiFi network
- Computer for development

## Step 1: Hardware Setup

Connect your servo to the ESP32:

- **Servo Red** → **ESP32 3.3V**
- **Servo Brown/Black** → **ESP32 GND**  
- **Servo Orange/Yellow** → **ESP32 GPIO 9**

## Step 2: ESP32 Code

Create a new Arduino sketch:

```arduino
#include <WiFi.h>
#include <Servo.h>
#include <QubiProtocol.h>

// WiFi credentials
const char* ssid = "your_wifi_name";
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
  
  // Start Qubi actuator
  if (actuator.begin("servo_01", QubiModuleType::ACTUATOR)) {
    Serial.println("Qubi actuator ready!");
  }
  
  // Set command handler
  actuator.setCommandHandler([](const QubiCommand& cmd) {
    if (cmd.action == "set_servo") {
      int angle = cmd.params["angle"];
      servo.write(angle);
      actuator.sendServoResponse(angle);
      Serial.printf("Servo moved to %d degrees\n", angle);
    }
  });
}

void loop() {
  actuator.processMessages();
  delay(10);
}
```

## Step 3: Web Control Interface

Create an HTML file for browser control:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Qubi Servo Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; }
        .slider { width: 100%; }
        .value { font-size: 24px; margin: 20px 0; }
        button { padding: 10px 20px; margin: 5px; }
    </style>
</head>
<body>
    <h1>Qubi Servo Control</h1>
    
    <div class="value">Angle: <span id="angle">90</span>°</div>
    
    <input type="range" min="0" max="180" value="90" 
           class="slider" id="angleSlider">
    
    <br><br>
    
    <button onclick="sendCommand()">Move Servo</button>
    <button onclick="centerServo()">Center (90°)</button>
    
    <div id="status"></div>

    <script type="module">
        import { QubiController, createCommandBuilder } from './qubi-protocol.js';
        
        // Replace with your ESP32's IP address
        const controller = new QubiController('192.168.1.100');
        const builder = createCommandBuilder();
        
        const angleSlider = document.getElementById('angleSlider');
        const angleDisplay = document.getElementById('angle');
        const status = document.getElementById('status');
        
        // Update display when slider moves
        angleSlider.addEventListener('input', function() {
            angleDisplay.textContent = this.value;
        });
        
        // Send servo command
        window.sendCommand = async function() {
            const angle = parseInt(angleSlider.value);
            
            try {
                const command = builder.actuator('servo_01').setServo(angle);
                const response = await controller.sendCommand(command);
                
                status.innerHTML = `<span style="color: green;">
                    ✓ Servo moved to ${angle}°</span>`;
            } catch (error) {
                status.innerHTML = `<span style="color: red;">
                    ✗ Error: ${error.message}</span>`;
            }
        };
        
        // Center servo
        window.centerServo = function() {
            angleSlider.value = 90;
            angleDisplay.textContent = '90';
            sendCommand();
        };
    </script>
</body>
</html>
```

## Step 4: Test Your Robot

1. **Upload the Arduino code** to your ESP32
2. **Note the IP address** printed in the Serial Monitor
3. **Update the IP address** in your HTML file
4. **Open the HTML file** in your browser
5. **Move the slider** and click "Move Servo"

You should see the servo move in real-time!

## Step 5: Discovery (Optional)

Test automatic module discovery:

```javascript
// Add this to your HTML script section
async function discoverModules() {
    try {
        const modules = await controller.discover();
        console.log('Found modules:', modules);
        
        modules.forEach(module => {
            console.log(`${module.id} (${module.type}) at ${module.ip}`);
        });
    } catch (error) {
        console.error('Discovery failed:', error);
    }
}

// Call discovery
discoverModules();
```

## Troubleshooting

### ESP32 Not Connecting
- Check WiFi credentials
- Ensure ESP32 is in range
- Verify power supply

### Commands Not Working
- Confirm IP address is correct
- Check firewall settings
- Ensure ESP32 and computer are on same network

### Servo Not Moving
- Verify wiring connections
- Check servo power supply
- Test servo with basic Arduino sketch first

## Next Steps

🎉 **Congratulations!** You've built your first Qubi robot. 

Now explore:
- [Protocol Overview](../protocol/overview.md) - Understand the communication protocol
- [Module Types](../modules/actuator.md) - Learn about different module types  
- [Advanced Tutorials](../tutorials/custom-module.md) - Build more complex robots
- [API Reference](../api-reference/arduino.md) - Deep dive into the libraries