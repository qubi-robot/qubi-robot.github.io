import {
  QubiCommand,
  ModuleType,
  ServoParams,
  PositionParams,
  EyesParams,
  ExpressionParams,
  MovementParams,
  LocationParams,
  Expression,
} from './types';
import { QubiValidationError } from './errors';

export class CommandBuilder {
  actuator(moduleId: string): ActuatorCommandBuilder {
    return new ActuatorCommandBuilder(moduleId);
  }

  display(moduleId: string): DisplayCommandBuilder {
    return new DisplayCommandBuilder(moduleId);
  }

  mobile(moduleId: string): MobileCommandBuilder {
    return new MobileCommandBuilder(moduleId);
  }

  sensor(moduleId: string): SensorCommandBuilder {
    return new SensorCommandBuilder(moduleId);
  }

  custom(moduleId: string): CustomCommandBuilder {
    return new CustomCommandBuilder(moduleId);
  }
}

abstract class BaseCommandBuilder {
  constructor(
    protected readonly moduleId: string,
    protected readonly moduleType: ModuleType
  ) {}

  protected createCommand(action: string, params: Record<string, any>): QubiCommand {
    return {
      module_id: this.moduleId,
      module_type: this.moduleType,
      action,
      params,
    };
  }
}

export class ActuatorCommandBuilder extends BaseCommandBuilder {
  constructor(moduleId: string) {
    super(moduleId, 'actuator');
  }

  setServo(params: ServoParams): QubiCommand {
    this.validateServoParams(params);
    return this.createCommand('set_servo', params);
  }

  setPosition(params: PositionParams): QubiCommand {
    this.validatePositionParams(params);
    return this.createCommand('set_position', params);
  }

  getPosition(): QubiCommand {
    return this.createCommand('get_position', {});
  }

  stop(): QubiCommand {
    return this.createCommand('stop', {});
  }

  private validateServoParams(params: ServoParams): void {
    if (params.angle < 0 || params.angle > 180) {
      throw new QubiValidationError('Servo angle must be between 0 and 180 degrees');
    }

    if (params.speed !== undefined && (params.speed < 0 || params.speed > 255)) {
      throw new QubiValidationError('Servo speed must be between 0 and 255');
    }

    if (params.easing !== undefined) {
      const validEasing = ['linear', 'ease-in', 'ease-out'];
      if (!validEasing.includes(params.easing)) {
        throw new QubiValidationError(`Invalid easing type: ${params.easing}`);
      }
    }
  }

  private validatePositionParams(params: PositionParams): void {
    if (!Number.isFinite(params.x) || !Number.isFinite(params.y) || !Number.isFinite(params.z)) {
      throw new QubiValidationError('Position coordinates must be finite numbers');
    }
  }
}

export class DisplayCommandBuilder extends BaseCommandBuilder {
  constructor(moduleId: string) {
    super(moduleId, 'display');
  }

  setEyes(params: EyesParams): QubiCommand {
    this.validateEyesParams(params);
    return this.createCommand('set_eyes', params);
  }

  setExpression(params: ExpressionParams): QubiCommand {
    this.validateExpressionParams(params);
    return this.createCommand('set_expression', params);
  }

  clearDisplay(): QubiCommand {
    return this.createCommand('clear_display', {});
  }

  setBrightness(brightness: number): QubiCommand {
    if (brightness < 0 || brightness > 100) {
      throw new QubiValidationError('Brightness must be between 0 and 100');
    }
    return this.createCommand('set_brightness', { brightness });
  }

  private validateEyesParams(params: EyesParams): void {
    this.validateEyePosition(params.left_eye, 'left_eye');
    this.validateEyePosition(params.right_eye, 'right_eye');
  }

  private validateEyePosition(eye: { x: number; y: number }, eyeName: string): void {
    if (!Number.isInteger(eye.x) || !Number.isInteger(eye.y)) {
      throw new QubiValidationError(`${eyeName} coordinates must be integers`);
    }
    if (eye.x < 0 || eye.y < 0) {
      throw new QubiValidationError(`${eyeName} coordinates must be non-negative`);
    }
  }

