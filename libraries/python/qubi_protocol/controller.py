"""Qubi protocol controller for sending commands and managing connections."""

import asyncio
import socket
import json
import time
from typing import List, Dict, Optional, Callable, Any, Tuple
from threading import Lock

from .types import (
    QubiCommand,
    QubiMessage,
    QubiResponse,
    QubiModule,
    QubiControllerOptions,
    DiscoveryOptions,
    QUBI_DEFAULT_PORT,
)
from .utils import (
    create_message,
    serialize_message,
    deserialize_message,
    is_valid_ip_address,
    is_valid_port,
    generate_sequence_number,
)
from .errors import (
    QubiError,
    QubiTimeoutError,
    QubiConnectionError,
    QubiValidationError,
)


class QubiController:
    """Controller for sending commands to Qubi modules."""
    
    def __init__(
        self,
        host: str,
        port: int = QUBI_DEFAULT_PORT,
        options: Optional[QubiControllerOptions] = None,
    ):
        """Initialize the controller.
        
        Args:
            host: IP address of the target module
            port: UDP port number
            options: Controller configuration options
        """
        if not is_valid_ip_address(host):
            raise QubiValidationError(f"Invalid IP address: {host}")
        
        if not is_valid_port(port):
            raise QubiValidationError(f"Invalid port: {port}")
        
        self.host = host
        self.port = port
        self.options = options or {}
        
        # Set default options
        self.timeout = self.options.get("timeout", 5.0)
        self.retries = self.options.get("retries", 3)
        self.sequence_tracking = self.options.get("sequence_tracking", True)
        
        # Internal state
        self._socket: Optional[socket.socket] = None
        self._sequence_counter = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}
        self._lock = Lock()
        
        # Event handlers
        self._response_handlers: List[Callable[[QubiResponse, Tuple[str, int]], None]] = []
        self._error_handlers: List[Callable[[Exception], None]] = []
        
        self._setup_socket()
    
    def _setup_socket(self) -> None:
        """Set up the UDP socket."""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.settimeout(self.timeout)
        except OSError as e:
            raise QubiConnectionError(f"Failed to create socket: {e}")
    
    def _get_next_sequence(self) -> int:
        """Get the next sequence number."""
        with self._lock:
            if self.sequence_tracking:
                self._sequence_counter = (self._sequence_counter + 1) % 2147483647
                return self._sequence_counter
            return generate_sequence_number()
    
    def send_command(self, command: QubiCommand) -> QubiResponse:
        """Send a single command and wait for response.
        
        Args:
            command: The command to send
            
        Returns:
            The response from the module
            
        Raises:
            QubiError: If the command fails
        """
        responses = self.send_batch([command])
        return responses[0]
    
    def send_batch(self, commands: List[QubiCommand]) -> List[QubiResponse]:
        """Send multiple commands in a single message.
        
        Args:
            commands: List of commands to send
            
        Returns:
            List of responses from modules
            
        Raises:
            QubiError: If any command fails
        """
        if not self._socket:
            raise QubiConnectionError("Controller not initialized")
        
        sequence = self._get_next_sequence() if self.sequence_tracking else None
        message = create_message(commands, sequence)
        
        return self._send_with_retry(message)
    
    def _send_with_retry(self, message: QubiMessage) -> List[QubiResponse]:
        """Send a message with retry logic."""
        last_error: Optional[Exception] = None
        
        for attempt in range(self.retries + 1):
            try:
                return self._send_message(message)
            except Exception as e:
                last_error = e
                
                if attempt < self.retries:
                    time.sleep(2 ** attempt * 0.1)  # Exponential backoff
        
        if last_error:
            raise last_error
        
        raise QubiError("All retry attempts failed")
    
    def _send_message(self, message: QubiMessage) -> List[QubiResponse]:
        """Send a single message and wait for response."""
        if not self._socket:
            raise QubiConnectionError("Socket not available")
        
        data = serialize_message(message)
        
        try:
            # Send the message
            self._socket.sendto(data.encode('utf-8'), (self.host, self.port))
            
            # Wait for response if sequence tracking is enabled
            if self.sequence_tracking and message.get("sequence") is not None:
                return self._wait_for_response(message["sequence"])
            else:
                # For non-sequence tracking, return empty list
                return []
                
        except socket.timeout:
            raise QubiTimeoutError(f"Request timed out after {self.timeout}s")
        except OSError as e:
            raise QubiConnectionError(f"Failed to send message: {e}")
    
    def _wait_for_response(self, sequence: int) -> List[QubiResponse]:
        """Wait for a response with the given sequence number."""
        if not self._socket:
            raise QubiConnectionError("Socket not available")
        
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            try:
                data, addr = self._socket.recvfrom(4096)
                response = json.loads(data.decode('utf-8'))
                
                # Call response handlers
                for handler in self._response_handlers:
                    try:
                        handler(response, addr)
                    except Exception as e:
                        self._call_error_handlers(e)
                
                # Check if this is our response
                if (response.get("data", {}).get("sequence") == sequence or
                    not self.sequence_tracking):
                    
                    if response.get("status", 500) >= 400:
                        raise QubiError(response.get("message", "Unknown error"),
                                      str(response.get("status")))
                    
                    return [response]
                    
            except socket.timeout:
                continue
            except json.JSONDecodeError:
                continue
            except Exception as e:
                self._call_error_handlers(e)
        
        raise QubiTimeoutError(f"No response received within {self.timeout}s")
    
    def discover(self, options: Optional[DiscoveryOptions] = None) -> List[QubiModule]:
        """Discover available Qubi modules on the network.
        
        Args:
            options: Discovery configuration options
            
        Returns:
            List of discovered modules
        """
        opts = options or {}
        timeout = opts.get("timeout", 3.0)
        broadcast_address = opts.get("broadcast_address", "255.255.255.255")
        retries = opts.get("retries", 2)
        
        discovered_modules: List[QubiModule] = []
        seen_modules = set()
        
        # Create discovery command
        discovery_command: QubiCommand = {
            "module_id": "*",
            "module_type": "custom",
            "action": "discover",
            "params": {},
        }
        
        # Create broadcast socket
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.settimeout(timeout / retries)
        
        try:
            message = create_message([discovery_command])
            data = serialize_message(message)
            
            for attempt in range(retries):
                # Send discovery broadcast
                broadcast_socket.sendto(
                    data.encode('utf-8'),
                    (broadcast_address, QUBI_DEFAULT_PORT)
                )
                
                # Listen for responses
                end_time = time.time() + (timeout / retries)
                while time.time() < end_time:
                    try:
                        response_data, addr = broadcast_socket.recvfrom(4096)
                        response = json.loads(response_data.decode('utf-8'))
                        
                        module_key = f"{response.get('module_id')}:{addr[0]}:{addr[1]}"
                        
                        if (module_key not in seen_modules and
                            response.get("data", {}).get("module_type")):
                            
                            seen_modules.add(module_key)
                            discovered_modules.append({
                                "id": response["module_id"],
                                "type": response["data"]["module_type"],
                                "ip": addr[0],
                                "port": addr[1],
                                "last_seen": time.time(),
                            })
                            
                    except socket.timeout:
                        break
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            return discovered_modules
            
        finally:
            broadcast_socket.close()
    
    def add_response_handler(
        self,
        handler: Callable[[QubiResponse, Tuple[str, int]], None]
    ) -> None:
        """Add a handler for incoming responses."""
        self._response_handlers.append(handler)
    
    def remove_response_handler(
        self,
        handler: Callable[[QubiResponse, Tuple[str, int]], None]
    ) -> None:
        """Remove a response handler."""
        if handler in self._response_handlers:
            self._response_handlers.remove(handler)
    
    def add_error_handler(self, handler: Callable[[Exception], None]) -> None:
        """Add a handler for errors."""
        self._error_handlers.append(handler)
    
    def remove_error_handler(self, handler: Callable[[Exception], None]) -> None:
        """Remove an error handler."""
        if handler in self._error_handlers:
            self._error_handlers.remove(handler)
    
    def _call_error_handlers(self, error: Exception) -> None:
        """Call all registered error handlers."""
        for handler in self._error_handlers:
            try:
                handler(error)
            except Exception:
                pass  # Ignore errors in error handlers
    
    def get_host(self) -> str:
        """Get the target host."""
        return self.host
    
    def get_port(self) -> int:
        """Get the target port."""
        return self.port
    
    def is_connected(self) -> bool:
        """Check if the controller is connected."""
        return self._socket is not None
    
    def close(self) -> None:
        """Close the controller and cleanup resources."""
        if self._socket:
            self._socket.close()
            self._socket = None
        
        # Clear pending requests
        with self._lock:
            for future in self._pending_requests.values():
                if not future.done():
                    future.set_exception(QubiError("Controller closed"))
            self._pending_requests.clear()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()