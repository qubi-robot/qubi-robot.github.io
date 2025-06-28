"""Utility functions for the Qubi protocol."""

import json
import re
import random
from typing import List

from .types import (
    QubiMessage,
    QubiCommand,
    QUBI_PROTOCOL_VERSION,
    QUBI_MAX_PACKET_SIZE,
    get_current_timestamp,
)
from .errors import QubiValidationError, QubiProtocolError


def create_message(commands: List[QubiCommand], sequence: int = None) -> QubiMessage:
    """Create a new Qubi message with the given commands."""
    message: QubiMessage = {
        "version": QUBI_PROTOCOL_VERSION,
        "timestamp": get_current_timestamp(),
        "commands": commands,
    }
    
    if sequence is not None:
        message["sequence"] = sequence
    
    return message


def serialize_message(message: QubiMessage) -> str:
    """Serialize a message to JSON string."""
    try:
        serialized = json.dumps(message, separators=(',', ':'))
        
        if len(serialized) > QUBI_MAX_PACKET_SIZE:
            raise QubiValidationError(
                f"Message size {len(serialized)} exceeds maximum {QUBI_MAX_PACKET_SIZE} bytes"
            )
        
        return serialized
    except (TypeError, ValueError) as e:
        raise QubiProtocolError(f"Failed to serialize message: {e}")


def deserialize_message(data: str) -> QubiMessage:
    """Deserialize a JSON string to a QubiMessage."""
    try:
        message = json.loads(data)
        validate_message(message)
        return message
    except json.JSONDecodeError as e:
        raise QubiProtocolError(f"Failed to parse JSON: {e}")
    except QubiValidationError:
        raise
    except Exception as e:
        raise QubiProtocolError(f"Failed to deserialize message: {e}")


def validate_message(message: dict) -> None:
    """Validate that a message conforms to the Qubi protocol."""
    if not isinstance(message, dict):
        raise QubiValidationError("Message must be a dictionary")
    
    # Check required fields
    if "version" not in message:
        raise QubiValidationError("Message missing version field")
    
    if message["version"] != QUBI_PROTOCOL_VERSION:
        raise QubiValidationError(
            f"Unsupported protocol version: {message['version']}, "
            f"expected: {QUBI_PROTOCOL_VERSION}"
        )
    
    if "timestamp" not in message:
        raise QubiValidationError("Message missing timestamp field")
    
    if not isinstance(message["timestamp"], int):
        raise QubiValidationError("Message timestamp must be an integer")
    
    if "commands" not in message:
        raise QubiValidationError("Message missing commands field")
    
    if not isinstance(message["commands"], list):
        raise QubiValidationError("Message commands must be a list")
    
    # Validate each command
    for i, command in enumerate(message["commands"]):
        try:
            validate_command(command)
        except QubiValidationError as e:
            raise QubiValidationError(f"Command {i}: {e}")


def validate_command(command: dict) -> None:
    """Validate that a command conforms to the Qubi protocol."""
    if not isinstance(command, dict):
        raise QubiValidationError("Command must be a dictionary")
    
    # Check required fields
    required_fields = ["module_id", "module_type", "action", "params"]
    for field in required_fields:
        if field not in command:
            raise QubiValidationError(f"Command missing {field} field")
    
    # Validate module_id
    if not isinstance(command["module_id"], str) or not command["module_id"]:
        raise QubiValidationError("Command module_id must be a non-empty string")
    
    # Validate module_type
    valid_types = ["actuator", "display", "mobile", "sensor", "custom"]
    if command["module_type"] not in valid_types:
        raise QubiValidationError(f"Invalid module_type: {command['module_type']}")
    
    # Validate action
    if not isinstance(command["action"], str) or not command["action"]:
        raise QubiValidationError("Command action must be a non-empty string")
    
    # Validate params
    if not isinstance(command["params"], dict):
        raise QubiValidationError("Command params must be a dictionary")


def is_valid_ip_address(ip: str) -> bool:
    """Check if a string is a valid IPv4 address."""
    if not isinstance(ip, str):
        return False
    
    ipv4_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if not ipv4_pattern.match(ip):
        return False
    
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)


def is_valid_port(port: int) -> bool:
    """Check if a number is a valid network port."""
    return isinstance(port, int) and 1 <= port <= 65535


def generate_sequence_number() -> int:
    """Generate a random sequence number."""
    return random.randint(1, 2147483647)  # Max 32-bit signed integer


def format_module_info(module: dict) -> str:
    """Format module information for display."""
    return (
        f"Module(id='{module['id']}', type='{module['type']}', "
        f"ip='{module['ip']}', port={module['port']})"
    )


def calculate_message_size(message: QubiMessage) -> int:
    """Calculate the serialized size of a message in bytes."""
    return len(serialize_message(message))