  private validateExpressionParams(params: ExpressionParams): void {
    const validExpressions: Expression[] = ['happy', 'sad', 'surprised', 'neutral', 'angry'];
    if (!validExpressions.includes(params.expression)) {
      throw new QubiValidationError(`Invalid expression: ${params.expression}`);
    }

    if (params.intensity !== undefined && (params.intensity < 0 || params.intensity > 100)) {
      throw new QubiValidationError('Expression intensity must be between 0 and 100');
    }
  }
}

export class MobileCommandBuilder extends BaseCommandBuilder {
  constructor(moduleId: string) {
    super(moduleId, 'mobile');
  }

  move(params: MovementParams): QubiCommand {
    this.validateMovementParams(params);
    return this.createCommand('move', params);
  }

  setLocation(params: LocationParams): QubiCommand {
    this.validateLocationParams(params);
    return this.createCommand('set_location', params);
  }

  getLocation(): QubiCommand {
    return this.createCommand('get_location', {});
  }

  stop(): QubiCommand {
    return this.createCommand('stop', {});
  }

  rotate(angle: number, speed?: number): QubiCommand {
    if (!Number.isFinite(angle)) {
      throw new QubiValidationError('Rotation angle must be a finite number');
    }
    
    const params: Record<string, any> = { angle };
    if (speed !== undefined) {
      if (speed < 0 || speed > 100) {
        throw new QubiValidationError('Rotation speed must be between 0 and 100');
      }
      params.speed = speed;
    }
    
    return this.createCommand('rotate', params);
  }

  private validateMovementParams(params: MovementParams): void {
    if (!Number.isFinite(params.velocity)) {
      throw new QubiValidationError('Velocity must be a finite number');
    }

    if (!Number.isFinite(params.direction)) {
      throw new QubiValidationError('Direction must be a finite number');
    }

    if (params.duration !== undefined && (params.duration <= 0)) {
      throw new QubiValidationError('Duration must be positive');
    }
  }

  private validateLocationParams(params: LocationParams): void {
    if (!Number.isFinite(params.x) || !Number.isFinite(params.y)) {
      throw new QubiValidationError('Location coordinates must be finite numbers');
    }

    if (params.heading !== undefined && !Number.isFinite(params.heading)) {
      throw new QubiValidationError('Heading must be a finite number');
    }
  }
}

export class SensorCommandBuilder extends BaseCommandBuilder {
  constructor(moduleId: string) {
    super(moduleId, 'sensor');
  }

  read(sensorType?: string): QubiCommand {
    const params = sensorType ? { sensor_type: sensorType } : {};
    return this.createCommand('read', params);
  }

  startStreaming(sensorType: string, interval: number): QubiCommand {
    if (interval <= 0) {
      throw new QubiValidationError('Streaming interval must be positive');
    }
    
    return this.createCommand('start_streaming', {
      sensor_type: sensorType,
      interval,
    });
  }

  stopStreaming(sensorType?: string): QubiCommand {
    const params = sensorType ? { sensor_type: sensorType } : {};
    return this.createCommand('stop_streaming', params);
  }

  calibrate(sensorType: string): QubiCommand {
    return this.createCommand('calibrate', { sensor_type: sensorType });
  }

  getStatus(): QubiCommand {
    return this.createCommand('get_status', {});
  }
}

export class CustomCommandBuilder extends BaseCommandBuilder {
  constructor(moduleId: string) {
    super(moduleId, 'custom');
  }

  command(action: string, params: Record<string, any> = {}): QubiCommand {
    if (!action || typeof action !== 'string') {
      throw new QubiValidationError('Action must be a non-empty string');
    }
    
    return this.createCommand(action, params);
  }
}

// Convenience function to create a new command builder
export function createCommandBuilder(): CommandBuilder {
  return new CommandBuilder();
}