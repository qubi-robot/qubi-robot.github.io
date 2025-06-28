import { QubiMessage, QubiCommand, QUBI_PROTOCOL_VERSION, QUBI_MAX_PACKET_SIZE } from './types';
import { QubiValidationError, QubiProtocolError } from './errors';

export function createMessage(commands: QubiCommand[], sequence?: number): QubiMessage {
  return {
    version: QUBI_PROTOCOL_VERSION,
    timestamp: Date.now(),
    sequence,
    commands,
  };
}

export function serializeMessage(message: QubiMessage): string {
  const serialized = JSON.stringify(message);
  
  if (serialized.length > QUBI_MAX_PACKET_SIZE) {
    throw new QubiValidationError(
      `Message size ${serialized.length} exceeds maximum ${QUBI_MAX_PACKET_SIZE} bytes`
    );
  }
  
  return serialized;
}

export function deserializeMessage(data: string): QubiMessage {
  try {
    const message = JSON.parse(data) as QubiMessage;
    validateMessage(message);
    return message;
  } catch (error) {
    if (error instanceof QubiValidationError) {
      throw error;
    }
    throw new QubiProtocolError(`Failed to parse message: ${error}`);
  }
}

export function validateMessage(message: QubiMessage): void {
  if (!message.version) {
    throw new QubiValidationError('Message missing version field');
  }
  
  if (message.version !== QUBI_PROTOCOL_VERSION) {
    throw new QubiValidationError(
      `Unsupported protocol version: ${message.version}, expected: ${QUBI_PROTOCOL_VERSION}`
    );
  }
  
  if (!message.timestamp || typeof message.timestamp !== 'number') {
    throw new QubiValidationError('Message missing or invalid timestamp field');
  }
  
  if (!Array.isArray(message.commands)) {
    throw new QubiValidationError('Message missing or invalid commands array');
  }
  
  for (const command of message.commands) {
    validateCommand(command);
  }
}

export function validateCommand(command: QubiCommand): void {
  if (!command.module_id || typeof command.module_id !== 'string') {
    throw new QubiValidationError('Command missing or invalid module_id');
  }
  
  if (!command.module_type || typeof command.module_type !== 'string') {
    throw new QubiValidationError('Command missing or invalid module_type');
  }
  
  const validTypes = ['actuator', 'display', 'mobile', 'sensor', 'custom'];
  if (!validTypes.includes(command.module_type)) {
    throw new QubiValidationError(`Invalid module_type: ${command.module_type}`);
  }
  
  if (!command.action || typeof command.action !== 'string') {
    throw new QubiValidationError('Command missing or invalid action');
  }
  
  if (!command.params || typeof command.params !== 'object') {
    throw new QubiValidationError('Command missing or invalid params');
  }
}

export function isValidIPAddress(ip: string): boolean {
  const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
  if (!ipv4Regex.test(ip)) {
    return false;
  }
  
  const parts = ip.split('.');
  return parts.every(part => {
    const num = parseInt(part, 10);
    return num >= 0 && num <= 255;
  });
}

export function isValidPort(port: number): boolean {
  return Number.isInteger(port) && port >= 1 && port <= 65535;
}

export function generateSequenceNumber(): number {
  return Math.floor(Math.random() * 2147483647); // Max 32-bit signed integer
}

export function waitFor(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}