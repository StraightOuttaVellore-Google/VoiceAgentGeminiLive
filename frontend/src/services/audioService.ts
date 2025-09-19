/**
 * Audio Service for handling microphone capture and audio playback
 * Direct PCM audio capture without WebM encoding to avoid decode issues
 */

import { logger } from './loggingService';

export interface AudioServiceCallbacks {
  onAudioData: (audioData: string, sampleRate: number) => void;
  onError: (error: string) => void;
  onVADStatus?: (isSpeech: boolean, confidence: number) => void;
}

export class AudioService {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphone: MediaStreamAudioSourceNode | null = null;
  private isRecording = false;
  private callbacks: AudioServiceCallbacks;
  private stream: MediaStream | null = null;
  private recordingInterval: NodeJS.Timeout | null = null;
  private audioBuffer: Float32Array[] = [];
  private bufferSize = 0;
  private originalSampleRate = 44100;

  // Audio queue properties (like standalone)
  private audioQueue: AudioBuffer[] = [];
  private isPlaying = false;
  private activeSource: AudioBufferSourceNode | null = null;

  // Audio settings - matching standalone implementation exactly
  private readonly TARGET_SAMPLE_RATE = 16000; // Input sample rate (like standalone)
  private readonly CHANNELS = 1;
  private readonly CHUNK_SIZE = 1024; // FFT size for analyser
  private readonly AUDIO_CHUNK_SIZE = 512; // Audio chunk size (like standalone)
  private readonly CHUNK_DURATION_MS = 32; // 512 samples at 16kHz = 32ms

  constructor(callbacks: AudioServiceCallbacks) {
    this.callbacks = callbacks;
  }

