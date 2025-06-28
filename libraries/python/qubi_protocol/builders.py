"""Command builders for creating type-safe Qubi commands."""

from typing import Dict, Any, Optional, Union

from .types import (
    QubiCommand,
    ModuleType,
    ServoParams,
    PositionParams,
    EyesParams,
    ExpressionParams,
    MovementParams,
    LocationParams,
    Expression,
)
from .errors import QubiValidationError


class BaseCommandBuilder:
    """Base class for command builders."""
    
    def __init__(self, module_id: str, module_type: ModuleType):
        self.module_id = module_id
        self.module_type = module_type
    
    def _create_command(self, action: str, params: Dict[str, Any]) -> QubiCommand:
        """Create a command with the given action and parameters."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "action": action,
            "params": params,
        }


class ActuatorCommandBuilder(BaseCommandBuilder):
    """Builder for actuator module commands."""
    
    def __init__(self, module_id: str):
        super().__init__(module_id, "actuator")
    
    def set_servo(self, angle: int, speed: Optional[int] = None, 
                  easing: Optional[str] = None) -> QubiCommand:
        """Create a servo control command."""
        self._validate_servo_params(angle, speed, easing)
        
        params: Dict[str, Union[int, str]] = {"angle": angle}
        if speed is not None:
            params["speed"] = speed
        if easing is not None:
            params["easing"] = easing
        
        return self._create_command("set_servo", params)
    
    def set_position(self, x: float, y: float, z: float) -> QubiCommand:
        """Create a 3D position command."""
        self._validate_position_params(x, y, z)
        
        params = {"x": x, "y": y, "z": z}
        return self._create_command("set_position", params)
    
    def get_position(self) -> QubiCommand:
        """Create a position query command."""
        return self._create_command("get_position", {})
    
    def stop(self) -> QubiCommand:
        """Create a stop command."""
        return self._create_command("stop", {})
    
    def _validate_servo_params(self, angle: int, speed: Optional[int], 
                              easing: Optional[str]) -> None:
        """Validate servo command parameters."""
        if not isinstance(angle, int) or angle < 0 or angle > 180:
            raise QubiValidationError("Servo angle must be an integer between 0 and 180")
        
        if speed is not None and (not isinstance(speed, int) or speed < 0 or speed > 255):
            raise QubiValidationError("Servo speed must be an integer between 0 and 255")
        
        if easing is not None:
            valid_easing = ["linear", "ease-in", "ease-out"]
            if easing not in valid_easing:
                raise QubiValidationError(f"Invalid easing type: {easing}")
    
    def _validate_position_params(self, x: float, y: float, z: float) -> None:
        """Validate position command parameters."""
        for coord, name in [(x, "x"), (y, "y"), (z, "z")]:
            if not isinstance(coord, (int, float)) or not (-float('inf') < coord < float('inf')):
                raise QubiValidationError(f"Position coordinate {name} must be a finite number")


class DisplayCommandBuilder(BaseCommandBuilder):
    """Builder for display module commands."""
    
    def __init__(self, module_id: str):
        super().__init__(module_id, "display")
    
    def set_eyes(self, left_x: int, left_y: int, right_x: int, right_y: int,
                 blink: Optional[bool] = None) -> QubiCommand:
        """Create an eye position command."""
        self._validate_eye_position(left_x, left_y, "left")
        self._validate_eye_position(right_x, right_y, "right")
        
        params: Dict[str, Any] = {
            "left_eye": {"x": left_x, "y": left_y},
            "right_eye": {"x": right_x, "y": right_y},
        }
        
        if blink is not None:
            params["blink"] = blink
        
        return self._create_command("set_eyes", params)
    
    def set_expression(self, expression: Expression, 
                      intensity: Optional[int] = None) -> QubiCommand:
        """Create a facial expression command."""
        self._validate_expression_params(expression, intensity)
        
        params: Dict[str, Union[str, int]] = {"expression": expression}
        if intensity is not None:
            params["intensity"] = intensity
        
        return self._create_command("set_expression", params)
    
    def clear_display(self) -> QubiCommand:
        """Create a clear display command."""
        return self._create_command("clear_display", {})
    
    def set_brightness(self, brightness: int) -> QubiCommand:
        """Create a brightness control command."""
        if not isinstance(brightness, int) or brightness < 0 or brightness > 100:
            raise QubiValidationError("Brightness must be an integer between 0 and 100")
        
        return self._create_command("set_brightness", {"brightness": brightness})
    
    def _validate_eye_position(self, x: int, y: int, eye_name: str) -> None:
        """Validate eye position parameters."""
        if not isinstance(x, int) or x < 0:
            raise QubiValidationError(f"{eye_name} eye x coordinate must be a non-negative integer")
        if not isinstance(y, int) or y < 0:
            raise QubiValidationError(f"{eye_name} eye y coordinate must be a non-negative integer")
    
    def _validate_expression_params(self, expression: str, intensity: Optional[int]) -> None:
        """Validate expression command parameters."""
        valid_expressions = ["happy", "sad", "surprised", "neutral", "angry"]
        if expression not in valid_expressions:
            raise QubiValidationError(f"Invalid expression: {expression}")
        
        if intensity is not None and (not isinstance(intensity, int) or intensity < 0 or intensity > 100):
            raise QubiValidationError("Expression intensity must be an integer between 0 and 100")


class MobileCommandBuilder(BaseCommandBuilder):
    """Builder for mobile module commands."""
    
    def __init__(self, module_id: str):
        super().__init__(module_id, "mobile")
    
    def move(self, velocity: float, direction: float, 
             duration: Optional[float] = None) -> QubiCommand:
        """Create a movement command."""
        self._validate_movement_params(velocity, direction, duration)
        
        params: Dict[str, Union[float]] = {
            "velocity": velocity,
            "direction": direction,
        }
        
        if duration is not None:
            params["duration"] = duration
        
        return self._create_command("move", params)
    
    def set_location(self, x: float, y: float, 
                    heading: Optional[float] = None) -> QubiCommand:
        """Create a location setting command."""
        self._validate_location_params(x, y, heading)
        
        params: Dict[str, float] = {"x": x, "y": y}
        if heading is not None:
            params["heading"] = heading
        
        return self._create_command("set_location", params)
    
    def get_location(self) -> QubiCommand:
        """Create a location query command."""
        return self._create_command("get_location", {})
    
    def stop(self) -> QubiCommand:
        """Create a stop command."""
        return self._create_command("stop", {})
    
    def rotate(self, angle: float, speed: Optional[float] = None) -> QubiCommand:
        """Create a rotation command."""
        if not isinstance(angle, (int, float)) or not (-float('inf') < angle < float('inf')):
            raise QubiValidationError("Rotation angle must be a finite number")
        
        params: Dict[str, Union[float]] = {"angle": angle}
        if speed is not None:
            if not isinstance(speed, (int, float)) or speed < 0 or speed > 100:
                raise QubiValidationError("Rotation speed must be a number between 0 and 100")
            params["speed"] = speed
        
        return self._create_command("rotate", params)
    
    def _validate_movement_params(self, velocity: float, direction: float, 
                                 duration: Optional[float]) -> None:
        """Validate movement command parameters."""
        if not isinstance(velocity, (int, float)) or not (-float('inf') < velocity < float('inf')):
            raise QubiValidationError("Velocity must be a finite number")
        
        if not isinstance(direction, (int, float)) or not (-float('inf') < direction < float('inf')):
            raise QubiValidationError("Direction must be a finite number")
        
        if duration is not None and (not isinstance(duration, (int, float)) or duration <= 0):
            raise QubiValidationError("Duration must be a positive number")
    
    def _validate_location_params(self, x: float, y: float, 
                                 heading: Optional[float]) -> None:
        """Validate location command parameters."""
        if not isinstance(x, (int, float)) or not (-float('inf') < x < float('inf')):
            raise QubiValidationError("Location x coordinate must be a finite number")
        
        if not isinstance(y, (int, float)) or not (-float('inf') < y < float('inf')):
            raise QubiValidationError("Location y coordinate must be a finite number")
        
        if heading is not None and (not isinstance(heading, (int, float)) or not (-float('inf') < heading < float('inf'))):
            raise QubiValidationError("Heading must be a finite number")


class SensorCommandBuilder(BaseCommandBuilder):
    """Builder for sensor module commands."""
    
    def __init__(self, module_id: str):
        super().__init__(module_id, "sensor")
    
    def read(self, sensor_type: Optional[str] = None) -> QubiCommand:
        """Create a sensor reading command."""
        params = {}
        if sensor_type is not None:
            params["sensor_type"] = sensor_type
        
        return self._create_command("read", params)
    
    def start_streaming(self, sensor_type: str, interval: float) -> QubiCommand:
        """Create a sensor streaming start command."""
        if not isinstance(sensor_type, str) or not sensor_type:
            raise QubiValidationError("Sensor type must be a non-empty string")
        
        if not isinstance(interval, (int, float)) or interval <= 0:
            raise QubiValidationError("Streaming interval must be a positive number")
        
        params = {"sensor_type": sensor_type, "interval": interval}
        return self._create_command("start_streaming", params)
    
    def stop_streaming(self, sensor_type: Optional[str] = None) -> QubiCommand:
        """Create a sensor streaming stop command."""
        params = {}
        if sensor_type is not None:
            params["sensor_type"] = sensor_type
        
        return self._create_command("stop_streaming", params)
    
    def calibrate(self, sensor_type: str) -> QubiCommand:
        """Create a sensor calibration command."""
        if not isinstance(sensor_type, str) or not sensor_type:
            raise QubiValidationError("Sensor type must be a non-empty string")
        
        params = {"sensor_type": sensor_type}
        return self._create_command("calibrate", params)
    
    def get_status(self) -> QubiCommand:
        """Create a sensor status query command."""
        return self._create_command("get_status", {})


class CustomCommandBuilder(BaseCommandBuilder):
    """Builder for custom module commands."""
    
    def __init__(self, module_id: str):
        super().__init__(module_id, "custom")
    
    def command(self, action: str, params: Optional[Dict[str, Any]] = None) -> QubiCommand:
        """Create a custom command."""
        if not isinstance(action, str) or not action:
            raise QubiValidationError("Action must be a non-empty string")
        
        return self._create_command(action, params or {})


class CommandBuilder:
    """Main command builder factory."""
    
    def actuator(self, module_id: str) -> ActuatorCommandBuilder:
        """Create an actuator command builder."""
        return ActuatorCommandBuilder(module_id)
    
    def display(self, module_id: str) -> DisplayCommandBuilder:
        """Create a display command builder."""
        return DisplayCommandBuilder(module_id)
    
    def mobile(self, module_id: str) -> MobileCommandBuilder:
        """Create a mobile command builder."""
        return MobileCommandBuilder(module_id)
    
    def sensor(self, module_id: str) -> SensorCommandBuilder:
        """Create a sensor command builder."""
        return SensorCommandBuilder(module_id)
    
    def custom(self, module_id: str) -> CustomCommandBuilder:
        """Create a custom command builder."""
        return CustomCommandBuilder(module_id)


def create_command_builder() -> CommandBuilder:
    """Create a new command builder instance."""
    return CommandBuilder()