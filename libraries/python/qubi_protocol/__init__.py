"""
Qubi Protocol - Python library for modular social robot communication.

This library provides a UDP-based JSON communication protocol for modular social robots.
It supports actuator, display, mobile, and sensor modules with type-safe command handling.
"""

from .types import (
    ModuleType,
    QubiCommand,
    QubiMessage,
    QubiResponse,
    QubiModule,
    ServoParams,
    PositionParams,
    EyesParams,
    ExpressionParams,
    MovementParams,
    LocationParams,
    SensorReading,
    SensorData,
    Expression,
    QUBI_PROTOCOL_VERSION,
    QUBI_DEFAULT_PORT,
    QUBI_MAX_PACKET_SIZE,
)

from .controller import QubiController, DiscoveryOptions, QubiControllerOptions

from .builders import (
    CommandBuilder,
    ActuatorCommandBuilder,
    DisplayCommandBuilder,
    MobileCommandBuilder,
    SensorCommandBuilder,
    CustomCommandBuilder,
    create_command_builder,
)

from .errors import (
    QubiError,
    QubiTimeoutError,
    QubiConnectionError,
    QubiProtocolError,
    QubiValidationError,
)

from .utils import (
    create_message,
    serialize_message,
    deserialize_message,
    validate_message,
    validate_command,
    is_valid_ip_address,
    is_valid_port,
    generate_sequence_number,
)

__version__ = "1.0.0"
__author__ = "Qubi Project"
__email__ = "qubi@example.com"

__all__ = [
    # Types
    "ModuleType",
    "QubiCommand",
    "QubiMessage", 
    "QubiResponse",
    "QubiModule",
    "ServoParams",
    "PositionParams",
    "EyesParams",
    "ExpressionParams", 
    "MovementParams",
    "LocationParams",
    "SensorReading",
    "SensorData",
    "Expression",
    "QUBI_PROTOCOL_VERSION",
    "QUBI_DEFAULT_PORT",
    "QUBI_MAX_PACKET_SIZE",
    # Controller
    "QubiController",
    "DiscoveryOptions",
    "QubiControllerOptions",
    # Builders
    "CommandBuilder",
    "ActuatorCommandBuilder",
    "DisplayCommandBuilder",
    "MobileCommandBuilder", 
    "SensorCommandBuilder",
    "CustomCommandBuilder",
    "create_command_builder",
    # Errors
    "QubiError",
    "QubiTimeoutError",
    "QubiConnectionError",
    "QubiProtocolError",
    "QubiValidationError",
    # Utils
    "create_message",
    "serialize_message",
    "deserialize_message",
    "validate_message",
    "validate_command",
    "is_valid_ip_address",
    "is_valid_port", 
    "generate_sequence_number",
]