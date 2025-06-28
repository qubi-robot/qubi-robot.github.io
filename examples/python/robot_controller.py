#!/usr/bin/env python3
"""
Advanced Qubi Robot Controller

This example demonstrates advanced robot control using multiple modules,
sequence tracking, error handling, and autonomous behaviors.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any

from qubi_protocol import (
    QubiController,
    create_command_builder,
    QubiError,
    QubiTimeoutError,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RobotController:
    """Advanced robot controller with multiple module support."""
    
    def __init__(self, robot_ip: str):
        self.robot_ip = robot_ip
        self.controller = QubiController(robot_ip, sequence_tracking=True)
        self.builder = create_command_builder()
        
        # Module tracking
        self.discovered_modules: Dict[str, Any] = {}
        self.module_status: Dict[str, str] = {}
        
        # Set up event handlers
        self.controller.add_response_handler(self._on_response)
        self.controller.add_error_handler(self._on_error)
    
    def _on_response(self, response, addr):
        """Handle incoming responses."""
        logger.info(f"Response from {response['module_id']}: {response['message']}")
        
        # Update module status
        self.module_status[response['module_id']] = 'active'
    
    def _on_error(self, error):
        """Handle errors."""
        logger.error(f"Error: {error}")
    
    async def discover_modules(self) -> List[Dict[str, Any]]:
        """Discover available modules."""
        logger.info("Discovering modules...")
        
        try:
            modules = self.controller.discover(timeout=5.0)
            self.discovered_modules = {m['id']: m for m in modules}
            
            logger.info(f"Discovered {len(modules)} modules:")
            for module in modules:
                logger.info(f"  - {module['id']} ({module['type']}) at {module['ip']}")
                
            return modules
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            return []
    
    def get_modules_by_type(self, module_type: str) -> List[Dict[str, Any]]:
        """Get modules of a specific type."""
        return [m for m in self.discovered_modules.values() if m['type'] == module_type]
    
    def set_servo_position(self, module_id: str, angle: int, speed: int = 128):
        """Control a servo actuator."""
        try:
            command = self.builder.actuator(module_id).set_servo(angle, speed)
            response = self.controller.send_command(command)
            logger.info(f"Servo {module_id} moved to {angle}°")
            return response
        except QubiError as e:
            logger.error(f"Failed to control servo {module_id}: {e}")
            raise
    
    def set_robot_expression(self, module_id: str, expression: str, intensity: int = 80):
        """Set robot facial expression."""
        try:
            command = self.builder.display(module_id).set_expression(expression, intensity)
            response = self.controller.send_command(command)
            logger.info(f"Expression set to {expression} (intensity: {intensity})")
            return response
        except QubiError as e:
            logger.error(f"Failed to set expression: {e}")
            raise
    
    def look_at_position(self, display_id: str, x: int, y: int):
        """Make robot look at a specific position."""
        try:
            # Set both eyes to look at the same position
            command = self.builder.display(display_id).set_eyes(x, y, x, y)
            response = self.controller.send_command(command)
            logger.info(f"Robot looking at position ({x}, {y})")
            return response
        except QubiError as e:
            logger.error(f"Failed to set eye position: {e}")
            raise
    
    def move_robot(self, mobile_id: str, velocity: float, direction: float, duration: float = None):
        """Move the robot."""
        try:
            command = self.builder.mobile(mobile_id).move(velocity, direction, duration)
            response = self.controller.send_command(command)
            logger.info(f"Robot moving: velocity={velocity}, direction={direction}")
            return response
        except QubiError as e:
            logger.error(f"Failed to move robot: {e}")
            raise
    
    def read_sensors(self, sensor_id: str):
        """Read sensor data."""
        try:
            command = self.builder.sensor(sensor_id).read()
            response = self.controller.send_command(command)
            logger.info(f"Sensor reading: {response.get('data', {})}")
            return response
        except QubiError as e:
            logger.error(f"Failed to read sensor {sensor_id}: {e}")
            raise
    
    def emergency_stop(self):
        """Stop all robot movement immediately."""
        logger.warning("EMERGENCY STOP activated!")
        
        # Stop all actuators and mobile modules
        commands = []
        
        for module in self.discovered_modules.values():
            if module['type'] == 'actuator':
                commands.append(self.builder.actuator(module['id']).stop())
            elif module['type'] == 'mobile':
                commands.append(self.builder.mobile(module['id']).stop())
        
        if commands:
            try:
                responses = self.controller.send_batch(commands)
                logger.info("Emergency stop completed")
                return responses
            except QubiError as e:
                logger.error(f"Emergency stop failed: {e}")
                raise
    
    def close(self):
        """Clean up resources."""
        self.controller.close()


async def demo_sequence(robot: RobotController):
    """Demonstrate various robot capabilities."""
    
    # Discover modules
    modules = await robot.discover_modules()
    if not modules:
        logger.error("No modules found!")
        return
    
    # Get modules by type
    actuators = robot.get_modules_by_type('actuator')
    displays = robot.get_modules_by_type('display')
    mobile = robot.get_modules_by_type('mobile')
    sensors = robot.get_modules_by_type('sensor')
    
    logger.info("\n=== Starting Demo Sequence ===")
    
    try:
        # 1. Greeting sequence
        if displays:
            display_id = displays[0]['id']
            robot.set_robot_expression(display_id, 'happy', 90)
            await asyncio.sleep(1)
            
            # Look around
            for x, y in [(20, 30), (80, 30), (50, 50)]:
                robot.look_at_position(display_id, x, y)
                await asyncio.sleep(0.5)
        
        # 2. Servo demonstration
        if actuators:
            servo_id = actuators[0]['id']
            logger.info("Servo demonstration...")
            
            # Sweep servo
            for angle in [0, 45, 90, 135, 180, 90]:
                robot.set_servo_position(servo_id, angle, 100)
                await asyncio.sleep(0.8)
        
        # 3. Sensor reading
        if sensors:
            sensor_id = sensors[0]['id']
            logger.info("Reading sensors...")
            robot.read_sensors(sensor_id)
        
        # 4. Movement demo (if mobile platform available)
        if mobile:
            mobile_id = mobile[0]['id']
            logger.info("Movement demonstration...")
            
            # Move in a small circle
            for direction in [0, 90, 180, 270]:
                robot.move_robot(mobile_id, 0.3, direction, 1.0)
                await asyncio.sleep(1.2)
            
            # Stop
            robot.move_robot(mobile_id, 0, 0)
        
        # 5. Expressions demo
        if displays:
            display_id = displays[0]['id']
            expressions = ['happy', 'surprised', 'sad', 'angry', 'neutral']
            
            logger.info("Expression demonstration...")
            for expr in expressions:
                robot.set_robot_expression(display_id, expr, 85)
                await asyncio.sleep(1.5)
        
        logger.info("=== Demo sequence completed ===")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        robot.emergency_stop()


async def autonomous_behavior(robot: RobotController):
    """Simple autonomous behavior loop."""
    
    displays = robot.get_modules_by_type('display')
    sensors = robot.get_modules_by_type('sensor')
    
    if not displays or not sensors:
        logger.info("Autonomous behavior requires display and sensor modules")
        return
    
    display_id = displays[0]['id']
    sensor_id = sensors[0]['id']
    
    logger.info("Starting autonomous behavior...")
    
    try:
        while True:
            # Read sensor
            sensor_response = robot.read_sensors(sensor_id)
            sensor_data = sensor_response.get('data', {})
            
            # React based on sensor data
            if 'distance' in sensor_data:
                distance = sensor_data['distance']
                
                if distance < 20:  # Close object
                    robot.set_robot_expression(display_id, 'surprised')
                    robot.look_at_position(display_id, 50, 20)  # Look down
                elif distance > 100:  # Far/no object
                    robot.set_robot_expression(display_id, 'neutral')
                    robot.look_at_position(display_id, 50, 50)  # Look forward
                else:  # Medium distance
                    robot.set_robot_expression(display_id, 'happy')
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        logger.info("Autonomous behavior stopped by user")
    except Exception as e:
        logger.error(f"Autonomous behavior error: {e}")


async def main():
    """Main application entry point."""
    
    # Configuration
    ROBOT_IP = "192.168.1.100"  # Change to your robot's IP
    
    # Create robot controller
    robot = RobotController(ROBOT_IP)
    
    try:
        # Run demo sequence
        await demo_sequence(robot)
        
        # Uncomment to run autonomous behavior
        # await autonomous_behavior(robot)
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        robot.close()


if __name__ == "__main__":
    asyncio.run(main())