  async initialize(): Promise<void> {
    try {
      // First, create AudioContext with a standard sample rate
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this.originalSampleRate = this.audioContext.sampleRate;
      
      // Resume audio context if suspended (required for some browsers)
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      logger.info(`AudioContext created with sample rate: ${this.originalSampleRate}Hz`, {}, 'AudioService');

      // Request microphone access with constraints that match our AudioContext
      const audioConstraints: MediaTrackConstraints = {
        channelCount: this.CHANNELS,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: this.originalSampleRate
      };

      // Try to get a stream with the AudioContext's sample rate
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({
          audio: audioConstraints
        });
        logger.info('Successfully obtained stream with matching sample rate', {}, 'AudioService');
      } catch (error) {
        logger.warn('Failed to get stream with matching sample rate, trying without constraints', { error }, 'AudioService');
        // Fallback: try without sample rate constraint
        this.stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            channelCount: this.CHANNELS,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        });
      }

      // Get the actual sample rate from the stream
      const audioTracks = this.stream.getAudioTracks();
      let streamSampleRate = this.originalSampleRate;
      if (audioTracks.length > 0) {
        const settings = audioTracks[0].getSettings();
        streamSampleRate = settings.sampleRate || this.originalSampleRate;
        logger.debug('MediaStream audio settings', { settings }, 'AudioService');
      }

      // If sample rates don't match, we need to handle this properly
      if (streamSampleRate !== this.originalSampleRate) {
        logger.info(`Sample rate mismatch detected: Stream=${streamSampleRate}Hz, AudioContext=${this.originalSampleRate}Hz`, {}, 'AudioService');
        
        // Close the current AudioContext
        this.audioContext.close();
        
        // Create a new AudioContext with the stream's sample rate
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
          sampleRate: streamSampleRate
        });
        this.originalSampleRate = streamSampleRate;
        
        // Resume the new context
        if (this.audioContext.state === 'suspended') {
          await this.audioContext.resume();
        }
        
        logger.info(`Created new AudioContext with sample rate: ${this.originalSampleRate}Hz`, {}, 'AudioService');
      }

      // Wait a bit to ensure the audio context is fully initialized
      await new Promise(resolve => setTimeout(resolve, 100));

      // Create analyser node for audio processing
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      this.analyser.smoothingTimeConstant = 0.8;

      // Create microphone source - this should now work since sample rates match
      this.microphone = this.audioContext.createMediaStreamSource(this.stream);
      this.microphone.connect(this.analyser);

      logger.info('Audio initialized successfully', {
        streamSampleRate,
        audioContextSampleRate: this.audioContext.sampleRate,
        originalSampleRate: this.originalSampleRate,
        targetSampleRate: this.TARGET_SAMPLE_RATE
      }, 'AudioService');

    } catch (error) {
      logger.error('Error initializing audio', { error }, 'AudioService');
      this.callbacks.onError('Microphone access denied or not available');
      throw error;
    }
  }

  startRecording(): void {
    if (!this.analyser || this.isRecording) return;

    this.isRecording = true;
    
    // Start continuous audio capture - match standalone timing
    this.recordingInterval = setInterval(() => {
      this.captureAudioChunk();
    }, this.CHUNK_DURATION_MS); // Capture every 32ms like standalone
  }

  stopRecording(): void {
    if (!this.isRecording) return;

    this.isRecording = false;
    
    if (this.recordingInterval) {
      clearInterval(this.recordingInterval);
      this.recordingInterval = null;
    }
  }

  private captureAudioChunk(): void {
    if (!this.analyser || !this.audioContext) return;

    try {
      // Get audio data directly as PCM
      const bufferLength = this.analyser.frequencyBinCount;
      const dataArray = new Float32Array(bufferLength);
      this.analyser.getFloatTimeDomainData(dataArray);
      
      // Add to buffer
      this.audioBuffer.push(new Float32Array(dataArray));
      this.bufferSize += dataArray.length;
      
      // Process audio when we have enough samples for a complete chunk
      const requiredSamples = Math.floor((this.originalSampleRate * this.CHUNK_DURATION_MS) / 1000);
      
      if (this.bufferSize >= requiredSamples) {
        // Process audio in chunks (like standalone)
        this.processAudioBuffer();
      }
    } catch (error) {
      console.error('Error capturing audio chunk:', error);
      this.callbacks.onError('Failed to capture audio data');
    }
  }

  private resampleAudio(audioData: Float32Array, fromRate: number, toRate: number): Float32Array {
    if (fromRate === toRate) {
      return audioData;
    }
    
    const ratio = toRate / fromRate;
    const newLength = Math.floor(audioData.length * ratio);
    const resampled = new Float32Array(newLength);
    
    // Simple linear interpolation resampling
    for (let i = 0; i < newLength; i++) {
      const sourceIndex = i / ratio;
      const index = Math.floor(sourceIndex);
      const fraction = sourceIndex - index;
      
      if (index + 1 < audioData.length) {
        resampled[i] = audioData[index] * (1 - fraction) + audioData[index + 1] * fraction;
      } else {
        resampled[i] = audioData[index] || 0;
      }
    }
    
    return resampled;
  }

  private simpleVAD(audioData: Float32Array): { isSpeech: boolean; confidence: number } {
    // Simple VAD based on energy and zero-crossing rate
    const rms = Math.sqrt(audioData.reduce((sum, val) => sum + val * val, 0) / audioData.length);
    
    // Calculate zero-crossing rate
    let zeroCrossings = 0;
    for (let i = 1; i < audioData.length; i++) {
      if ((audioData[i] >= 0) !== (audioData[i - 1] >= 0)) {
        zeroCrossings++;
      }
    }
    const zcr = zeroCrossings / audioData.length;
    
    // Simple heuristic: speech has moderate energy and moderate zero-crossing rate - make it less aggressive
    const energyThreshold = 0.002; // Lower threshold for better speech detection
    const zcrMin = 0.05; // Lower minimum ZCR
    const zcrMax = 0.4; // Higher maximum ZCR
    
    const hasEnergy = rms > energyThreshold;
    const hasSpeechZCR = zcr > zcrMin && zcr < zcrMax;
    
    const isSpeech = hasEnergy && hasSpeechZCR;
    const confidence = Math.min(1, rms * 100); // Simple confidence based on energy
    
    return { isSpeech, confidence };
  }

  private processAudioBuffer(): void {
    if (!this.audioContext) return;

    // Combine all buffered audio
    const combinedBuffer = new Float32Array(this.bufferSize);
    let offset = 0;
    for (const chunk of this.audioBuffer) {
      combinedBuffer.set(chunk, offset);
      offset += chunk.length;
    }
    
    // Resample to 16kHz input rate (like standalone)
    const inputBuffer = this.resampleAudio(combinedBuffer, this.originalSampleRate, this.TARGET_SAMPLE_RATE);
    
    // Check if we have enough samples for a complete chunk
    if (inputBuffer.length < this.AUDIO_CHUNK_SIZE) {
      // Not enough samples, keep buffering
      return;
    }
    
    // Process in 512-sample chunks (like standalone)
    const numChunks = Math.floor(inputBuffer.length / this.AUDIO_CHUNK_SIZE);
    
    for (let i = 0; i < numChunks; i++) {
      const startIdx = i * this.AUDIO_CHUNK_SIZE;
      const endIdx = startIdx + this.AUDIO_CHUNK_SIZE;
      const chunk = inputBuffer.slice(startIdx, endIdx);
      
      // Simple VAD for frontend feedback
      const vadResult = this.simpleVAD(chunk);
      if (this.callbacks.onVADStatus) {
        this.callbacks.onVADStatus(vadResult.isSpeech, vadResult.confidence);
      }
      
      // Debug logging for audio chunks
      logger.debug(`Audio chunk processed: ${chunk.length} samples, VAD: ${vadResult.isSpeech}, confidence: ${vadResult.confidence.toFixed(3)}`, {}, 'AudioService');
      
      // Convert to 16-bit PCM (like standalone)
      const pcmData = new Int16Array(chunk.length);
      for (let j = 0; j < chunk.length; j++) {
        pcmData[j] = Math.max(-32768, Math.min(32767, chunk[j] * 32768));
      }
      
      // Convert to base64
      const base64Data = this.arrayBufferToBase64(pcmData.buffer);
      
      // Send each chunk immediately (like standalone) with 16kHz input rate
      logger.debug(`Sending audio chunk: ${base64Data.length} chars, sample rate: ${this.TARGET_SAMPLE_RATE}`, {}, 'AudioService');
      this.callbacks.onAudioData(base64Data, this.TARGET_SAMPLE_RATE);
    }
    
    // Keep remaining samples in buffer for next iteration
    const remainingSamples = inputBuffer.length % this.AUDIO_CHUNK_SIZE;
    if (remainingSamples > 0) {
      // Convert back to original sample rate for buffering
      const remainingAtOriginalRate = this.resampleAudio(
        inputBuffer.slice(-remainingSamples), 
        this.TARGET_SAMPLE_RATE, 
        this.originalSampleRate
      );
      this.audioBuffer = [remainingAtOriginalRate];
      this.bufferSize = remainingAtOriginalRate.length;
    } else {
      this.audioBuffer = [];
      this.bufferSize = 0;
    }
  }

  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  // Stop playback and clear the queue (like standalone)
  public stopPlayback(): void {
    logger.info('Stopping playback and clearing audio queue', {}, 'AudioService');
    if (this.activeSource) {
      this.activeSource.stop();
      this.activeSource = null;
    }
    this.audioQueue = []; // Clear the queue
    this.isPlaying = false;
  }

  // Queue audio for playback (like standalone)
  public async playAudio(audioData: string, mimeType: string): Promise<void> {
    logger.debug('Queueing audio data for playback', { length: audioData.length, mimeType }, 'AudioService');
    try {
      if (!this.audioContext) {
        // Initialize if it's somehow not ready
        await this.initialize();
        if (!this.audioContext) {
          logger.error('AudioContext could not be initialized', {}, 'AudioService');
          return;
        }
      }
      
      // Resume audio context if suspended (important for user interaction)
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      const binaryString = atob(audioData);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Create the AudioBuffer from the raw data
      const audioBuffer = await this.createAudioBuffer(bytes.buffer, mimeType);
      
      // Add the processed buffer to our queue
      this.audioQueue.push(audioBuffer);
      
      // If the player isn't already running, start it.
      if (!this.isPlaying) {
        this.processAudioQueue();
      }
    } catch (error) {
      logger.error('Error processing or queueing audio', { error, mimeType }, 'AudioService');
      this.callbacks.onError('Failed to process audio for playback');
    }
  }

  // Process audio queue sequentially (like standalone)
  private async processAudioQueue(): Promise<void> {
    if (this.isPlaying || this.audioQueue.length === 0) {
      return;
    }

    this.isPlaying = true;
    logger.info('Starting audio queue processing', { queueSize: this.audioQueue.length }, 'AudioService');

    while (this.audioQueue.length > 0) {
      const audioBuffer = this.audioQueue.shift(); // Get the next buffer from the front of the queue
      if (audioBuffer) {
        try {
          await this.playBuffer(audioBuffer);
        } catch (error) {
          logger.error('Error playing buffer from queue', { error }, 'AudioService');
          // If one buffer fails, stop processing to avoid a cascade of errors
          this.stopPlayback(); 
          break;
        }
      }
    }
    
    logger.info('Audio queue processing finished', {}, 'AudioService');
    this.isPlaying = false;
  }

  // Play a single audio buffer (like standalone)
  private playBuffer(buffer: AudioBuffer): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.audioContext) {
        reject(new Error("AudioContext is not available"));
        return;
      }
      this.activeSource = this.audioContext.createBufferSource();
      this.activeSource.buffer = buffer;
      this.activeSource.connect(this.audioContext.destination);
      
      this.activeSource.onended = () => {
        this.activeSource = null;
        resolve();
      };
      
      this.activeSource.start();
    });
  }

  // Helper function to create AudioBuffer
  private createAudioBuffer(data: ArrayBuffer, mimeType: string): Promise<AudioBuffer> {
    if (!this.audioContext) {
      return Promise.reject(new Error("AudioContext not initialized"));
    }
    
    // For raw PCM data, we need to build the buffer manually
    if (mimeType.startsWith('audio/pcm')) {
      const rateMatch = mimeType.match(/rate=(\d+)/);
      const sampleRate = rateMatch ? parseInt(rateMatch[1], 10) : 24000;
      const pcmSamples = data.byteLength / 2; // 16-bit PCM
      
      const audioBuffer = this.audioContext.createBuffer(1, pcmSamples, sampleRate);
      const channelData = audioBuffer.getChannelData(0);
      
      const view = new DataView(data);
      for (let i = 0; i < pcmSamples; i++) {
        const sample = view.getInt16(i * 2, true); // true for little-endian
        channelData[i] = sample / 32768.0;
      }
      return Promise.resolve(audioBuffer);
    } else {
      // For encoded formats like Opus, let the browser do the work
      return this.audioContext.decodeAudioData(data);
    }
  }

  cleanup(): void {
    this.stopRecording();
    this.stopPlayback(); // Stop any ongoing playback and clear queue
    
    // Clear audio buffer
    this.audioBuffer = [];
    this.bufferSize = 0;
    
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    
    if (this.microphone) {
      this.microphone.disconnect();
      this.microphone = null;
    }
    
    if (this.analyser) {
      this.analyser.disconnect();
      this.analyser = null;
    }
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.isRecording = false;
  }

  isRecordingActive(): boolean {
    return this.isRecording;
  }
}
