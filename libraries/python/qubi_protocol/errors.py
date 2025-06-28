"""Exception classes for the Qubi protocol."""


class QubiError(Exception):
    """Base exception for all Qubi protocol errors."""
    
    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.code = code


class QubiTimeoutError(QubiError):
    """Raised when an operation times out."""
    
    def __init__(self, message: str = "Operation timed out"):
        super().__init__(message, "TIMEOUT")


class QubiConnectionError(QubiError):
    """Raised when a connection fails."""
    
    def __init__(self, message: str = "Connection failed"):
        super().__init__(message, "CONNECTION_ERROR")


class QubiProtocolError(QubiError):
    """Raised when there's a protocol-level error."""
    
    def __init__(self, message: str = "Protocol error"):
        super().__init__(message, "PROTOCOL_ERROR")


class QubiValidationError(QubiError):
    """Raised when validation fails."""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, "VALIDATION_ERROR")