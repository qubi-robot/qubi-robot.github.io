export const QUBI_PROTOCOL_VERSION = '1.0';
export const QUBI_DEFAULT_PORT = 8888;
export const QUBI_MAX_PACKET_SIZE = 1024;

export type ModuleType = 'actuator' | 'display' | 'mobile' | 'sensor' | 'custom';

export interface QubiCommand {
  module_id: string;
  module_type: ModuleType;
  action: string;
  params: Record<string, any>;
}

export interface QubiMessage {
  version: string;
  timestamp: number;
  sequence?: number;
  commands: QubiCommand[];
}

export interface QubiResponse {
  status: number;
  message: string;
  module_id: string;
  timestamp: number;
  data?: Record<string, any>;
}

export interface QubiModule {
  id: string;
  type: ModuleType;
  ip: string;
  port: number;
  lastSeen: number;
}

// Actuator module types
export interface ServoParams {
  angle: number;
  speed?: number;
  easing?: 'linear' | 'ease-in' | 'ease-out';
}

export interface PositionParams {
  x: number;
  y: number;
  z: number;
}

// Display module types
export interface EyePosition {
  x: number;
  y: number;
}

export interface EyesParams {
  left_eye: EyePosition;
  right_eye: EyePosition;
  blink?: boolean;
}

export type Expression = 'happy' | 'sad' | 'surprised' | 'neutral' | 'angry';

export interface ExpressionParams {
  expression: Expression;
  intensity?: number;
}

// Mobile module types
export interface MovementParams {
  velocity: number;
  direction: number;
  duration?: number;
}

export interface LocationParams {
  x: number;
  y: number;
  heading?: number;
}

// Sensor module types
export interface SensorReading {
  sensor_type: string;
  value: number;
  unit?: string;
  timestamp: number;
}

export interface SensorData {
  sensor_type: string;
  data: Record<string, any>;
  timestamp: number;
}

// Discovery types
export interface DiscoveryOptions {
  timeout?: number;
  broadcastAddress?: string;
  retries?: number;
}

// Controller options
export interface QubiControllerOptions {
  timeout?: number;
  retries?: number;
  sequenceTracking?: boolean;
}