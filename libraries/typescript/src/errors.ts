export class QubiError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'QubiError';
  }
}

export class QubiTimeoutError extends QubiError {
  constructor(message: string = 'Operation timed out') {
    super(message, 'TIMEOUT');
    this.name = 'QubiTimeoutError';
  }
}

export class QubiConnectionError extends QubiError {
  constructor(message: string = 'Connection failed') {
    super(message, 'CONNECTION_ERROR');
    this.name = 'QubiConnectionError';
  }
}

export class QubiProtocolError extends QubiError {
  constructor(message: string = 'Protocol error') {
    super(message, 'PROTOCOL_ERROR');
    this.name = 'QubiProtocolError';
  }
}

export class QubiValidationError extends QubiError {
  constructor(message: string = 'Validation failed') {
    super(message, 'VALIDATION_ERROR');
    this.name = 'QubiValidationError';
  }
}