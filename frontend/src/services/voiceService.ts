/**
 * Voice Service for handling WebSocket communication with the backend
 */

import { logger } from './loggingService';

export interface VoiceConfig {
  systemPrompt: string;
  voice: string;
  allowInterruptions: boolean;
  mode: 'study' | 'wellness';
  vad_enabled?: boolean; // Add VAD control flag
}

export interface VoiceMessage {
  type: 'config' | 'audio' | 'text' | 'status' | 'error';
  data?: string;
  text?: string;
  status?: 'config_received' | 'connected' | 'listening' | 'thinking' | 'speaking' | 'idle' | 'disconnected';
  config?: VoiceConfig;
  sampleRate?: number;
  mimeType?: string;
}

export class VoiceService {
  private ws: WebSocket | null = null;
  private clientId: string;
  private onMessage: (message: VoiceMessage) => void;
  private onStatusChange: (status: string) => void;
  private onError: (error: string) => void;

  constructor(
    onMessage: (message: VoiceMessage) => void,
    onStatusChange: (status: string) => void,
    onError: (error: string) => void
  ) {
    this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
    this.onError = onError;
  }

  async connect(config: VoiceConfig): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          logger.info('WebSocket connected successfully', { clientId: this.clientId }, 'VoiceService');
          // Send configuration
          this.send({
            type: 'config',
            config: config
          });
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: VoiceMessage = JSON.parse(event.data);
            logger.debug('WebSocket message received', { type: message.type, status: message.status }, 'VoiceService');
            this.onMessage(message);
            
            if (message.type === 'status') {
              this.onStatusChange(message.status || 'idle');
            }
          } catch (error) {
            logger.error('Error parsing WebSocket message', { error, rawData: event.data }, 'VoiceService');
            this.onError('Failed to parse server message');
          }
        };

        this.ws.onclose = (event) => {
          logger.info('WebSocket closed', { code: event.code, reason: event.reason }, 'VoiceService');
          this.onStatusChange('disconnected');
        };

        this.ws.onerror = (error) => {
          logger.error('WebSocket error', { 
            error, 
            readyState: this.ws?.readyState, 
            url: wsUrl 
          }, 'VoiceService');
          this.onError('Connection error');
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  send(message: VoiceMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      logger.debug('Sending WebSocket message', { type: message.type }, 'VoiceService');
      this.ws.send(JSON.stringify(message));
    } else {
      logger.warn('WebSocket not connected, cannot send message', { messageType: message.type }, 'VoiceService');
    }
  }

  sendAudio(audioData: string, sampleRate: number = 16000): void {
    logger.debug('Sending audio data', { 
      dataLength: audioData.length, 
      sampleRate 
    }, 'VoiceService');
    this.send({
      type: 'audio',
      data: audioData,
      sampleRate: sampleRate
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}