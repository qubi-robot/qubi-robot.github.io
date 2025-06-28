import * as dgram from 'dgram';
import { EventEmitter } from 'events';
import {
  QubiCommand,
  QubiMessage,
  QubiResponse,
  QubiModule,
  QubiControllerOptions,
  DiscoveryOptions,
  QUBI_DEFAULT_PORT,
} from './types';
import {
  createMessage,
  serializeMessage,
  deserializeMessage,
  isValidIPAddress,
  isValidPort,
  generateSequenceNumber,
  waitFor,
} from './utils';
import {
  QubiError,
  QubiTimeoutError,
  QubiConnectionError,
  QubiValidationError,
} from './errors';

export class QubiController extends EventEmitter {
  private socket: dgram.Socket | null = null;
  private readonly host: string;
  private readonly port: number;
  private readonly options: Required<QubiControllerOptions>;
  private sequenceCounter = 0;
  private readonly pendingRequests = new Map<number, {
    resolve: (response: QubiResponse) => void;
    reject: (error: Error) => void;
    timeout: NodeJS.Timeout;
  }>();

  constructor(host: string, port: number = QUBI_DEFAULT_PORT, options: QubiControllerOptions = {}) {
    super();

    if (!isValidIPAddress(host)) {
      throw new QubiValidationError(`Invalid IP address: ${host}`);
    }

    if (!isValidPort(port)) {
      throw new QubiValidationError(`Invalid port: ${port}`);
    }

    this.host = host;
    this.port = port;
    this.options = {
      timeout: options.timeout ?? 5000,
      retries: options.retries ?? 3,
      sequenceTracking: options.sequenceTracking ?? true,
    };

    this.setupSocket();
  }

  private setupSocket(): void {
    this.socket = dgram.createSocket('udp4');
    
    this.socket.on('message', (msg, rinfo) => {
      try {
        const response = JSON.parse(msg.toString()) as QubiResponse;
        this.handleResponse(response);
        this.emit('response', response, rinfo);
      } catch (error) {
        this.emit('error', new QubiError(`Failed to parse response: ${error}`));
      }
    });

    this.socket.on('error', (error) => {
      this.emit('error', new QubiConnectionError(`Socket error: ${error.message}`));
    });
  }

  private handleResponse(response: QubiResponse): void {
    if (this.options.sequenceTracking && response.data?.sequence) {
      const sequence = response.data.sequence as number;
      const pending = this.pendingRequests.get(sequence);
      
      if (pending) {
        clearTimeout(pending.timeout);
        this.pendingRequests.delete(sequence);
        
        if (response.status >= 200 && response.status < 300) {
          pending.resolve(response);
        } else {
          pending.reject(new QubiError(response.message, response.status.toString()));
        }
      }
    }
  }

  async sendCommand(command: QubiCommand): Promise<QubiResponse> {
    return this.sendBatch([command]).then(responses => responses[0]!);
  }

  async sendBatch(commands: QubiCommand[]): Promise<QubiResponse[]> {
    if (!this.socket) {
      throw new QubiConnectionError('Controller not initialized');
    }

    const sequence = this.options.sequenceTracking ? this.getNextSequence() : undefined;
    const message = createMessage(commands, sequence);
    
    return this.sendWithRetry(message);
  }

  private async sendWithRetry(message: QubiMessage): Promise<QubiResponse[]> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.options.retries; attempt++) {
      try {
        return await this.sendMessage(message);
      } catch (error) {
        lastError = error as Error;
        
        if (attempt < this.options.retries) {
          await waitFor(Math.pow(2, attempt) * 100); // Exponential backoff
        }
      }
    }

    throw lastError;
  }

  private sendMessage(message: QubiMessage): Promise<QubiResponse[]> {
    return new Promise((resolve, reject) => {
      if (!this.socket) {
        reject(new QubiConnectionError('Socket not available'));
        return;
      }

      const data = serializeMessage(message);
      
      // Set up timeout and tracking for sequence-based requests
      if (this.options.sequenceTracking && message.sequence !== undefined) {
        const timeout = setTimeout(() => {
          this.pendingRequests.delete(message.sequence!);
          reject(new QubiTimeoutError(`Request timed out after ${this.options.timeout}ms`));
        }, this.options.timeout);

        this.pendingRequests.set(message.sequence, {
          resolve: (response) => resolve([response]),
          reject,
          timeout,
        });
      }

      this.socket.send(data, this.port, this.host, (error) => {
        if (error) {
          if (message.sequence !== undefined) {
            const pending = this.pendingRequests.get(message.sequence);
            if (pending) {
              clearTimeout(pending.timeout);
              this.pendingRequests.delete(message.sequence);
            }
          }
          reject(new QubiConnectionError(`Failed to send message: ${error.message}`));
        } else if (!this.options.sequenceTracking) {
          // For non-sequence tracking, resolve immediately
          resolve([]);
        }
      });
    });
  }

  async discover(options: DiscoveryOptions = {}): Promise<QubiModule[]> {
    const {
      timeout = 3000,
      broadcastAddress = '255.255.255.255',
      retries = 2,
    } = options;

    const discoveredModules: QubiModule[] = [];
    const seenModules = new Set<string>();

    // Create discovery message
    const discoveryCommand: QubiCommand = {
      module_id: '*',
      module_type: 'custom',
      action: 'discover',
      params: {},
    };

    // Set up temporary listener for discovery responses
    const responseHandler = (response: QubiResponse, rinfo: dgram.RemoteInfo) => {
      const moduleKey = `${response.module_id}:${rinfo.address}:${rinfo.port}`;
      
      if (!seenModules.has(moduleKey) && response.data?.module_type) {
        seenModules.add(moduleKey);
        discoveredModules.push({
          id: response.module_id,
          type: response.data.module_type,
          ip: rinfo.address,
          port: rinfo.port,
          lastSeen: Date.now(),
        });
      }
    };

    this.on('response', responseHandler);

    try {
      // Send discovery broadcast
      const message = createMessage([discoveryCommand]);
      const data = serializeMessage(message);
      
      for (let attempt = 0; attempt < retries; attempt++) {
        await new Promise<void>((resolve, reject) => {
          if (!this.socket) {
            reject(new QubiConnectionError('Socket not available'));
            return;
          }

          this.socket.send(data, QUBI_DEFAULT_PORT, broadcastAddress, (error) => {
            if (error) {
              reject(new QubiConnectionError(`Discovery broadcast failed: ${error.message}`));
            } else {
              resolve();
            }
          });
        });

        await waitFor(timeout / retries);
      }

      return discoveredModules;
    } finally {
      this.off('response', responseHandler);
    }
  }

  private getNextSequence(): number {
    if (this.options.sequenceTracking) {
      this.sequenceCounter = (this.sequenceCounter + 1) % 2147483647;
      return this.sequenceCounter;
    }
    return generateSequenceNumber();
  }

  getHost(): string {
    return this.host;
  }

  getPort(): number {
    return this.port;
  }

  isConnected(): boolean {
    return this.socket !== null;
  }

  close(): void {
    if (this.socket) {
      // Clear all pending requests
      this.pendingRequests.forEach(({ timeout, reject }) => {
        clearTimeout(timeout);
        reject(new QubiError('Controller closed'));
      });
      this.pendingRequests.clear();

      this.socket.close();
      this.socket = null;
      this.emit('close');
    }
  }
}