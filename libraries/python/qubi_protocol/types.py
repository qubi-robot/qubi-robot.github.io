"""Type definitions for the Qubi protocol."""

from typing import Dict, List, Optional, Literal, Union, TypedDict
from typing_extensions import NotRequired
import time

QUBI_PROTOCOL_VERSION = "1.0"
QUBI_DEFAULT_PORT = 8888
QUBI_MAX_PACKET_SIZE = 1024

ModuleType = Literal["actuator", "display", "mobile", "sensor", "custom"]
Expression = Literal["happy", "sad", "surprised", "neutral", "angry"]


class QubiCommand(TypedDict):
    """A command to be sent to a Qubi module."""
    module_id: str
    module_type: ModuleType
    action: str
    params: Dict[str, Union[str, int, float, bool, Dict, List]]


class QubiMessage(TypedDict):
    """A complete message containing one or more commands."""
    version: str
    timestamp: int
    sequence: NotRequired[int]
    commands: List[QubiCommand]


class QubiResponse(TypedDict):
    """Response from a Qubi module."""
    status: int
    message: str
    module_id: str
    timestamp: int
    data: NotRequired[Dict[str, Union[str, int, float, bool, Dict, List]]]


class QubiModule(TypedDict):
    """Information about a discovered Qubi module."""
    id: str
    type: ModuleType
    ip: str
    port: int
    last_seen: float


# Actuator module parameter types
class ServoParams(TypedDict):
    """Parameters for servo control commands."""
    angle: int
    speed: NotRequired[int]
    easing: NotRequired[Literal["linear", "ease-in", "ease-out"]]


class PositionParams(TypedDict):
    """Parameters for 3D position commands."""
    x: float
    y: float
    z: float


# Display module parameter types
class EyePosition(TypedDict):
    """Position of a single eye."""
    x: int
    y: int


class EyesParams(TypedDict):
    """Parameters for eye position commands."""
    left_eye: EyePosition
    right_eye: EyePosition
    blink: NotRequired[bool]


class ExpressionParams(TypedDict):
    """Parameters for facial expression commands."""
    expression: Expression
    intensity: NotRequired[int]


# Mobile module parameter types
class MovementParams(TypedDict):
    """Parameters for movement commands."""
    velocity: float
    direction: float
    duration: NotRequired[float]


class LocationParams(TypedDict):
    """Parameters for location commands."""
    x: float
    y: float
    heading: NotRequired[float]


# Sensor module types
class SensorReading(TypedDict):
    """A single sensor reading."""
    sensor_type: str
    value: float
    unit: NotRequired[str]
    timestamp: float


class SensorData(TypedDict):
    """Complex sensor data with arbitrary fields."""
    sensor_type: str
    data: Dict[str, Union[str, int, float, bool, Dict, List]]
    timestamp: float


# Discovery and controller options
class DiscoveryOptions(TypedDict, total=False):
    """Options for module discovery."""
    timeout: float
    broadcast_address: str
    retries: int


class QubiControllerOptions(TypedDict, total=False):
    """Options for the Qubi controller."""
    timeout: float
    retries: int
    sequence_tracking: bool


def get_current_timestamp() -> int:
    """Get current timestamp in milliseconds."""
    return int(time.time() * 1000)